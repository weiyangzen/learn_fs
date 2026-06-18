# sources/distributed-fs/ceph-client/fs/nfs/pnfs.h

## Purpose
`pnfs.h` is the shared pNFS client contract. It defines the layout segment, layout header, layout driver, data-server address, device-id, and commit interfaces used by the generic NFS client and pNFS layout modules. It also provides inline helpers and disabled stubs so non-NFSv4 builds can compile pNFS call sites away cleanly.

## Important APIs, types, and functions
Core types are `struct pnfs_layoutdriver_type`, `struct pnfs_layout_hdr`, `struct pnfs_layout_segment`, `struct pnfs_device`, `struct pnfs_devicelist`, `struct nfs4_deviceid_node`, `struct nfs4_pnfs_ds_addr`, and `struct nfs4_pnfs_ds`. Driver callbacks cover mount setup/teardown, layout header and segment allocation, segment insertion, range return, pageio ops, DS commit info, sync, read/write pagelist attempts, device-id allocation/free, layoutreturn/layoutcommit/layoutstats preparation, and I/O cancellation. `struct pnfs_commit_ops` defines layout-driver hooks for DS commit bucketing.

Declared functions cover layout driver registration, NFSv4 layout procedures, layout cache lifecycle, layout update, layout return/commit, pNFS read/write completion, generic pageio integration, device-id cache operations, data-server cache/connect/decode, generic commit helpers, open-time layoutget helpers, mdsthreshold allocation, layout error handling, and layoutstats reporting. Inline helpers include `pnfs_enabled_sb()`, `pnfs_get_lseg()`, `pnfs_is_valid_lseg()`, `pnfs_calc_offset_end()`, `pnfs_calc_offset_length()`, `pnfs_end_offset()`, range-intersection helpers, commit helper dispatchers, `pnfs_sync_inode()`, `pnfs_return_layout()`, and `pnfs_lseg_cancel_io()`.

## Control flow
Consumers include this header to decide whether pNFS is active for an `nfs_server`, obtain or drop lseg/device references, dispatch to layout-driver operations, and fall back when pNFS is unavailable. Under `CONFIG_NFS_V4`, calls resolve to real functions implemented mostly in `pnfs.c`, `pnfs_dev.c`, and `pnfs_nfs.c`. Without NFSv4 support, the same names become harmless stubs returning false, zero, `NULL`, `PNFS_NOT_ATTEMPTED`, or no-op behavior, preserving call-site simplicity.

The header is also the main compile-time coupling between generic NFS pageio and layout modules: pNFS-aware read/write descriptors call `pnfs_update_layout()`, driver-specific pageio ops can call generic coalescing helpers, and commit code can route pages either to MDS lists or DS bucket lists through `pnfs_commit_ops`.

## State and persistence behavior
The declarations describe in-memory state. `pnfs_layout_hdr` holds volatile client layout state and sequence tracking; `pnfs_layout_segment` represents a server-granted range with refcounts and flags; `nfs4_deviceid_node` is a cached decoded `GETDEVICEINFO` result; `nfs4_pnfs_ds` represents a cached data-server endpoint set and optional connected `nfs_client`. None of these structures persist on disk. Server-visible persistence is mediated through RPCs declared here, especially `LAYOUTGET`, `LAYOUTRETURN`, `LAYOUTCOMMIT`, DS writes/commits, and layoutstats.

## Dependencies and integration points
The header depends on Linux refcounts, workqueues, NFS inode/page structures, NFSv4 stateid and layout UAPI types, RPC transport identifiers, and layout-driver modules such as files, flexfiles, block, SCSI, or object layouts. It is included by generic NFS code, NFSv4 procedure code, pNFS device code, and individual layout drivers. The `CONFIG_NFS_V4_2` guarded layoutstats declaration integrates with NFSv4.2 only when available.

## Risks and test signals
Risks center on API contract misuse: missing mandatory driver callbacks, refcount imbalance for lsegs/device IDs/data servers, wrong range arithmetic at `NFS4_MAX_UINT64`, using pNFS helpers when `pnfs_curr_ld` is `NULL`, commit op dispatch without initialized DS info, and divergence between real functions and stub semantics. Build tests should cover NFSv4 enabled/disabled and NFSv4.2 enabled/disabled. Runtime tests should exercise each inline dispatch path with no layout driver, a working driver, unavailable devices, invalid lsegs, DS commit pages, range boundary values, and layout return/commit policy flags.
