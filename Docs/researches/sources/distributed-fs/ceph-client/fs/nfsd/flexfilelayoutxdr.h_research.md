# sources/distributed-fs/ceph-client/fs/nfsd/flexfilelayoutxdr.h

## Purpose
`flexfilelayoutxdr.h` defines the in-memory flex-file pNFS layout/device structures that `flexfilelayout.c` populates and `flexfilelayoutxdr.c` encodes.

## Important APIs, types, and functions
It defines flexfile flag bits `FF_FLAGS_NO_LAYOUTCOMMIT`, `FF_FLAGS_NO_IO_THRU_MDS`, and `FF_FLAGS_NO_READ_IO`; address length constants `FF_NETID_LEN` and `FF_ADDR_LEN`; `struct pnfs_ff_netaddr`; `struct pnfs_ff_device_addr`; and `struct pnfs_ff_layout`. It declares `nfsd4_ff_encode_getdeviceinfo()` and `nfsd4_ff_encode_layoutget()`.

## Control flow
There is no executable flow. The header establishes a two-stage contract: layout callbacks allocate/fill these structures, then XDR callbacks serialize them into protocol replies.

## State and persistence
The structures are per-operation response state. They contain protocol-level values such as NFS version, payload sizes, uid/gid, deviceid, stateid, and filehandle copies, but no durable server registry.

## Dependencies and integration points
The header depends on IPv6 address length definitions and NFSD NFSv4 XDR types. It is included by the pNFS flexfile provider and its encoder.

## Risks and test signals
Risks include fixed string buffers becoming too small for future netids/universal address forms, flag definitions diverging from encoder behavior, and structure ownership ambiguity. Test signals include compile-time users of both encoders, maximum-length universal address generation, and pNFS client decode coverage for every flag.
