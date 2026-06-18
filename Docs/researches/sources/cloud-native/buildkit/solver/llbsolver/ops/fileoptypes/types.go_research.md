# sources/cloud-native/buildkit/solver/llbsolver/ops/fileoptypes/types.go

Purpose: defines narrow interfaces that decouple `FileOpSolver` from concrete BuildKit cache refs, mounts, and filesystem backends.

Important APIs/types/functions: `Ref`, `Mount`, `Backend`, and `RefManager`. `Backend` exposes file action primitives with explicit destination, source, user, and group mounts. `RefManager` prepares refs as readonly or writable mounts and commits mounts back to refs.

Control flow: no implementation; interfaces define the call contract consumed by `ops/file.go` and implemented by real `llbsolver/file` package and fake tests.

State/persistence: interface-level only. Persistence semantics are delegated to implementations: `Commit` turns mutable mount state into a ref; `Release` decrements/releases refs or mounts.

Dependencies/integration: imports `context`, `session.Group`, and `pb` file action types. This file is the abstraction boundary between generic file-action graph logic and backend filesystem mutation.

Risks: the interfaces do not encode ownership transfer precisely, so callers and implementers must follow conventions around releasing mounts after commit/error. The minimal `Ref` interface only has `Release`, so type assertions are needed elsewhere when worker/cache-specific behavior is required.

Test signals: tested indirectly by `file_test.go` fake implementations and real backend tests outside this subset.
