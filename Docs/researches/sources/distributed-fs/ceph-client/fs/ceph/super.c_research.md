# sources/distributed-fs/ceph-client/fs/ceph/super.c

## Purpose
`super.c` implements CephFS filesystem registration, mount option parsing, superblock setup/sharing, client creation/destruction, module cache lifecycle, statfs/sync behavior, forced unmount/reconnect, remount handling, and module parameters.

## Important APIs, Types, And Functions
Key functions include `ceph_init_fs_context()`, `ceph_parse_mount_param()`, `ceph_get_tree()`, `ceph_set_super()`, `ceph_compare_super()`, `ceph_real_mount()`, `ceph_kill_sb()`, `ceph_umount_begin()`, `ceph_force_reconnect()`, `init_ceph()`, and `exit_ceph()`. It defines super operations, fs context operations, `ceph_fs_type`, global kmem caches, and the `disable_send_metrics`/mount syntax/idmap module parameters.

## Control Flow
Mount starts with fs-context allocation and option parsing, including old and new source syntaxes. `ceph_get_tree()` creates a `ceph_fs_client`, initializes the MDS client, finds or creates a shared superblock, sets up BDI parameters, opens a cluster session, registers fscache/debugfs, and opens the root dentry. Unmount pre-flushes MDS state, syncs filesystems, waits for dirty folios and stopping blockers, kills the anon super, unregisters fscache/debugfs, and destroys the client.

## State, Persistence, And Dependencies
The file owns process-wide CephFS cache objects and a list of clients used to wake metric reporting when module parameters change. Per-mount state lives in `struct ceph_fs_client` and `struct ceph_mount_options`. Persistent storage is remote Ceph cluster state; local state is kernel memory and superblock structures.

## Integration Points
It ties VFS fs_context/super_operations, libceph monitor/osd clients, MDS client, fscache, fscrypt, debugfs, quota statfs, xattrs, export ops, and workqueues together. `extra_mon_dispatch()` routes MDSMAP/FSMAP messages to the MDS client.

## Risks
Risks include option compatibility between old/new mount syntax, superblock sharing with subtly different options, teardown ordering around dirty folios and MDS blockers, mount failure cleanup, blocklisted-client recovery, and module parameter changes racing with live clients.

## Test Signals
Test old/new mount sources, remountable options, no-MDS cluster behavior, shared versus `noshare` mounts, fscache/fscrypt configs, statfs with quotas and noquotadf, forced unmount, blocklist clean recovery, module load/unload, and fault injection in cache/client setup.
