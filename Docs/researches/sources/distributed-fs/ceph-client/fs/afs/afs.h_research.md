# sources/distributed-fs/ceph-client/fs/afs/afs.h

## Purpose
`afs.h` defines protocol-wide AFS types, limits, identifiers, callback/status records, access masks, volume metadata, and XDR UUID layout shared across the client.

## Important APIs, types, and functions
Important definitions include cell/volume/path length limits, `afs_volid_t`, `afs_vnodeid_t`, `afs_dataversion_t`, `afs_voltype_t`, `afs_file_type_t`, `afs_lock_type_t`, `struct afs_fid`, `struct afs_callback`, `struct afs_callback_break`, `struct afs_uuid`, `struct afs_volume_info`, `afs_access_t` ACE bits, `struct afs_file_status`, `struct afs_status_cb`, status-change flags, `struct afs_volsync`, `struct afs_volume_status`, `AFS_BLOCK_SIZE`, and `struct afs_uuid__xdr`.

## Control flow
This header is declarative. Client RPC, inode, volume, validation, callback, and security code use these types to encode/decode wire data and represent cached metadata.

## State and persistence
The structures represent runtime state derived from remote AFS servers and wire-persistent identifiers such as volume IDs, vnode IDs, uniquifiers, callbacks, and status data.

## Dependencies and integration points
It integrates with file service, volume location, cache manager, YFS, and RxRPC client code.

## Risks and test signals
Risks include width/endian mistakes, limit mismatches against protocol specs, and stale shared type assumptions. Test signals include XDR encode/decode tests, large vnode/volume IDs, callback break records, file status conversion, ACL masks, and YFS high-vnode compatibility.
