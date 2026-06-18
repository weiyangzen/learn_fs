# sources/distributed-fs/ceph-client/fs/afs/afs_vl.h

## Purpose
`afs_vl.h` defines Volume Location service constants, operation IDs, VL error codes, YFS endpoint tags, VLDB entry structures, and XDR layouts.

## Important APIs, types, and functions
Key definitions include `AFS_VL_PORT`, `VL_SERVICE`, `YFS_VL_SERVICE`, `enum AFSVL_Operations`, `enum AFSVL_Errors`, YFS server/endpoint enums, `YFS_MAXENDPOINTS`, `struct afs_vldbentry`, `AFS_VLF_*` and `AFS_VLSF_*` flags, `struct afs_ListAddrByAttributes__xdr`, and `struct afs_uvldbentry__xdr`.

## Control flow
VL client and rotation code use these constants and structures to query volume records, server UUID/address data, capabilities, endpoints, and cell names.

## State and persistence
The structures represent remote persistent VLDB content and transient decoded results in the client.

## Dependencies and integration points
It depends on common AFS identifiers from `afs.h` and integrates with `vlclient.c`, DNS/cell setup, server list construction, and YFS upgrades.

## Risks and test signals
Risks include fixed array-size mismatches, XDR padding errors, UUID/server-index confusion, and VL error translation drift. Test signals include legacy and UUID VL entry queries, YFS endpoint decoding, max server lists, bad VLDB entries, and all VL error mappings.
