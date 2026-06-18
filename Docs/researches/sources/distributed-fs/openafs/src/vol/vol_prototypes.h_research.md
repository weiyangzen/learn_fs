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
