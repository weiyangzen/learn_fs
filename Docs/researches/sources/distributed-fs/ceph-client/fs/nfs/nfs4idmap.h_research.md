# sources/distributed-fs/ceph-client/fs/nfs/nfs4idmap.h

## Purpose

`nfs4idmap.h` declares the NFSv4 ID mapping interface shared by client setup, XDR attribute encoding/decoding, and file-attribute postprocessing. It keeps the mapping API independent via forward declarations for NFS client/server/fattr/string structures.

## Important APIs, Types, and Functions

The header declares subsystem lifecycle functions `nfs_idmap_init` and `nfs_idmap_quit`, per-client lifecycle functions `nfs_idmap_new` and `nfs_idmap_delete`, fattr owner/group string helpers `nfs_fattr_init_names`, `nfs_fattr_free_names`, and `nfs_fattr_map_and_free_names`, mapping calls `nfs_map_name_to_uid`, `nfs_map_group_to_gid`, `nfs_map_uid_to_name`, `nfs_map_gid_to_group`, numeric parser `nfs_map_string_to_numeric`, and external cache timeout `nfs_idmap_cache_timeout`.

## Control Flow

The header defines no runtime control flow. It establishes call boundaries: client/module lifecycle code owns idmap initialization and cleanup; XDR and attribute code call the mapping functions; fattr decode paths initialize owner/group string storage then map and free it after decoding.

## State and Persistence Behavior

State is opaque to the header. Implementations maintain keyring caches, per-client idmap objects, user namespace references, and temporary fattr strings. `nfs_idmap_cache_timeout` controls key cache lifetime and is exposed as a module/sysctl parameter elsewhere.

## Dependencies and Integration Points

It includes `linux/uidgid.h` and `uapi/linux/nfs_idmap.h`, and is consumed by `nfs4client.c`, `nfs4idmap.c`, `nfs4xdr.c`, and NFSv4 super/sysctl code. The API is NFSv4-specific but supports generic Linux kuid/kgid types.

## Risks and Edge Cases

The header's main risk is contract mismatch: callers must pass valid server/client idmap context and must free mapped owner/group strings exactly once. Numeric parsing returns a boolean success indicator rather than errno, so callers must preserve that convention.

## Test Signals

Build coverage under NFSv4, owner/group encode/decode tests, idmap module parameter tests, and fattr mapping/freeing paths validate this interface.
