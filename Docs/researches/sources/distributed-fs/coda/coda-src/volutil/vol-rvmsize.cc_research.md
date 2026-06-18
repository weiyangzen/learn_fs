# sources/distributed-fs/coda/coda-src/volutil/vol-rvmsize.cc

## Purpose

`vol-rvmsize.cc` implements `S_VolRVMSize`, an administrative estimator for the RVM space consumed by a volume's header, vnode list arrays, vnode records, directory inodes, and directory pages. The complete 130-line file was read.

## Important APIs, Types, and Functions

The entry point is `S_VolRVMSize(RPC2_Handle, VolumeId, RVMSize_data *)`. It uses `XlateVid()`, `VGetVolume()`, `SRV_RVM(VolumeList[])`, `vindex`, `vindex_iterator`, `DI_Pages()`, and `VPutVolume()`.

## Control Flow

The handler initializes volutil mode, translates replicated ids to local replica ids, attaches the volume, accumulates fixed header/list sizes, fills vnode count and byte fields in `RVMSize_data`, iterates large vnodes to add directory-page bytes, then releases the volume and disconnects.

## State and Persistence Behavior

The handler is read-only with respect to persistent volume state. It computes from in-memory/RVM metadata and returns the result through the RPC output structure.

## Dependencies and Integration Points

Dependencies include `camprivate.h`, `vrdb.h`, `index.h`, `coda_globals.h`, `codadir.h`, and `volutil.h`. The client formatter is `volclient.cc`'s `rvmsize()` command.

## Risks and Test Signals

Risks include approximate accounting, assuming all large vnodes have valid `dirNode` pointers, ignoring volume logs and allocator overhead, and returning zero `status` even if accounting undercounts. Tests should compare known synthetic volumes, missing-volume errors, replicated id translation, directory page accounting, and empty-volume handling.
