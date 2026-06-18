# sources/distributed-fs/openafs/src/vol/vol-salvage.c

## Purpose
Implements the OpenAFS salvager core for partition-wide and single-volume-group repair. It scans vice inodes, correlates them with `V*.vol` disk headers, repairs or recreates missing special inodes, validates vnode indexes against backing inodes, repairs directory trees, handles orphan policy, adjusts namei/link-table link counts, and coordinates with the fileserver through FSYNC/SALVSYNC when salvaging a live demand-attach fileserver volume.

## Important APIs, Types, and Functions
Global options implement the salvager command surface declared in `vol-salvage.h`: `debug`, `Testing`, `ListInodeOption`, `ShowRootFiles`, `RebuildDirs`, `Parallel`, `PartsPerDisk`, `forceR`, `ShowLog`, `ShowSuid`, `ShowMounts`, `orphans`, `Showmode`, `OKToZap`, and `ForceSalvage`.

`struct SalvInfo` is the per-job state carrier. It tracks the current partition/device/path, the active volume-group link handle, the copied `VolumeDiskData`, inode and volume summaries, per-class `VnodeInfo`, whether volume contents changed, and whether FSYNC should be used.

Major entrypoints are `SalvageFileSysParallel`, `SalvageFileSys`, `SalvageFileSys1`, `GetInodeSummary`, `GetVolumeSummary`, `DoSalvageVolumeGroup`, `SalvageVolumeHeaderFile`, `SalvageHeader`, `SalvageVnodes`, `SalvageIndex`, `SalvageVolume`, and the fileserver coordination calls `AskOffline`, `AskOnline`, `AskDelete`, `AskError`, and `AskDAFS`.

Supporting repair functions include `CompareInodes`, `CountVolumeInodes`, `CompareVolumes`, `DeleteExtraVolumeHeaderFile`, `QuickCheck`, `FindLinkHandle`, `CreateLinkTable`, `CheckDupLinktable`, `DistilVnodeEssence`, `SalvageDir`, `JudgeEntry`, `CopyOnWrite`, `CopyAndSalvage`, `CreateRootDir`, `CreateReadme`, `MaybeZapVolume`, `ClearROInUseBit`, `CopyInode`, `UseTheForceLuke`, `RemoveTheForce`, `Fork`, `Wait`, `Log`, `Abort`, and `Exit`.

## Control Flow
Partition salvage can be scheduled by `SalvageFileSysParallel`, which limits concurrent workers to `Parallel`, chains partitions thought to share the same disk by `SameDisk`, forks per-partition salvagers, writes child logs as numbered `SalvageLog.N` files, and merges those logs after all jobs complete. `SalvageFileSys` is the simpler single-partition wrapper and forks unless running in debug or a non-forking platform mode.

`SalvageFileSys1` initializes a fresh `SalvInfo`, locks either the partition or the target volume group, sets `ForceSalvage` from the `FORCESALVAGE` sentinel or single-volume mode, removes stale `salvage.inodes.*` and `salvage.temp.*` files, creates an unlinked temporary inode list, and calls `GetInodeSummary`. If `-i` was requested it only prints inodes and returns the single volume online if possible.

`GetInodeSummary` calls `ListViceInodes`, optionally filtered by `OnlyOneVolume`, sorts entries through `CompareInodes`, rewrites the temporary inode file in sorted order, and writes an `InodeSummary` record per volume. The sorting groups special and data inodes by RW volume group and orders duplicate vnode candidates so the most desirable inode is considered first.

`GetVolumeSummary` first tries `AskVolumeSummary` for DAFS/salvageserver volume-group membership from the fileserver VG cache. If that is unavailable, it scans partition volume headers using `VWalkVolumeHeaders`, `CountHeader`, `RecordHeader`, and `UnlinkHeader`. Badly named or unreadable headers are deleted for partition salvage, while single-volume salvage is more conservative. Volume summaries are sorted so an RW volume precedes its clones.

`SalvageFileSys1` then walks inode summaries by RW volume group, matches each inode summary to a partition header summary, deletes extra header files without actual data, and invokes `DoSalvageVolumeGroup`. Extra headers remaining after the inode pass are also deleted. In single-volume mode it brings all non-deleted VG members back online, prioritizing the requested volume, or sends DONE/delete if the requested volume never existed in the resulting summary.

`DoSalvageVolumeGroup` optionally skips clean volumes via `QuickCheck`, forks per volume group, reads the group's inode range, locates or recreates the namei link table, then salvages RO clones before the RW volume. Each volume is checked in two passes: a non-mutating check pass can decide whether a clone or partial volume should be removed, and the second pass performs header and vnode repairs. After all volumes are processed, residual `ViceInodeInfo.linkCount` deltas are applied with `IH_INC`/`IH_DEC`, then the RW volume receives directory/tree salvage through `SalvageVolume`.

`SalvageVolumeHeaderFile` constructs the expected `VolumeHeader` from special inodes, uses the current `.vol` header to choose among duplicate special inodes, deletes or ignores duplicate special files according to orphan policy, recreates missing required special inodes through `SalvageHeader`, writes or creates the top-level disk header when it differs, and initializes the `volumeInfoHandle`.

`SalvageIndex` walks a small or large vnode index, skips `vNull` records, removes partially allocated vnodes with bad magic, reconciles vnode inode numbers, uniquifiers, data versions, and lengths against the sorted inode list, zeroes RW vnodes with no backing inode, and decrements matching inode link counts so later link-count reconciliation knows the inode is referenced.

`SalvageVolume` reads the RW volume info, distills large and small vnode indexes into `VnodeEssence` arrays, recursively salvages directories with `SalvageDir`, optionally creates a replacement root directory and README when the root is gone and `-orphans attach` is active, attaches or removes orphaned vnodes according to policy, writes changed vnode records, recalculates file/block counts and uniquifier, breaks callbacks or removes fsstate when needed, and finally clears `inUse`/`needsSalvaged`, sets `dontSalvage`, and writes the repaired `VolumeDiskData`.

## State and Persistence Behavior
The code directly mutates the on-disk volume representation unless `Testing` is set. Persistent effects include deleting bad or extra `V*.vol` headers, creating missing special inodes, recreating volume headers, fixing namei link tables, changing vnode index records, copying and replacing directory inodes before mutation, deleting orphaned vnodes, attaching orphaned vnodes under root with generated `__ORPHAN*__` names, creating a replacement root plus `README.ROOTDIR`, updating link counts, and rewriting volume metadata.

Safety state is recorded in volume headers: DAFS `LockVolume` sets `inUse = programType` before salvage so a crash leaves the volume needing salvage. Successful salvage clears `inUse`, `needsSalvaged`, sets `inService`, and sets `dontSalvage = DONT_SALVAGE`. If content changed, `needsCallback` and `updateDate` are updated.

Temporary inode and summary files are created under the partition or `tmpdir`, unlinked after opening, and read through file descriptors. `FORCESALVAGE` is consumed after full-partition salvage. Logging is persistent via the OpenAFS server log machinery unless client mode writes timestamped messages to stderr.

## Dependencies and Integration Points
The file is tightly integrated with OpenAFS volume internals: `ihandle`, `vnode`, `volume`, `partition`, `viceinode`, `volinodes`, `vol-salvage`, `salvage`, `vol_internal`, and directory routines from `afs/dir.h`. It depends on platform inode scanners through `ListViceInodes`, volume header walkers/readers/writers through `VWalkVolumeHeaders`, `VReadVolumeDiskHeader`, `VCreateVolumeDiskHeader`, `VWriteVolumeDiskHeader`, and `VDestroyVolumeDiskHeader`, and namei helpers such as `namei_SetLinkCount`, `namei_HandleToName`, and `namei_FixSpecialOGM`.

Live fileserver integration uses FSYNC (`FSYNC_VolOp`, `FSYNC_VGCQuery`, `FSYNC_VerifyCheckout`, reconnect/disconnect helpers) and optionally SALVSYNC (`SALVSYNC_LinkVolume`, reconnect/disconnect helpers). DAFS builds add volume lock-file coordination via `VLockVolumeByIdNB`, `VVolLockType`, and partition lock reinitialization. `SetSalvageDirHandle` is imported from `vol_internal.h` to bind directory handles to salvager I/O.

## Risks
This code intentionally repairs corrupt persistent state, so false positives are dangerous. The two-pass check/repair pattern reduces risk, but many paths still use `opr_Assert`/`opr_Verify` for I/O invariants, causing aborts instead of graceful recovery. Link-count reconciliation is subtle because `ViceInodeInfo.linkCount` is a delta after reference scanning; wrong decrements can leak data or prematurely drop inodes. Orphan attachment rewrites parent/unique state and root directory contents, so it can expose old cached-client inconsistencies, which the recreated-root README explicitly warns about.

Concurrency risks are guarded by salvage locks, partition/volume locks, FSYNC checkout verification, retries for fileserver restarts, and disk grouping for parallel salvage. Remaining risks include races with unauthorized volserver/fileserver activity during partition salvage, stale fileserver VG cache data, failure to break callbacks after mutations, and platform-specific behavior around unlinked temporary files and root inode checks.

## Test Signals
Useful test signals are salvager log lines for forced salvage, duplicate special inode handling, missing headers, vnode length/inode/unique repairs, orphan counts, callback-break failures, and final `Salvaged NAME (ID): files, blocks`. Dry-run `Testing` mode should report intended mutations without writing. `ListInodeOption` validates inode enumeration/sorting. Partition tests should cover clean quick-check volumes, missing `.vol` headers, corrupt special inode magic, duplicate specials with one header-referenced candidate, missing backing inodes, bad directory `.`/`..`, orphan attach/remove/ignore, namei link table recreation, DAFS FSYNC denied/retry paths, and single-volume salvage of a clone that must be rescheduled as an RW volume group.

## Source Notes
Read as C implementation; 5029 source lines; source-tree-aligned report generated for subset `subset-b-007819`.
