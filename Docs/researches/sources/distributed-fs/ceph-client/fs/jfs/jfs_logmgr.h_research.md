# sources/distributed-fs/ceph-client/fs/jfs/jfs_logmgr.h

## Purpose
`jfs_logmgr.h` defines the JFS journal ABI and the in-memory structures shared by the log manager, transaction manager, metapage layer, mount/unmount code, and replay code. It describes the on-disk log superblock, log pages, log record descriptor, line-vector descriptor, active log state, log buffers, log-sync list prefix, and the public log-manager API.

## Important APIs, types, and functions
Key constants are `LOGPSIZE`, `L2LOGPSIZE`, `LOGPAGES`, `LOGSUPER_B`, `LOGSTART_B`, `LOGMAGIC`, `LOGVERSION`, and `MAX_ACTIVE`. On-disk structures are `struct logsuper`, `struct logpage`, `struct lrd`, and `struct lvd`. In-memory structures are `struct jfs_log`, `struct lbuf`, and `struct logsyncblk`. The header exports `lmLogOpen()`, `lmLogClose()`, `lmLogShutdown()`, `lmLogInit()`, `lmLogFormat()`, `lmGroupCommit()`, `jfsIOWait()`, `jfs_flush_journal()`, and `jfs_syncpt()`.

## Control flow
The header does not execute code, but it encodes the contracts used by `jfs_logmgr.c` and `jfs_txnmgr.c`. Transaction code fills `struct lrd` with record type and type-specific fields, then calls `lmLog()`. Log manager code packs optional line-vector data before the fixed descriptor, updates `struct logpage` header/trailer `eor`, and records current and committed LSNs in `struct jfs_log` and `struct tblock`.

## State and persistence behavior
`struct logsuper` is stored in log block 1 and records magic/version, serial number, size, block size, state, end-of-log, journal UUID/label, and up to `MAX_ACTIVE` filesystem UUIDs sharing the journal. `struct logpage` stores duplicate page and eor values in header/trailer to detect partial writes. `struct lrd` is the replay descriptor for commit, sync point, mount, after-image, no-redo, and map-update records. `struct jfs_log` is volatile state and includes current append page/eor, sync-point cursors, group-commit queue, log buffer queue, shared-superblock list, and journaling-disabled flag.

## Dependencies and integration points
The header pulls in UUID support, `jfs_filsys.h` for filesystem state and flags, and `jfs_lock.h` for sleep/locking helpers. It relies on `pxd_t` from JFS types for physical extents and on `struct tblock`/`struct metapage` users treating the leading fields as a `struct logsyncblk`. The exported API is consumed by mount, unmount, transaction commit, metapage writeback, log formatting, and background I/O threads.

## Risks
The on-disk structures use little-endian fields and fixed field placement; layout changes would break replay and userspace repair tools. `struct logsyncblk` must remain a common prefix for both transaction blocks and metapages, so field reordering in either embedding structure is dangerous. The `logdiff()` macro assumes circular log arithmetic relative to `log->syncpt`; wrong inputs can miscompute sync pressure and allow log overwrite. Constants such as `LOGPHDRSIZE`, `LOGPTLRSIZE`, and `LOGRDSIZE` are baked into record packing.

## Test signals
Build-time layout checks are implicit, so recovery tests are the main signal: formatted logs should validate with `LOGMAGIC`, dirty logs should reject mount before replay, active filesystem lists should be updated on shared external journals, and replay should correctly interpret all `LOG_*` record and data-type flags. Endian-sensitive tests should inspect log descriptors and extent fields on disk.
