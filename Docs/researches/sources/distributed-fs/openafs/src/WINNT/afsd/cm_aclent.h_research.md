# sources/distributed-fs/openafs/src/WINNT/afsd/cm_aclent.h

## Purpose
`cm_aclent.h` defines the ACL cache entry structure and declares the ACL cache API for the Windows cache manager. It is the shared contract between access checks, status population, token-change handling, and cache initialization.

## Important Types And APIs
`cm_aclent_t` contains an LRU queue node, magic value, per-scache linked-list pointer, back pointer to the scache, held user pointer, cached random access rights, and token/TGT expiration time. `CM_ACLENT_MAGIC` supports cache validation. The declared API covers initialization, lookup, allocation helper declaration, insertion/update, freeing all entries on an scache, invalidating one user, validation, shutdown, resetting entries for a cell/user, and retrieving token lifetime for a user/cell.

## State, Dependencies, And Integration
The header exposes `cm_aclLock`, which protects both global LRU state and ACL entry mutation. It depends on OpenAFS queue/lock types and cache-manager user/cell/scache types. `cm_access.c` uses lookup results to answer access-right checks; `cm_scache.c` adds entries from server status; token and ioctl paths reset ACL state when credentials change.

## Risks And Test Signals
The static `GetFreeACLEnt` prototype in a header mirrors an implementation-private helper and is unusual; it can trigger warnings or confusion if included broadly. Callers must honor implementation lock requirements even though only prototypes are visible here. Test signals are ABI-compatible struct layout for memory-mapped cache data, lock initialization, add/find/free/reset behavior, and validation catching bad magic or pointer corruption.
