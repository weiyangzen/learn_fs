# subset-b-007819 Research

Grouped research report for OpenAFS volume salvage and volume inspection entrypoints. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vol-salvage.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vol-salvage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vol-salvage.h -->
# sources/distributed-fs/openafs/src/vol/vol-salvage.h

## Purpose
Declares the salvager version, core salvage data structures, command-line global flags, platform-specific NT job structures, and external function prototypes used by the OpenAFS salvager implementation.

## Important APIs, Types, and Functions
`SalvageVersion` is `2.4`. `struct InodeSummary` summarizes the sorted inode list for one volume, including volume id, RW parent id, starting index, inode counts, special inode counts, maximum inode uniquifier, and a linked `VolumeSummary`. `readOnly(isp)` detects clone summaries by comparing `volumeId` and `RWvolumeId`.

`struct VolumeSummary` wraps a `VolumeHeader`, an opened `volumeInfoHandle`, and flags describing deletion, callback needs, and whether the header is still unused/extra. `struct VnodeInfo` describes a vnode index and owns per-vnode `VnodeEssence` records for link count, claimed/changed/salvaged/todelete state, parent, unique, name, mode, inode, type, and owner metadata. `struct DirSummary` carries a directory handle plus vnode identity, dot/dotdot status, copy-on-write state, parent/name, and link handle.

The header exports orphan modes `ORPH_IGNORE`, `ORPH_REMOVE`, and `ORPH_ATTACH`, `MAXPARALLEL`, `ROOTINODE`, `canfork`, `tmpdir`, and prototypes for all major salvage, logging, FSYNC, header, vnode, directory, inode, and NT helper routines.

## Control Flow
This file does not implement control flow, but it defines the contract used by `vol-salvage.c`: partition salvage builds `InodeSummary` and `VolumeSummary`, per-volume salvage populates `VnodeInfo`, directory salvage mutates `DirSummary`, and the public routines operate in the sequence `SalvageFileSys*` -> `GetInodeSummary`/`GetVolumeSummary` -> `DoSalvageVolumeGroup` -> `SalvageVolumeHeaderFile`/`SalvageVnodes` -> `SalvageVolume`.

## State and Persistence Behavior
The structures here are in-memory summaries of persistent AFS state. Their fields directly drive disk writes in the implementation: special inode references, `.vol` header creation/deletion, vnode index changes, directory copy-on-write, link-count reconciliation, callback signaling, and orphan disposition.

## Dependencies and Integration Points
Includes `salvage.h` and `volinodes.h`, so it depends on common salvager definitions, `ViceInodeInfo`, inode constants, and the `afs_inode_info` table. It references volume, vnode, inode, partition, and directory types supplied by the broader `src/vol` build. NT-only declarations integrate with the Windows spawned-child salvage path.

## Risks
Because this header exports many globals, option state is process-wide and fork/thread behavior must be handled carefully. The nested `VnodeEssence` type is embedded inside `VnodeInfo`, so consumers rely on this exact layout. `fileSysPath[9]` in `SalvInfo` is intentionally narrow for traditional `/vicepX` paths in the C file; code using this contract must avoid assuming arbitrary long partition display names fit there.

## Test Signals
Compile tests should catch prototype drift between `vol-salvage.c` and the header. Salvager behavioral tests indirectly validate `InodeSummary`, `VolumeSummary`, and `VnodeInfo` layout by exercising inode sorting, volume grouping, header matching, vnode scans, and orphan policies.

## Source Notes
Read as C header; 250 source lines; source-tree-aligned report generated for subset `subset-b-007819`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vol-salvage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vol_internal.h -->
# sources/distributed-fs/openafs/src/vol/vol_internal.h

## Purpose
Provides a small internal volume-module prototype boundary. In this subset it exposes the physical I/O helper needed by the salvager to initialize directory handles.

## Important APIs, Types, and Functions
The only declaration is `SetSalvageDirHandle(DirHandle *, VolumeId, Device, Inode, int *)`, implemented by `physio.c`. It binds a `DirHandle` to a volume id, device, inode, and a change flag pointer.

## Control Flow
There is no executable control flow. `vol-salvage.c` calls `SetSalvageDirHandle` before checking, copying, rebuilding, or mutating AFS directories in `CopyOnWrite`, `CopyAndSalvage`, `CreateRootDir`, `SalvageDir`, and orphan attachment.

## State and Persistence Behavior
The helper declaration is persistence-critical because the resulting `DirHandle` is the object through which directory operations read and write directory inodes. The `int *` change flag lets low-level directory handling propagate that a volume was modified.

## Dependencies and Integration Points
Requires `DirHandle`, `VolumeId`, `Device`, and `Inode` definitions from the including volume sources. It creates an intentional private dependency from salvage logic to physical directory I/O without exporting the entire `physio.c` surface.

## Risks
The narrow header means type availability depends on include order. Any signature change in `physio.c` must be kept synchronized here and across salvager call sites.

## Test Signals
Compilation validates the prototype. Directory salvage tests that repair, copy, or create directories validate the runtime behavior behind this declaration.

## Source Notes
Read as C header; 8 source lines; source-tree-aligned report generated for subset `subset-b-007819`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vol_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vol_prototypes.h -->
# sources/distributed-fs/openafs/src/vol/vol_prototypes.h

## Purpose
Collects cross-file prototypes for several volume package helpers that are shared outside their implementation files: clone operations, volume nuking, and volume utility metadata routines.

## Important APIs, Types, and Functions
`CloneVolume(Error *, Volume *, Volume *, Volume *)` and `vol_PollProc` expose clone support. `nuke(char *, afs_int32)` exposes destructive partition/volume removal. The vutil prototypes cover `AssignVolumeName`, `AssignVolumeName_r`, `ClearVolumeStats`, `ClearVolumeStats_r`, `CopyVolumeStats`, `CopyVolumeStats_r`, and `CopyVolumeHeader`.

## Control Flow
The header is declarative. Consumers call these helpers when creating clones, destroying volume contents, assigning generated names, clearing/copying accounting fields, or copying disk header structures.

## State and Persistence Behavior
The declared routines modify in-memory `VolumeDiskData` and `Volume` structures, and in the case of cloning/nuking can drive persistent volume state changes through their implementations. The `_r` variants signal reentrant/thread-aware utility paths.

## Dependencies and Integration Points
Depends on volume package types such as `Error`, `Volume`, `VolumeDiskData`, and `afs_int32` being visible before inclusion. It is a compatibility-style aggregate prototype header used by volume utilities that need a small subset of implementation APIs.

## Risks
As a shared prototype bucket, it can hide coupling between unrelated volume subsystems. Signature drift or missing includes will show up as compile failures, but semantic coupling, especially around `nuke`, needs implementation-level tests.

## Test Signals
Build coverage is the primary direct signal. Clone, volume-delete, and header-copy tests indirectly verify that these prototypes match the implementation ABI.

## Source Notes
Read as C header; 30 source lines; source-tree-aligned report generated for subset `subset-b-007819`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vol_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/voldefs.h -->
# sources/distributed-fs/openafs/src/vol/voldefs.h

## Purpose
Defines fundamental volume type constants, volume-group limits, partition limits, on-disk volume header filename formats, and server metadata paths for the OpenAFS volume package.

## Important APIs, Types, and Functions
Volume type aliases map historic names to numeric constants: `RWVOL`, `ROVOL`, `BACKVOL`, and `RWREPL`, with `VOLMAXTYPES` set to 4. `VOL_VG_MAX_VOLS` caps volume group members handled together at 20. `VOL_MAX_CHECKOUT_RETRIES` caps retry loops when checkout/locking races with fileserver restart. `VOLMAXPARTS` is 255.

`VFORMATDIGITS`, `VHDREXT`, `VFORMAT`, and `VHDRNAMELEN` define the `V0000000000.vol` or legacy `.vl` header filename contract. `VMAXPATHLEN` caps external volume path names. Namei builds define `INODEDIR` as `AFSIDat`. `MAXVOLIDPATH` and `SERVERLISTPATH` point to server-wide volume id and server id metadata.

## Control Flow
No executable control flow exists here. These constants steer parsing, allocation, retry, and filename generation in the volume package. In this subset, `vol-salvage.c` uses `VOL_VG_MAX_VOLS`, `VOL_MAX_CHECKOUT_RETRIES`, `VOLMAXPARTS`, `VFORMAT`, `VHDRNAMELEN`-related naming behavior, `VMAXPATHLEN`, and volume type constants.

## State and Persistence Behavior
The filename macros are persistent ABI: changing `VHDREXT` or `VFORMAT` changes the names used for on-disk volume header files and must match all readers/writers. The volume type constants are stored in volume metadata and interpreted by fileserver, volserver, and tooling.

## Dependencies and Integration Points
Requires `<afs/param.h>` before filename macros so `AFS_VOLID_FMT` is available. Integrates with `volume.h`, salvager, vutil, namei storage, max volume id allocation, and server identity configuration.

## Risks
The comments explicitly warn that changing volume types requires checking `volumeWriteable` and that `VHDREXT` and `VFORMAT` must change together. `VOL_VG_MAX_VOLS` bounds DAFS VG query handling; exceeding it would require protocol and allocation changes.

## Test Signals
Header filename round-trip tests, volume creation/deletion, salvager volume-header scanning, and platform builds for AIX/HPUX versus normal `.vol` naming validate this file. Retry behavior around fileserver restarts exercises `VOL_MAX_CHECKOUT_RETRIES`.

## Source Notes
Read as C header; 93 source lines; source-tree-aligned report generated for subset `subset-b-007819`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/voldefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/volinfo-main.c -->
# sources/distributed-fs/openafs/src/vol/volinfo-main.c

## Purpose
Implements the `volinfo` command-line entrypoint for dumping or repairing selected OpenAFS volume internals through the shared `vol-info` scanning backend.

## Important APIs, Types, and Functions
`VolInfo` is the command callback. It initializes the backend with `volinfo_Init`, allocates options with `volinfo_Options`, translates command flags into `struct VolInfoOpt`, registers vnode handlers with `volinfo_AddVnodeHandler`, and invokes `volinfo_ScanPartitions`.

Supported parameters include `-checkout`, `-vnode`, `-date`, `-inode`, `-itime`, `-part`, `-volumeid`, `-header`, `-sizeonly`/`-sizeOnly`, `-fixheader`, `-saveinodes`, `-orphaned`, and namei-only `-filenames`.

## Control Flow
`main` creates a single cmd syntax object and dispatches. `VolInfo` initializes defaults, parses optional partition and numeric volume id, rejects `-volumeid 0`, then applies option interactions. `-saveinodes` and `-sizeonly` suppress default info/header/vnode/time/orphan output. `-orphaned` and `-filenames` imply vnode dumping for compatibility. It registers handlers for saving all file inodes, accumulating size totals, and printing large/small vnode data before scanning the requested partition(s).

## State and Persistence Behavior
Most modes are read-only scans. `-checkout` can coordinate with a running fileserver to check out volumes. `-fixheader` may repair headers through the shared backend, and `-saveinodes` writes extracted volume files into the current directory. The allocated `VolInfoOpt` is freed before return.

## Dependencies and Integration Points
Depends on OpenAFS command parsing (`afs/cmd.h`), volume primitives (`ihandle`, `vnode`, locks, rx queues), and `vol-info.h` for options, handlers, and scanning. It includes `AFS_component_version_number.c` on non-NT builds for version stamping.

## Risks
Option interactions are compatibility-sensitive: scripts may depend on `-orphaned` implying `-vnode` and `-sizeOnly` spelling. `strtoul` only checks for zero, so malformed strings with numeric prefixes may be partially accepted by libc semantics. Modes that write files or fix headers need care when run against live volumes without `-checkout`.

## Test Signals
CLI tests should cover invalid `-volumeid`, `-sizeonly` suppressing other output, `-orphaned` and `-filenames` handler registration, namei conditional option availability, and scans of all partitions versus selected partition/volume.

## Source Notes
Read as C command entrypoint; 198 source lines; source-tree-aligned report generated for subset `subset-b-007819`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/volinfo-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/volinodes.h -->
# sources/distributed-fs/openafs/src/vol/volinodes.h

## Purpose
Defines the common table describing special volume inodes and provides `init_inode_info`, which adapts that table to a specific `VolumeHeader` instance.

## Important APIs, Types, and Functions
`NO_LINK_TABLE` is platform-dependent: namei builds use link tables, while non-namei builds mark them obsolete. `MAXINODETYPE` is `VI_LINKTABLE`, the highest special inode type tracked.

`struct afs_inode_info` describes a special inode by expected `versionStamp`, `inodeType`, fixed header size, pointer to the inode field in a `VolumeHeader`, human description, and an `obsolete` flag.

`afs_common_inode_info` lists volume info (`VI_VOLINFO`), small vnode index, large vnode index, ACL, mount table, and link table. ACL and mount table are obsolete; link table is obsolete outside namei. `init_inode_info` copies the common table and converts stored `offsetof(struct VolumeHeader, field)` values into actual pointers into the caller's `VolumeHeader`.

## Control Flow
The header has one inline loop in `init_inode_info`. Salvager code creates a temporary `VolumeHeader`, calls this helper, fills inode fields from discovered special inodes, and passes each `afs_inode_info` entry to `SalvageHeader`.

## State and Persistence Behavior
This table defines which special inodes must exist, how much header data must be read to validate magic/version, which `VolumeHeader` fields reference them, and which old inode types the salvager may delete or ignore. It therefore drives persistent volume header repair and special-inode recreation.

## Dependencies and Integration Points
Requires `VolumeHeader`, `versionStamp`, `Inode`, volume magic/version constants, and `VI_*` special inode constants. It is used by vutil and salvager logic to keep volume header interpretation consistent.

## Risks
The comment notes `inodeType` is redundant because the table must be ordered. If `VI_*` numbering or `VolumeHeader` layout changes without updating this table, the salvager can validate or write the wrong inode field. The offset-to-pointer cast is deliberate but sensitive to structure layout and include definitions.

## Test Signals
Tests that recreate missing volume info, vnode index, and namei link-table inodes validate this mapping. Platform builds should verify namei versus non-namei obsolete behavior. Corrupt magic tests verify the expected stamps and sizes.

## Source Notes
Read as C header; 113 source lines; source-tree-aligned report generated for subset `subset-b-007819`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/volinodes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/volscan-main.c -->
# sources/distributed-fs/openafs/src/vol/volscan-main.c

## Purpose
Implements the `volscan` command-line entrypoint for machine-readable scans of volume vnode information using the shared `vol-info` backend.

## Important APIs, Types, and Functions
`ColumnNames` is generated from `VOLSCAN_COLUMNS` for command help. `VolScan` initializes `volinfo`, sets `VolInfoOpt` into volscan mode (`dumpInfo = 0`), parses filters and output settings, registers detail/ACL handlers, and invokes `volinfo_ScanPartitions`.

Supported parameters include `-checkout`, `-partition`, `-volumeid`, `-type`, `-find`, `-mask`, `-output`, `-delim`, `-noheading`, and `-ignore-magic`.

## Control Flow
`main` defines the cmd syntax and dispatches. `VolScan` parses partition and volume id, rejects zero volume ids, enables or disables headings, optionally disables directory magic checks, copies a delimiter with a 15-byte cap, and computes scan filters. With no `-type`, it scans RW, RO, and BK volumes; explicit values must be `rw`, `ro`, or `bk`. With no `-find`, it finds files, directories, mounts, and symlinks; explicit values may also include `acl`. Mode masks are parsed as octal and bounded by the option array. Output defaults to `host`, `desc`, `fid`, `dv`, optional ACL columns, and `path`; explicit columns are validated by `volinfo_AddOutputColumn`. Vnode handlers are registered for large vnodes, small vnodes, and ACL scanning according to the find mask.

## State and Persistence Behavior
The scanner is intended to be read-only, except that `-checkout` interacts with the running fileserver to safely inspect checked-out volumes. Output formatting state lives in `VolInfoOpt`, including delimiter, heading, filters, masks, and selected columns.

## Dependencies and Integration Points
Uses OpenAFS cmd parsing, rx queues, locks, ihandle/vnode definitions, and `vol-info.h` scanning/printing functions. It shares the same scanner backend as `volinfo-main.c`, making CLI behavior a thin configuration layer around reusable volume traversal logic.

## Risks
`strncpy` caps delimiters but silently truncates long delimiters. `strtoul`/`strtol` validation is minimal and treats zero masks as invalid, so users cannot search for mask `0000`. Unknown filter or column values fail early. `-ignore-magic` can trade path-lookup validation for resilience when directories are corrupt, so tests should cover both modes.

## Test Signals
CLI tests should cover default columns, ACL columns when `-find acl` is used, invalid `-type`, invalid `-find`, too many masks, invalid masks, unknown output columns, delimiter truncation, heading suppression, and partition/volume-specific scans.

## Source Notes
Read as C command entrypoint; 255 source lines; source-tree-aligned report generated for subset `subset-b-007819`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/volscan-main.c -->
