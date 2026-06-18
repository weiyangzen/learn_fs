# sources/distributed-fs/ceph-client/fs/nfs/nfs3super.c

## Purpose
`nfs3super.c` registers NFSv3 client support as a version-specific module. It binds the common NFS filesystem type and superblock operations to the NFSv3 RPC version, NFSv3 client operation vector, and optional NFSv3 xattr handlers.

## Important APIs, Types, And Functions
The file defines global `struct nfs_subversion nfs_v3` with `THIS_MODULE`, `&nfs_fs_type`, `&nfs_version3`, `&nfs_v3_clientops`, and `&nfs_sops`. `init_nfs_v3()` registers it, and `exit_nfs_v3()` unregisters it. Module metadata declares GPL licensing and an NFSv3 description.

## Control Flow And Integration Points
At module load, the common NFS version registry gains the NFSv3 subversion. Mount selection can then use `nfs_version3` from `nfs3xdr.c` and `nfs_v3_clientops` from `nfs3proc.c`. `nfs3client.c` references `nfs_v3` when creating pNFS data-server clients.

## State And Persistence Behavior
The static `nfs_v3` object persists for the module lifetime. Its `owner` field participates in module reference handling through `get_nfs_version()` and `put_nfs_version()`.

## Dependencies
The module depends on common NFS filesystem registration, `nfs3_fs.h`, `nfs_version3`, `nfs_v3_clientops`, and `nfs_sops`.

## Risks And Edge Cases
Registration/unregistration must pair cleanly. Since `nfs_v3` is non-static and used by data-server setup, its symbol lifetime matters. Incorrect operation vector binding would affect every NFSv3 mount and pNFS data server.

## Test Signals
Build and load/unload NFSv3 support, mount explicit `vers=3`, use pNFS data-server paths, verify NFSv3 procedure counters, and confirm module unload is blocked while NFSv3 mounts exist.
