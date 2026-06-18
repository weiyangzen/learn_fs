# sources/distributed-fs/coda/coda-src/vol/dumpcamstorage.cc

Purpose: debugging/introspection code for dumping Coda recoverable storage (`SRV_RVM`) volume and vnode structures to stdout. It is not a mutation path; it exposes internal RVM state for diagnostics.

Important APIs: `dump_storage(level, tag)` prints global initialization, first volume slots, small/large vnode free-list entries, vnode free-list indexes, and `MaxVolId` when `VolDebugLevel` allows it. `print_VolHead`, `print_VolData`, `print_VnodeDiskObject`, and `print_VolumeDiskData` recursively render volume headers, `VolumeData`, recoverable vnode list contents, and `VolumeDiskData` fields. `PrintCamVnode`, `PrintCamDiskData`, and `PrintCamVolume` are level-gated wrappers used by recovery/volume code.

Control flow/state: the dump traverses `SRV_RVM(VolumeList[i])` and each recoverable `rec_smolist`, recovering containing `VnodeDiskObject` values with `strbase`. It calls `ExtractVnode` for targeted vnode display, so it exercises the same lookup path as index/recovery code.

Dependencies/integration: depends on `cvnode.h`, `volume.h`, VLDB/partition/vutil/fssync/index/recovery/cam globals, recoverable lists, and version-vector printing. Risks include hard-coded volume/free-list traversal limits in `dump_storage`, direct stdout output, and dereferencing corrupt RVM pointers during failure diagnosis. Test signals: enable high `VolDebugLevel`, create volumes with small/large vnodes, verify printed fields match RVM state, and run after salvage failures to ensure diagnostics do not crash on missing lists.
