# sources/distributed-fs/ceph-client/fs/nfsd/flexfilelayout.c

## Purpose
`flexfilelayout.c` implements a minimal pNFS flex-file layout provider for NFSD where the metadata server is also the single data server and storage location is the same file exported over NFSv3.

## Important APIs, types, and functions
The exported integration object is `ff_layout_ops`. Its callbacks are `nfsd4_ff_proc_layoutget()`, `nfsd4_ff_proc_getdeviceinfo()`, and `nfsd4_ff_proc_layoutcommit()`, with XDR encoders supplied by `flexfilelayoutxdr.c`. It allocates and fills `struct pnfs_ff_layout` and `struct pnfs_ff_device_addr`.

## Control flow
For LAYOUTGET, the server allocates one layout descriptor, sets flags to avoid layoutcommit, discourage MDS I/O, and deny read I/O for RW layouts, adjusts uid for read-only segments to avoid write permission, derives a deviceid from the filehandle, copies the filehandle, and expands the granted segment to the whole file. For GETDEVICEINFO, it allocates one device address, sets NFSv3 version data, sizes from `svc_max_payload()`, derives netid and universal address from the request destination address, and returns it through `gd_device`. LAYOUTCOMMIT is accepted as a no-op.

## State and persistence
There is no durable layout state in this file. Per-request allocations are attached to NFSv4 layout response objects and encoded/freed by the surrounding pNFS code. Device generation is hard-coded to zero, and the layout is always a single mirror/single data-server model.

## Dependencies and integration points
The file depends on pNFS layout infrastructure, `nfsd4_set_deviceid()`, service payload sizing, RPC address formatting, and the flexfile XDR definitions. It is selected through export pNFS layout type setup and participates in NFSv4.1 pNFS operations.

## Risks and test signals
Risks include oversimplified topology assumptions, incorrect destination address selection behind NAT or multi-homed servers, uid manipulation causing unexpected client access behavior, deviceid generation collisions, and memory ownership between proc and encoder layers. Test signals include IPv4 and IPv6 GETDEVICEINFO, LAYOUTGET for read and read-write segments, whole-file segment verification, client behavior with `NO_READ_IO` and `NO_IO_THRU_MDS`, and pNFS disabled/export flag combinations.
