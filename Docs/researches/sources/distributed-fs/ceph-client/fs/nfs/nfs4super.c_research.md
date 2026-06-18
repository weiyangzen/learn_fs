# sources/distributed-fs/ceph-client/fs/nfs/nfs4super.c

## Purpose
`nfs4super.c` wires NFSv4 into the Linux VFS/NFS subversion framework. It defines NFSv4 superblock operations, module initialization and teardown, NFSv4 mount/referral traversal through the server pseudo-root, referral loop protection, and inode eviction cleanup for NFSv4-specific state.

## Important APIs and Functions
- `nfs_v4`: `struct nfs_subversion` registration binding NFSv4 RPC version, client ops, super ops, filesystem type, and xattr handlers.
- `nfs4_write_inode()`: delegates normal NFS inode writeback, then commits pNFS layouts on synchronous writeback.
- `nfs4_evict_inode()`: final inode cleanup for delegations, pNFS layouts, generic NFS inode state, and NFSv4 xattr cache.
- `nfs4_try_get_tree()`: creates an NFSv4 server and mounts the requested export via the pseudo-root.
- `nfs4_get_referral_tree()`: creates a referral server and mounts the referred export.
- `init_nfs_v4()` / `exit_nfs_v4()`: module lifecycle for DNS resolver, idmapper, xattr cache, sysctl, server-side-copy ops, pNFS DS unload, and subversion registration.

## Control Flow
Mounting duplicates the caller's `fs_context`, installs the created `nfs_server` into the duplicate root context, copies fscache uniqueness when present, synthesizes a root source string (`host:/` or `[ipv6]:/`), mounts the server root with `fc_mount()`, then uses `mount_subtree()` to walk to the requested export path. Referral protection tracks nesting per current task in a global list and rejects traversal beyond `NFS_MAX_NESTED_REFERRALS`.

Inode eviction first truncates and clears inode pages, then returns delegations, returns and destroys pNFS layout state, runs generic NFS inode cleanup, and zaps the NFSv4 xattr cache. Module initialization is staged with unwind labels so partial failures destroy only initialized subsystems.

## State and Persistence
The file owns registration state for the NFSv4 subversion and sysctl/idmap/DNS/pNFS-xattr subsystems. Referral loop state is a transient global list protected by `nfs_referral_count_list_lock` and keyed by `current`. Superblock and inode state persist only as VFS/NFS in-memory objects.

## Dependencies and Integration Points
This code integrates VFS mount APIs, NFS fs_context parsing, NFSv4 server creation, DNS resolution, idmapping, NFSv4 sysctls, pNFS, NFSv4.2 xattrs and server-side copy, and the generic NFS superblock helpers. It exports the NFSv4 subversion to the generic NFS mount path via `register_nfs_version()`.

## Risks
Mount error paths must drop duplicated contexts, root mounts, and server references correctly. Referral loop accounting is per-task and must always be unwound after `mount_subtree()`. Eviction ordering is important: delegations and layouts must be returned before generic inode state is discarded. Initialization and exit ordering must remain symmetric, especially around optional `CONFIG_NFS_V4_2` features.

## Test Signals
Mount tests should cover IPv4 and IPv6 source formatting, normal exports, referral traversal, nested referral loop rejection, fscache options, and failure injection in server creation or root mount. Teardown tests should watch delegation return, layout return/destroy, xattr cache cleanup, and clean module unload with optional NFSv4.2 features.
