# sources/distributed-fs/coda/coda-src/dir/fid.c

## Purpose
Utility functions for comparing, printing, copying, and constructing Coda `ViceFid` and directory-local `DirFid` identifiers, including special local/disconnected/repair FID forms.

## APIs, Types, and Functions
Exports `FID_PrintFid()`, `FID_CpyVol()`, `FID_Int2DFid()`, `FID_NFid2Int()`, `FID_VFid2DFid()`, `FID_DFid2VFid()`, `FID_Cmp()`, `FID_EQ()`, `FID_VolEQ()`, `FID_IsDisco()`, `FID_IsLocalDir()`, `FID_IsLocalFile()`, `FID_MakeDiscoFile()`, `FID_MakeDiscoDir()`, `FID_MakeSubtreeRoot()`, `FID_MakeLocalDir()`, `FID_MakeLocalFile()`, `FID_IsFakeRoot()`, `FID_MakeLocalSubtreeRoot()`, `FID_MakeRoot()`, `FID_IsVolRoot()`, and `FID_()`.

## Control Flow, State, and Persistence
Most functions directly fill or compare fields. Static constants define fake/local volume and vnode sentinel values: local file/dir vnodes, fake subtree root vnode, and root vnode/unique. `FID_()` formats a FID into one of four rotating static buffers.

## Dependencies and Integration
Used by directory handles, repair code, and conflict/disconnected operation paths. Depends on Coda FID type definitions and network byte-order helpers for `DirNFid` conversion.

## Risks and Test Signals
Risks include static buffer reuse in `FID_()`, sentinel collisions if real IDs overlap, no volume assignment in `FID_DFid2VFid()`, and global constants encoded as mutable statics. Test signals are ordering/equality checks, root/local/disconnected detection, and correct directory entry FID conversion.
