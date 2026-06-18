# sources/distributed-fs/openafs/src/WINNT/afsd/cm_server.h

## Purpose
`cm_server.h` declares the Windows cache manager's server model: server objects, server-reference list nodes, server ranking constants, state flags, probe flags, global locks, and public server-management APIs.

## Important APIs and types
- `cm_server_vols_t` stores pages of volume IDs known to reside on a server.
- `cm_server_t` records global-list membership, socket address, type, connection list, flags, wait/ping counts, capabilities, cell pointer, refcount, ranks, volume list, down time, and UUID.
- `cm_serverRef_t` links volumes/cells to servers with per-reference status, refcount, and volume ID.
- `enum repstate` distinguishes not-busy, busy, offline, and deleted server refs.
- Constants define server types (`CM_SERVER_VLDB`, `CM_SERVER_FILE`), flags (`DOWN`, `PREF_SET`, `NO64BIT`, `NOINLINEBULK`, `UUID`), check masks, and IP rank buckets.
- Public functions cover creation/find, refs, ranking, probing, list operations, capability flags, interface updates, dumping, equality, and RPC stats clearing.

## Control flow and state behavior
The header's protection comments define lock ownership: global lists and server refs are protected by `cm_serverLock`; per-server address/type/flags/waits/capabilities/ranks/vols/down time/UUID are protected by `serverp->mx`; interface arrays are protected by `cm_syscfgLock`. Server-reference lists are sorted by active rank and can retain deleted nodes until refcounts drop.

## Dependencies and integration points
It includes Winsock and OSI lock types and forward-references cell/connection structures. It is consumed by volume, cell, connection, callback, and diagnostics modules that need server identity, ordering, and reachability information.

## Risks and edge cases
- `NUM_SERVER_VOLS` is derived from pointer size and should be treated as layout-sensitive.
- Several APIs accept `locked` flags; callers must pass the right value to avoid double-locking or unlocked mutation.
- Server objects can be pointed to by cells and volumes without holds, so global lock discipline is part of memory safety.

## Test signals
Tests should validate server-ref refcount behavior under locked/unlocked calls, list ordering by rank, deleted reference cleanup, IP rank constants, capability flag setters, and lock-protected interface array updates.
