# sources/distributed-fs/ceph-client/fs/nfsd/flexfilelayoutxdr.c

## Purpose
`flexfilelayoutxdr.c` serializes NFSD flex-file pNFS layout and device-address data into NFSv4 XDR replies.

## Important APIs, types, and functions
The public encoders are `nfsd4_ff_encode_layoutget()` and `nfsd4_ff_encode_getdeviceinfo()`. They consume `struct pnfs_ff_layout` and `struct pnfs_ff_device_addr`, respectively. A small local `struct ff_idmap` stores decimal uid/gid strings.

## Control flow
`nfsd4_ff_encode_layoutget()` computes fixed and variable lengths for a single mirror, single data server, single filehandle flex-file layout; reserves XDR space; emits stripe unit, mirror/server counts, deviceid, efficiency, stateid, filehandle, uid/gid strings, flags, and stats hint. `nfsd4_ff_encode_getdeviceinfo()` handles the RFC 8881 zero-`gd_maxcount` probe by returning a zero length, otherwise reserves space for one netaddr and one version tuple and emits netid, universal address, NFS version/minor, rsize, wsize, and tight-coupling flag.

## State and persistence
The file has no retained state. It trusts that the layout and device structures attached by `flexfilelayout.c` remain valid for the duration of encoding.

## Dependencies and integration points
It depends on SUNRPC XDR stream helpers, NFSv4 constants, `svcxdr_encode_deviceid4()`, and flexfile structures in `flexfilelayoutxdr.h`. Its return values are NFS status codes such as `nfserr_toosmall` and `nfserr_resource` consumed by NFSv4 compound encoding.

## Risks and test signals
Risks include length miscalculation, failing to reserve enough padded XDR space, uid/gid string truncation if assumptions change, and mismatching RFC flex-file layout field order. Test signals include layout encoding under small reply buffers, zero maxcount GETDEVICEINFO, IPv6 universal addresses near `FF_ADDR_LEN`, non-root uid/gid values, and XDR decode validation by Linux and non-Linux pNFS clients.
