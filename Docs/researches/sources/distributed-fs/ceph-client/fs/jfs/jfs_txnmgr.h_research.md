# sources/distributed-fs/ceph-client/fs/jfs/jfs_txnmgr.h

## Purpose
`jfs_txnmgr.h` defines the shared transaction-manager data structures, flags, lock overlays, commit descriptor, global tables, and exported transaction APIs. It is the contract between mutating JFS code, transaction commit, log manager, and metadata page handling.

## Important APIs, types, and functions
Important types are `struct tblock`, `struct tlock`, `struct lv`, `struct linelock`, `struct xtlock`, `struct maplock`, `struct xdlistlock`, and `struct commit`. Macros `tid_to_tblock()` and `lid_to_tlock()` index global `TxBlock` and `TxLock`. Flags include commit flags (`COMMIT_SYNC`, `COMMIT_FORCE`, `COMMIT_PMAP`, `COMMIT_WMAP`, `COMMIT_PWMAP`, `COMMIT_DELETE`, `COMMIT_TRUNCATE`, `COMMIT_CREATE`, `COMMIT_LAZY`, `COMMIT_PAGE`, `COMMIT_INODE`), tlock state/type/operation flags, and maplock allocation/free flags. Exported APIs include transaction begin/end/commit/abort, tlock/maplock allocation, line-lock extension, map free, EA logging, freelock cleanup, quiesce/resume, lazy commit, and sync thread entry points.

## Control flow
The header itself is declarative. Callers begin a transaction with `txBegin()`, obtain tlocks through `txLock()`/`txMaplock()`, add line vectors through `txLinelock()`, commit with `txCommit()`, and finish with `txEnd()`. The log manager uses the common leading fields of `struct tblock` as a log-sync block and group-commit state carrier.

## State and persistence behavior
`struct tblock` tracks transaction identity, lock list, log transaction id, commit queue linkage, commit LSN/page/eor, group-commit wait queue, and inode create/delete payload. `struct tlock` binds a transaction to a metapage or inode and stores a 48-byte overlay used as a line lock, xtree lock, or map lock. Maplock and xdlistlock overlays describe persistent and working map allocation/free operations that are applied only after the journal commit is durable.

## Dependencies and integration points
The header includes `jfs_logmgr.h`, so transaction records share log descriptor types and group commit flags. It depends on metapage, inode, extent, and JFS-specific lock users to interpret overlays correctly. The fixed sizes and comments about alignment matter for both 32-bit and 64-bit builds.

## Risks
The overlay design is compact but fragile: `struct linelock`, `struct xtlock`, `struct maplock`, and `struct xdlistlock` all occupy `tlock.lock`, so field growth or alignment changes can corrupt commit records. `tid_t` and `lid_t` are 16-bit, matching table limits and on-structure fields; increasing table sizes without changing the types would wrap. The common `logsyncblk` prefix in `tblock` must stay compatible with log manager list operations.

## Test signals
Build and runtime tests should stress every tlock type and operation flag: inode updates, xtree growth/truncation/free, dtree split/free, map-only EA/ACL changes, anonymous locks, lazy commits, and forced commits. Debug builds should watch lock overlay counts (`TLOCKSHORT`, `TLOCKLONG`) and assert that line-vector indexes never exceed their maximums.
