# sources/cloud-native/buildkit/solver/llbsolver/ops/file.go

Purpose: implements LLB file operations (`mkdir`, `mkfile`, `symlink`, `rm`, `copy`) as a graph of actions over BuildKit refs, including cache-key dependency selection and a reusable `FileOpSolver`.

Important APIs/types/functions: `fileOp`, `NewFileOp`, `CacheMap`, `Exec`, `FileOpSolver`, `Solve`, `validate`, `getInput`, `addSelector`, `dedupeSelectors`, `processOwner`, `isDefaultIndexes`, and `unlazyResultFunc`.

Control flow: `CacheMap` serializes each action, records action input/secondary/output indexes unless they match the historical default pattern, and computes selectors for copy sources and named user/group lookups. Selectors for inputs invalidated by mutation are skipped. `Exec` converts worker refs, builds a file backend, and delegates to `FileOpSolver`. `Solve` validates indexes, output continuity, duplicate outputs, and action dependency loops, then resolves each output in parallel. `getInput` uses flightcontrol to memoize action results, prepares primary and secondary mounts, loads user/group mounts, runs the backend action, and either commits to a ref or keeps a mount alive for downstream actions.

State/persistence: action outputs become immutable refs through `RefManager.Commit`. Intermediate mounts are released on error or after final resolution. The solver tracks `outs` and `ins` maps per instance, so instances are not reusable across independent solves.

Dependencies/integration: integrates `llbsolver/file` backend/ref manager, `fileoptypes`, worker refs, session groups, cache content hashing, errdefs wrapping, and platform-specific user readers.

Risks: file-action indexes are easy to misuse; loops and invalid indexes can otherwise recurse forever. Error wrapping commits partial mutable mounts for diagnostics, which has ownership and release risks. Cache selectors must include `/etc/passwd` and `/etc/group` for named chown but avoid hashing mutated inputs.

Test signals: `file_test.go` covers action chaining, chown mounts, copy source/destination semantics, invalid outputs/indexes/loops, multi-output, scratch roots, and parallel independent branches.
