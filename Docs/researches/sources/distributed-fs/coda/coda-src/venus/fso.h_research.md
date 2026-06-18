# sources/distributed-fs/coda/coda-src/venus/fso.h

## Purpose
This header specifies Venus' cached file-system object layer. It defines the recoverable FSDB cache database, individual `fsobj` records, cache state flags, status summaries, local/disconnected mutation APIs, object locking, and integration hooks for communication, volumes, hoarding, repair, and 9P.

## Important APIs, Types, and Functions
`fsdb` owns cache sizing, block/file accounting, hash table, freelist, priority queue, delete queue, open-for-write queue, cache statistics, and object allocation/reclamation. Public methods include `Find`, `Get`, `Put`, `Flush`, `TranslateFid`, callback break handling, user reset, priority reset, and stats/printing. `fsobj` stores Fids, component names, volume pointers, persistent Venus status, access rights, dirty/local/fetch flags, mount state, parent/child links, priority state, hoard/MLE bindings, data pointers, cache files, locks, and repair metadata. Its APIs span fetch/getattr/store/setattr, create/remove/link/rename/mkdir/rmdir/symlink, open/read/close/access/lookup/readdir/readlink/read-intent, directory package operations, disconnected/local mutation logging, repair operations, conflict handling, and cache reporting.

## Control Flow
Callers obtain objects through `FSDB->Get`/`Find`, operate through `fsobj` public CFS methods, and release with `Put`. Object methods coordinate cache validity, server reachability, dirty state, partial data, local mutation logs, and locks. Macros describe replacement, fetchability, garbage collection, and activity decisions used by implementations.

## State and Persistence Behavior
Many fields are recoverable through RVM-backed structures, while `/*T*/` marks transient runtime fields. FSDB persists cached object metadata, local/disconnected mutation state, cache allocation state, and dirty objects. File data lives in cache files or directory handles. The layer is central to Venus recovery and reintegration.

## Dependencies and Integration Points
It depends on Vice/RPC2 types, Coda directory utilities, LKA, hoard database, communication, realm DB, cache files, Venus recovery, vproc, volume classes, and `binding`. `9pfs.cc` is a friend so it can inspect cnodes through fsobjs.

## Risks and Test Signals
Risks include recoverable/transient field confusion, lock/refcount imbalance, dirty object loss, partial fetch holes, callback invalidation races, local/global conflict errors, and cache replacement of active objects. Tests should cover crash recovery, callback breaks, disconnected mutation/reintegration, mount points, partial file reads, cache pressure reclamation, repair operations, and 9P reads/writes through fsobjs.
