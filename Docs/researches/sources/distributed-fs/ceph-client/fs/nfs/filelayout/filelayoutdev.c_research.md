# sources/distributed-fs/ceph-client/fs/nfs/filelayout/filelayoutdev.c

## Purpose
`filelayoutdev.c` implements deviceid and data-server operations for the pNFS files layout driver. It decodes GETDEVICEINFO opaque device data, builds the stripe-index table and data-server list, manages deviceid lifetime, computes stripe/data-server indices, selects per-stripe file handles, and connects to data servers on demand.

## Important APIs, types, and functions
Public functions are `nfs4_fl_alloc_deviceid_node`, `nfs4_fl_free_deviceid`, `nfs4_fl_put_deviceid`, `nfs4_fl_calc_j_index`, `nfs4_fl_calc_ds_index`, `nfs4_fl_select_ds_fh`, and `nfs4_fl_prepare_ds`. Module parameters `dataserver_timeo` and `dataserver_retrans` tune DS RPC connection retry behavior.

## Control flow
`nfs4_fl_alloc_deviceid_node` initializes an XDR stream over `pnfs_device` pages, decodes the stripe count, reads each 32-bit wire stripe index into a compact `u8` array, decodes the multipath/data-server count, validates limits and index ranges, allocates a flexible `nfs4_file_layout_dsaddr`, and initializes its generic deviceid node.

For each data-server entry, it decodes the multipath count and repeatedly calls `nfs4_decode_mp_ds_addr` to collect usable addresses. The address list is added to or looked up in the pNFS DS cache with `nfs4_pnfs_ds_add`; decoded temporary addresses are then drained. Failures unwind scratch folio, stripe indices, DS addresses, and any partially built dsaddr.

Stripe math uses `(offset - pattern_offset) / stripe_unit + first_stripe_index`, modulo stripe count, to derive `j`. The DS index is `stripe_indices[j]`. File-handle selection differs by sparse versus dense layouts: sparse layouts can use one shared file handle, the MDS OPEN file handle when `num_fh == 0`, or the DS index; dense layouts use the stripe index directly.

`nfs4_fl_prepare_ds` checks that the chosen DS exists, verifies or establishes the DS client connection with `nfs4_pnfs_ds_connect`, marks the deviceid unavailable on connection failure, and refuses to return a DS if the deviceid has become invalid/unavailable.

## State and persistence behavior
Decoded deviceid state is cached in memory and tied to the generic pNFS deviceid cache. Each dsaddr owns the stripe-index array and references to cached `struct nfs4_pnfs_ds` objects. Freeing drops DS references, frees the stripe table, and RCU-frees the dsaddr. Data-server connections are created lazily and cached in each DS object.

No local persistent state exists. Device availability state is runtime recovery state maintained through generic pNFS deviceid flags.

## Dependencies and integration points
This file depends on XDR decode helpers, folios for scratch decode, NFSv4 session/deviceid helpers, pNFS DS address decode/cache helpers, network namespace state from the server NFS client, and `filelayout.h` structures shared with `filelayout.c`.

## Risks
Malformed device data can otherwise corrupt routing. The code must reject excessive stripe counts, excessive multipath counts, stripe indices outside the DS list, empty usable DS address lists, and oversized file handles selected later by layout code. The compact `u8` array depends on enforcing the 256 multipath maximum before assignment.

Connection races are controlled by memory barriers and cached `ds_clp` checks; callers must handle NULL returns by falling back. If unavailable deviceids are not marked correctly, the client can repeatedly try broken DS paths or fail to return layouts.

## Test signals
Test valid and invalid GETDEVICEINFO blobs, zero/large stripe counts, maximum 4096 stripes, multipath count above 256, stripe index equal to DS count, empty multipath address lists, duplicate DS cache hits, DS connect failure, deviceid invalid/unavailable transitions, sparse zero-FH selection, dense stripe file-handle selection, and module parameter effects on DS connection attempts.
