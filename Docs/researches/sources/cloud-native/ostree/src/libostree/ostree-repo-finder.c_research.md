# sources/cloud-native/ostree/src/libostree/ostree-repo-finder.c

Purpose: defines the shared `OstreeRepoFinder` interface, the parallel multi-finder orchestration helpers, and the boxed `OstreeRepoFinderResult` type used by remote discovery and pull selection.

Important APIs/types/functions: `ostree_repo_finder_resolve_async/finish`, `ostree_repo_finder_resolve_all_async/finish`, `OstreeRepoFinderResult`, `ostree_repo_finder_result_new`, `dup`, `compare`, `free`, and `freev`. Internal validation helpers check collection refs, checksum maps, and result array ordering.

Control flow: single-finder resolution is a thin wrapper around `resolve_all` with a one-element finder array. `resolve_all_async` validates inputs, starts every finder implementation in parallel, collects successful result arrays, logs individual finder errors without failing the whole operation, waits for all pending finders using `ResolveAllData`, sorts results, and returns a single `GPtrArray`. Result construction refs the remote/finder and ref/checksum maps; comparison orders by priority, then summary last-modified when both nonzero, then count of non-NULL checksums, then remote name.

State and persistence: interface objects are external. This file manages only per-operation `GTask` state and boxed-result ownership. No repository state is changed here.

Dependencies/integration: finder implementations register `resolve_async`/`resolve_finish` vfuncs. `ostree-repo-pull.c` and public find-remotes APIs consume sorted result arrays and result metadata to choose pull sources.

Risks: `resolve_all` ignores individual finder failures and returns whatever other finders produced, which is resilient but can hide a broken discovery backend unless debug logs are inspected. `ostree_repo_finder_result_new` rejects empty ref maps, even though higher-level comments discuss zero-ref results. `compare` currently orders lower numeric priority first and has a FIXME about zero-ref results and “usefulness” semantics.

Test signals: `tests/test-repo-finder-config.c` exercises interface calls and `ostree_repo_find_remotes_async`. Additional tests should cover result ordering, validation failures, multi-finder partial failures, and boxed ownership.
