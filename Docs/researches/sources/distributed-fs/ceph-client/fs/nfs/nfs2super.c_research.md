# sources/distributed-fs/ceph-client/fs/nfs/nfs2super.c

## Purpose
`nfs2super.c` registers NFSv2 client support as a version-specific module. It binds the common NFS filesystem type and super operations to the NFSv2 RPC version and client operation vector.

## Important APIs, Types, And Functions
The file defines static `struct nfs_subversion nfs_v2` with `THIS_MODULE`, `&nfs_fs_type`, `&nfs_version2`, `&nfs_v2_clientops`, and `&nfs_sops`. `init_nfs_v2()` registers that subversion. `exit_nfs_v2()` unregisters it. Module metadata declares GPL licensing and the description.

## Control Flow And Integration Points
At module init, `register_nfs_version(&nfs_v2)` makes NFSv2 discoverable through the registry declared in `nfs.h`. The common mount path can then select NFSv2, use `nfs_version2` from `nfs2xdr.c` for RPC procedure metadata, and call `nfs_v2_clientops` from the common v2 client implementation. Module exit removes the version from lookup.

## State And Persistence Behavior
The only state is the static registration object. Its lifetime is the module lifetime, guarded by the version registry and module owner reference.

## Dependencies
The module depends on `nfs_fs_type`, `nfs_sops`, `nfs_version2`, and `nfs_v2_clientops` from the broader NFS client implementation.

## Risks And Edge Cases
Registration must happen exactly once, and unregister must match init. Missing or mismatched operation vectors would produce mount-time failures. NFSv2 has narrower protocol semantics, so callers must not assume v3/v4 capabilities when this subversion is selected.

## Test Signals
Build with NFSv2 enabled, load/unload the module, mount an NFSv2 export, confirm `/proc` or mount stats identify v2 RPCs, and verify NFSv3-only features such as ACLs are unavailable.
