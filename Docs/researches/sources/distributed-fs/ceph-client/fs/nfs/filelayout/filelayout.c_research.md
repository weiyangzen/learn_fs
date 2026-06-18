# sources/distributed-fs/ceph-client/fs/nfs/filelayout/filelayout.c

## Purpose
`filelayout.c` implements the pNFS NFSv4.1 files layout driver. It decodes file layout segments, validates deviceids, maps logical file offsets to data-server offsets, routes reads/writes/commits to data servers, handles data-server errors and fallback to the metadata server, maintains pNFS commit buckets, and registers the layout driver with the generic pNFS client.

## Important APIs, types, and functions
The driver registers `filelayout_type` with layout id `LAYOUT_NFSV4_1_FILES`. Key operations are `filelayout_alloc_layout_hdr`, `filelayout_free_layout_hdr`, `filelayout_alloc_lseg`, `filelayout_free_lseg`, `filelayout_read_pagelist`, `filelayout_write_pagelist`, `filelayout_commit_pagelist`, `filelayout_alloc_deviceid_node`, and `filelayout_free_deviceid_node`.

Offset and striping helpers include `filelayout_get_dense_offset`, `filelayout_get_dserver_offset`, `filelayout_pg_test`, `select_bucket_index`, `calc_ds_index_from_commit`, and `select_ds_fh_from_commit`. Error and callback machinery includes `filelayout_async_handle_error`, read/write/commit prepare and done callbacks, `filelayout_reset_read`, `filelayout_reset_write`, and `filelayout_set_layoutcommit`.

## Control flow
Layout allocation decodes opaque `LAYOUTGET` data with XDR into a `struct nfs4_filelayout_segment`: deviceid, utilization flags, dense/sparse mode, commit-through-MDS flag, stripe unit, first stripe index, pattern offset, and file-handle array. The layout is validated for sane pattern offset and stripe unit, and later `filelayout_check_deviceid` binds the segment to a cached deviceid node, validates stripe index and file-handle counts, and atomically installs `fl->dsaddr`.

Read and write pageio initialization uses `fl_pnfs_update_layout` to acquire an appropriate layout segment. If no segment is available or a recoverable error occurs, pageio falls back to MDS operations. Coalescing is limited by generic pNFS checks and, for striped layouts, by stripe-unit boundaries so a single pageio header does not cross an incompatible data-server stripe.

For a DS read/write, the driver computes `j` from file offset, pattern offset, stripe unit, and first stripe index, maps it to a DS index through the device stripe map, prepares the DS connection, selects a data-server file handle, converts dense-layout offsets when needed, and initiates an async NFS RPC against the DS client. Completion callbacks handle NFSv4 sequence setup, stateid selection, stats, and propagation back to generic NFS pageio code.

Unstable writes are assigned to MDS or DS commit lists depending on `commit_through_mds` and stripe type. DS commit initiation selects the correct data server and file handle, then uses generic NFS commit setup with filelayout-specific call ops. Commit completion can request resend through MDS or set layoutcommit state.

## State and persistence behavior
Runtime state includes per-layout `struct nfs4_filelayout` commit info, per-segment file handles and deviceid reference, data-server client references on active RPC headers, layout failure flags, pNFS commit arrays, and layoutcommit markers. Persistent file data and layout metadata remain on the NFS server/MDS; this driver only caches decoded layout and device state.

Layout invalidation and fallback are explicit. Fatal DS layout errors destroy or mark the layout for return, wake waiters on the session slot table, and resend failed I/O through the MDS. Connection errors mark deviceids unavailable and set layout failure so future I/O avoids the broken DS until recovery.

## Dependencies and integration points
The driver depends on generic pNFS layout management, NFSv4.1 sessions, NFS pageio, NFS commit infrastructure, NFSv4 stateid/delegation helpers, SUNRPC task call ops, deviceid cache management from `filelayoutdev.c`, and layout-driver registration. It integrates directly with `direct.c` and buffered writeback through generic NFS pageio and commit abstractions.

## Risks
Offset math and stripe selection are correctness-critical. Dense layouts rewrite offsets; sparse layouts preserve offsets but may have one, zero, or many file handles. Bad file-handle count validation, stripe-unit crossing, or commit-bucket mapping can send data or COMMIT to the wrong DS. Error handling also must distinguish recoverable delays/session issues from layout-invalidating or device-unavailable failures.

Reference management is sensitive: DS client references, lseg references, commit-array lifetime, and RCU layout header freeing must align with asynchronous RPC completion. Fallback paths must set `NFS_IOHDR_REDO` exactly once and avoid double sequence completion.

## Test signals
Test sparse and dense layouts, single and multiple file handles, zero file-handle sparse layout, stripe-boundary pageio coalescing, commit-through-MDS and DS commit modes, DS session errors, DS connection failures, stale/badhandle layout errors, layout return after failure, verifier mismatch on commit, layoutcommit end-offset behavior, and module register/unregister.
