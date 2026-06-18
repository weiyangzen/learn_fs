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
