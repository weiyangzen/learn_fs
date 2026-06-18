<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/vsprocs.h -->
# sources/distributed-fs/openafs/src/libadmin/vos/vsprocs.h

## Purpose
Declares the libadmin VOS volume-operation API implemented in `vsprocs.c`, along with the broad OpenAFS, Rx, ubik, VLDB, volserver, and admin includes required by those signatures. It is the public internal header for code that wants to call the UV-style administrative procedures.

## Important APIs, Types, And Functions
The header exposes prototypes for volume lifecycle (`UV_CreateVolume`, `UV_DeleteVolume`, `UV_NukeVolume`, `UV_VolumeZap`), movement and replication (`UV_MoveVolume`, `UV_BackupVolume`, `UV_ReleaseVolume`, `UV_AddSite`, `UV_RemoveSite`), dump/restore (`UV_DumpVolume`, `UV_RestoreVolume`), listing (`UV_ListPartitions`, `UV_XListVolumes`, `UV_XListOneVolume`, `UV_ListOneVolume`, `UV_VolserStatus`), synchronization (`UV_SyncVldb`, `CheckVldb`, `UV_SyncServer`), metadata changes (`UV_SetVolume`, `UV_RenameVolume`), and the `CLOCKSKEW` constant used for incremental dump safety.

## Control Flow
The header itself has no runtime flow. Its signatures establish the calling convention used by libadmin: functions return boolean-like success, place detailed OpenAFS status in `afs_status_p`, and accept either a cell handle, an existing volserver Rx connection, or server/partition ids depending on whether the function must touch VLDB, volserver, or both.

## State And Persistence
No state is stored in the header. The exposed operations manipulate persistent VLDB entries, volume headers, volume transactions, dump files, and replica state through the implementation.

## Dependencies And Integration Points
Consumers inherit dependencies on `rx`, `ubik`, `vlserver`, `volser`, `vldbint`, `afs_Admin`, `kautils`, `cellconfig`, `afsint`, and platform socket/file headers. Signature drift here breaks callers in the admin library and any VOS administration wrappers.

## Risks And Test Signals
Risk centers on declaration/implementation mismatch and excessive include coupling. Build coverage of `src/libadmin/vos`, plus caller tests that compile against only this header, are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/vsprocs.h -->
