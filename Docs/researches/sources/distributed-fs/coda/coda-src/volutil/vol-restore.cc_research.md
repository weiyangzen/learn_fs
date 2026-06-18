# sources/distributed-fs/coda/coda-src/volutil/vol-restore.cc

## Purpose

`vol-restore.cc` implements server-side volume restore from a dump streamed by the volutil client over the `VOLDUMP_SUBSYSTEMID` side channel. The complete 792-line file was read. It creates a new restored volume, reconstructs large and small vnode lists in RVM, rebuilds file and directory data, and brings the restored volume online.

## Important APIs, Types, and Functions

The exported entry point is `S_VolRestore()`. Major helpers are `RestoreVolume()`, `FreeVnodeIndex()`, `ReadLargeVnodeIndex()`, `ReadSmallVnodeIndex()`, and `ReadVnodeDiskObject()`. It uses dump parsing helpers from `voldump.h`/`dump.h`, inode operations such as `icreate()` and `iopen()`, directory inode helpers `DI_Copy()`/`DI_VMFree()`, RVM list storage `rec_smolist`, and volume APIs `VCreateVolume()`, `VUpdateVolume()`, `VDetachVolume()`, and `HashDelete()`.

## Control Flow

`S_VolRestore` initializes volutil state, validates the partition and requested id, binds back to the client dump subsystem, allocates a dump buffer, and calls `RestoreVolume()`. `RestoreVolume()` reads and validates a full dump header, rejects incremental and illegal read-write/replicated volume types, creates or allocates a target id in a transaction, creates a provisional volume, reads large and small vnode indexes, validates end-of-dump, copies dumped disk data into the volume header, marks the volume blessed/in service, updates and detaches it. Vnode reads are batched by `VnodePollPeriod` so long restores periodically end transactions and yield.

## State and Persistence Behavior

Restore mutates RVM volume metadata, RVM vnode-list arrays, recoverable vnode objects, directory inodes, and underlying vice inodes for file data. Provisional vnode lists from `VCreateVolume()` are freed before restored lists are installed. On failure after volume creation, `S_VolRestore` calls `HashDelete(*volid)` but many partial disk/RVM side effects depend on transaction aborts and later salvage. Dump content is streamed from the client rather than read from a server-side path.

## Dependencies and Integration Points

Dependencies include `rvmlib`, `recov`, `camprivate`, `partition`, `viceinode`, `volhash`, `voldump`, `al`, `fssync`, `codadir`, RPC2 SMARTFTP, and dump-buffer code. The client side is `volclient.cc`'s `restorefromback()` plus `S_ReadDump()`.

## Risks and Test Signals

Risks include partial restore cleanup, multiple places that return without freeing newly allocated directory pages or closing handles on error, reliance on dump tag correctness, host-endian dump assumptions, and `CODA_ASSERT` for RVM allocation/list invariants. Tests should cover full restore, id allocation and `MaxVolId` update, duplicate id rejection, bad partition, incremental dump rejection, malformed vnode tags, directory ACL externalization, file-data transfer failure, and salvage of interrupted restores.
