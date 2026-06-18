# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fetcher.go

Purpose: defines the migration `Fetcher` interface, distribution constants, size-limited reader wrapper, and `MultiFetcher` failover/circuit-breaker logic.

Important APIs and control flow: `MultiFetcher.Fetch` returns a latched exhaustion error when set, tries never-failed fetchers before quarantined fetchers, clears quarantine and failure count on success, does not penalize context cancellation, and after every fetcher fails increments a full-loop counter. After `maxMultiFetcherFullLoopFailures`, it latches `ErrMultiFetcherExhausted`.

State and persistence: `MultiFetcher` keeps session-scoped failed fetcher indexes, loop failure count, and exhausted error protected by a mutex. No disk persistence.

Dependencies and integration: used by migration download code to combine multiple HTTP gateway fetchers. `GetDistPathEnv` reads `IPFS_DIST_PATH`.

Risks and test signals: `Fetchers()` exposes the slice directly, so callers could mutate it. Exhaustion is lifetime-scoped and requires constructing a new fetcher to retry after network recovery. Tests cover quarantine, reset, cap, concurrency, success reset, and cancellation behavior.
