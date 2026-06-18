# sources/distributed-fs/ceph-client/security/landlock/fs.c

## Purpose

`fs.c` is Landlock's filesystem enforcement core. It manages inode-backed Landlock objects, adds path-beneath rules, walks filesystem hierarchies to evaluate per-layer access, mediates mount namespace changes, path operations, open/truncate/device ioctl, Unix socket path resolution, and file-owner signal scope state.

## Important APIs, Types, and Functions

Object/rule helpers include `release_inode()`, `get_inode_object()`, `landlock_append_fs_rule()`, and `find_rule()`. IOCTL helpers `is_masked_device_ioctl()` and `is_masked_device_ioctl_compat()` define device ioctl commands not restricted by `LANDLOCK_ACCESS_FS_IOCTL_DEV`. Access-check helpers include `may_refer()`, `no_more_access()`, `scope_to_request()`, `is_eacces()`, `is_access_to_paths_allowed()`, `current_check_access_path()`, `collect_domain_accesses()`, and `current_check_refer_path()`. LSM hooks cover inode free, superblock delete, mount/move/umount/remount/pivotroot, path create/remove/link/rename/truncate, Unix socket lookup, file allocation/open/truncate/ioctl/fowner/free, and `landlock_add_fs_hooks()` registers them.

## Control Flow

Adding a filesystem rule validates that non-directories only receive file-applicable rights, upgrades relative rights to absolute rights for unhandled access, obtains or creates an inode object, and inserts a rule into the ruleset tree. Normal access checks first ask whether the current or file credential has a domain handling the requested fs bits. If yes, `landlock_init_layer_masks()` creates per-layer denied masks and `is_access_to_paths_allowed()` walks from the target path up through parents and mount points, unmasking access where rules grant it. If all layers are satisfied, access is allowed; otherwise audit details are filled and `-EACCES` is returned.

Link and rename use `current_check_refer_path()`, which compares source and destination hierarchies to avoid access-right widening. It collects domain access matrices for source and destination parents, considers child access for moved/exchanged dentries, checks whether the destination is at least as restrictive, and prioritizes `-EACCES` for missing create/remove rights over `-EXDEV` for unsafe reparenting. Mount topology hooks deny mount namespace changes by any subject whose domain handles filesystem rights, because topology changes can reveal new paths. Open records the rights available at open time in the file security blob, including optional truncate and device-ioctl rights; later truncate/ioctl hooks enforce those saved rights even if the current task is different.

## State and Persistence Behavior

Inodes have weak RCU pointers to `landlock_object`; rules hold strong object references. `hook_sb_delete()` and `release_inode()` coordinate inode/object disassociation with spinlocks, RCU assignment, `iput()`, and a superblock `inode_refs` wait counter. File blobs persist `allowed_access`, audit deny masks, and fowner subject state. Rulesets/domains are immutable while enforced; access matrices are stack-temporary during checks. Audit state is updated through `landlock_log_denial()`.

## Dependencies and Integration Points

The file depends on VFS dentries, paths, mount walking, LSM hooks, file modes, ioctl command definitions, AF_UNIX socket lookup, Landlock rulesets/objects/credentials/audit, and superblock/inode/file LSM blobs declared in `fs.h`. It integrates with syscalls implemented elsewhere through `landlock_append_fs_rule()`.

## Risks and Test Signals

This file is high risk because small path-walk or lifetime changes can create sandbox escapes, false denials, inode reference leaks, or unmount hangs. Disconnected dentries, bind mounts, mount roots, `RENAME_EXCHANGE`, `O_PATH`, optional rights captured at open, file descriptors passed across domains, and device ioctl allowlists are sensitive. Test Landlock selftests for file hierarchy, refer, truncate, ioctl, Unix socket path resolution, mount operations, open-file transfer, KUnit suite `landlock_fs`, and stress tests with concurrent unmount/rule insertion.
