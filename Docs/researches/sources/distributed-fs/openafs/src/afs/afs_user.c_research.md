# sources/distributed-fs/openafs/src/afs/afs_user.c

## Purpose

`afs_user.c` manages Cache Manager `unixuser` records keyed by uid/PAG and cell. It owns the `afs_users[NUSERS]` hash table, reference counting, per-user locking, token garbage collection, access-cache invalidation, connection reset after token changes, PAG statistics, primary-user selection, and optional PAG garbage collection by walking the process table.

## Important APIs, Types, and Functions

Global state includes `afs_xuser` and `afs_users`. Core APIs are `afs_GCUserData`, `afs_FindUser`, `afs_GetUser`, `afs_LockUser`, `afs_PutUser`, `afs_ComputePAGStats`, `afs_SetPrimary`, `afs_NotifyUser`, and `afs_MarkUserExpired`. When `AFS_PAG_MANAGER` is not defined, the file also provides `afs_CheckTokenCache`, `afs_ResetAccessCache`, and `afs_ResetUserConns`. With `AFS_GCPAGS`, it adds `afs_GCPAGs_perproc_func` and `afs_GCPAGs`. Important state flags include `UHasTokens`, `UTokensBad`, `UNeedsReset`, `UPAGCounted`, `UPrimary`, and `TMP_UPAGNotReferenced`.

## Control Flow and State

`afs_GetUser` hashes by uid, keeps each bucket sorted by uid, reuses an existing record when uid and cell match, fills in a previously unknown cell when appropriate, or allocates a new zeroed `unixuser` with an initialized lock, `UNDEFVID`, `refCount = 1`, and current `tokenTime`. Remote/exported users propagate exporter references when creating additional cell-specific records. `afs_FindUser` is a lookup-only path that increments `refCount` and returns the user with the requested lock. `afs_PutUser` releases the requested lock and decrements `refCount`.

`afs_GCUserData` obtains locks in the documented order, scans all users, discards expired tokens, and deletes unreferenced records when no usable token remains or unauthenticated timeout has elapsed. Deletion releases user connections, frees tokens, releases exporter references, and frees the record. `afs_CheckTokenCache` marks users whose tokens have become unusable as `UTokensBad | UNeedsReset`, scans vcaches to remove matching access-cache entries, frees removed access entries, and clears reset flags. `afs_ResetUserConns` marks every connection vector for the user with `forceConnectFS` so future RPCs use new tokens, then resets access-cache entries for that uid/cell.

`afs_ComputePAGStats` walks user buckets to calculate current PAG count, record count, authenticated/unauthenticated record count, max records per PAG, longest chain, and high-water marks. It uses `UPAGCounted` as a temporary mark while grouping records with the same uid in a bucket. `afs_SetPrimary` ensures that only one record for a uid has `UPrimary`, while preserving an existing primary until it has unlogged. Optional `afs_GCPAGs` marks all user records as not referenced, asks OS-specific process traversal to clear live PAGs, disables PAG GC if traversal appears broken, and expires unreferenced non-exported records for later removal.

## Dependencies and Integration Points

This file depends on token management from `afs_tokens.c`, connection and server locks (`afs_xsrvAddr`, `afs_xconn`, `afs_ReleaseConnsUser`), vcache/access-cache structures (`afs_vhashT`, `struct axscache`, `afs_FindAxs`, `afs_RemoveAxs`, `afs_FreeAllAxs`), exporter reference hooks, OS credential/PAG helpers, and `afs_stats_cmfullperf.authent`. It is used by connection setup, pioctl token operations, request initialization, server checks, access checks, and background daemons.

## Persistence and Side Effects

User records and token jars are memory-resident but long-lived. Token changes and expiration directly affect authorization, Rx connection reuse, and cached access decisions. GC can free records and connections; access-cache resets remove per-vcache authorization results. Stats high-water marks persist for the process lifetime.

## Risks and Test Signals

Risks include refcount/lock mismatches, access-cache removal while using only read locks due to hierarchy constraints, token-expiration races, sorted-bucket insertion mistakes, and PAG GC expiring all tokens if process traversal fails. The code contains explicit safeguards for traversal failure, but platform credential walkers remain high risk. Test signals include token set/unlog/expiration flows, user lookup by uid/cell including `cell == -1`, connection refresh after token replacement, access-cache invalidation after bad tokens, PAG stats correctness with multiple cells per PAG, exporter user handling, and PAG GC behavior when process traversal returns zero processes or zero credentials.
