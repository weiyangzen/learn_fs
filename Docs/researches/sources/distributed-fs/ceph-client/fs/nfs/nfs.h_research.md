# sources/distributed-fs/ceph-client/fs/nfs/nfs.h

## Purpose
`nfs.h` is the small public-private interface between the common NFS module and version-specific NFS modules. It defines how NFSv2, NFSv3, and other subversions register their filesystem, RPC version, operation vector, superblock operations, and xattr handlers.

## Important APIs, Types, And Functions
`struct nfs_subversion` carries `owner`, `nfs_fs`, `rpc_vers`, `rpc_ops`, `sops`, and optional `xattr` handler pointers. The declared registry API is `find_nfs_version()`, `get_nfs_version()`, `put_nfs_version()`, `register_nfs_version()`, and `unregister_nfs_version()`.

## Control Flow And Integration Points
Version modules such as `nfs2super.c` and `nfs3super.c` define a static `struct nfs_subversion`, fill it with their version-specific `rpc_version` and `nfs_rpc_ops`, and register it at module init. Mount parsing and server creation can then locate the requested version and hold a module reference through `get_nfs_version()`.

## State And Persistence Behavior
The file defines no state directly. Registered `nfs_subversion` objects persist for the lifetime of their modules. The `owner` module pointer is part of the lifetime contract that prevents use after unload while a version is active.

## Dependencies
The interface depends on VFS `file_system_type`, SunRPC scheduling/RPC version types, NFS XDR declarations, and the common `struct nfs_rpc_ops` contract.

## Risks And Edge Cases
Incorrect registration or missing module reference handling can lead to unsupported version lookup failures or module unload races. Optional `xattr` handlers must match version capabilities. Because this header is included by version modules, ABI-like changes affect all NFS version registrations.

## Test Signals
Build and load/unload NFSv2 and NFSv3 modules, mount explicit protocol versions, verify unsupported versions fail cleanly, and test module unload refusal while mounts are active.
