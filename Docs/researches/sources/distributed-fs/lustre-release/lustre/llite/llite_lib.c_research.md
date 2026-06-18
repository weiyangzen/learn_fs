# sources/distributed-fs/lustre-release/lustre/llite/llite_lib.c

## Purpose

`llite_lib.c` implements the main Lustre llite client superblock and inode support. It initializes and frees `ll_sb_info`, parses llite mount options, connects the mount to MDT and OST client devices, negotiates capabilities, creates the root inode, wires VFS operation tables, handles unmount teardown, updates inodes from Lustre metadata replies, manages directory LMV layout state, performs setattr/truncate coordination across MDT and OST/PCC state, implements statfs/project-statfs, provides common ioctls, builds metadata RPC operation descriptors, and supports parent/link lookup helpers used by user APIs.

This file is the bridge between Linux VFS lifecycle and Lustre's remote metadata/data services. It owns most mount-time and inode-time state transitions for llite.

## Important APIs, Types, And Functions

- `struct proj_sfs_cache`: per-project cached `kstatfs` entry stored in `ll_sb_info::ll_proj_sfs_htable`.
- `ll_init_sbi()` and `ll_free_sbi()`: allocate/free superblock-private state, including PCC, readahead workqueue, CL client cache, foreign symlink defaults, root squash state, feature defaults, statfs/project cache, file heat/open-cache defaults, and tunables.
- `client_common_fill_super()`: core mount connection routine. It connects to the MDT, fetches statfs and root FID, validates required server features, adapts local flags, connects to the OST/LOV stack, initializes CL state, creates the root inode, installs superblock operation tables, export operations, xattr handlers, crypto ops, sysfs links, clustered-NFS `s_dev`, and read-ahead limits.
- `ll_options()`: parses llite mount options into `ll_sbi_flags` and related values such as foreign symlink prefix, user principal, checksum selection, dummy encryption, SSK key id, flock mode, lazy statfs, user xattrs, and statfs-project behavior.
- `ll_fill_super()`, `ll_put_super()`, `client_common_put_super()`, and `ll_kill_super()`: VFS mount/unmount entry points. They process config logs, create per-instance OBD names, register debugfs, connect/disconnect devices, wait for statahead shutdown, restore clustered-NFS device numbers, clean OBD devices, free crypto policy, and purge CL env caches.
- `ll_lli_init()`, `ll_read_inode2()`, `ll_update_inode()`, `ll_clear_inode()`, `ll_delete_inode()`: inode initialization, update, final writeback/discard, and teardown.
- Directory layout helpers: `ll_iget_anon_dir()`, `ll_init_lsm_md()`, `ll_update_default_lsm_md()`, `ll_update_lsm_md()`, `ll_dir_default_lmv_inherit()`, and `ll_update_dir_depth_dmv()`.
- Attribute and truncate path: `ll_md_setattr()`, `ll_io_zero_page()`, `volatile_ref_file()`, `ll_setattr_raw()`, and `ll_setattr()`.
- Statfs APIs: `ll_statfs_internal()`, `ll_statfs_project()`, `ll_statfs()`, and `ll_obd_statfs()`.
- File attribute/ioctl helpers: `fileattr_get()`, `fileattr_set()`, `ll_fileattr_get()`, `ll_fileattr_set()`, `ll_iocontrol()`, `ll_flush_ctx()`, `ll_umount_begin()`, `ll_open_cleanup()`.
- Metadata operation helpers: `ll_prep_md_op_data()`, `ll_finish_md_op_data()`, and `ll_unlock_md_op_lsm()`.
- User data helpers: `ll_copy_user_md()`, `ll_compute_rootsquash_state()`, `ll_getparent()`, `ll_get_obd_name()`, and `ll_get_sb_uuid()`.

## Control Flow

Mount starts in `ll_fill_super()`. It allocates config state, creates `ll_sb_info` with defaults, parses mount options, sets default dentry operations, generates a per-mount UUID, derives the Lustre fsname, renames the SSK key, configures the backing device info, registers debugfs, processes the Lustre config log, resolves profile MDT/OST names, appends the per-superblock instance id, and calls `client_common_fill_super()`.

`client_common_fill_super()` first connects the metadata export with a large set of MDT feature flags. It handles MDT/fileset `-EROFS` by forcing a read-only retry, validates the root FID and required connect flags, fetches final connect data, sets VFS superblock limits, and updates client feature bits based on server support. It then connects the data export with OST feature flags and checksum/grant settings, updates aggregate connect flags, installs VFS operations, fetches root metadata, initializes CL state, constructs the root inode with `ll_iget()`, handles root security/encryption context, applies checksum settings, creates `s_root`, changes `s_dev` to a hash of the MDT UUID for clustered NFS, computes whole-file readahead limits, and creates sysfs links.

Unmount flow calls `ll_put_super()`. It ends config logs, marks matching OBD devices forced when needed, disconnects MDT/OST if mount setup completed, cleans up SSK keys and OBD devices, unregisters BDI/debugfs state, frees dummy crypto policy and `ll_sb_info`, calls common Lustre super teardown, and purges CL env caches. `ll_kill_super()` handles early kill-super behavior and waits for running statahead references before final teardown.

Inode update flow starts with a Lustre metadata reply. `ll_prep_inode()` decodes `lustre_md`, either updates an existing inode or calls `ll_iget()` for a new one, applies piggyback layout locks only when an intent lock contains layout state, updates default LMV deletion, applies foreign-file policy, and cleans up open handles if an open reply cannot be consumed. `ll_update_inode()` initializes CL file state when EA size is present, updates directory LMV state, replaces ACL cache, updates VFS inode number/generation/timestamps/mode/owner/project/link/rdev/FID/size/block fields, preserves lazy plaintext size for encrypted files without keys, and tracks HSM restore state.

Setattr flow uses `ll_setattr()` for VFS validation and encryption preparation, then `ll_setattr_raw()`. The raw path validates size against VFS and Lustre limits, sets missing ctime/mtime/atime values, drops the inode lock for regular files before the MDT RPC, always asks the MDT to authorize the change, updates local inode metadata from the reply, and then updates PCC or OST attributes for regular files. Encrypted truncates may zero the tail page through CLIO before OST setattr. Restored files may need a follow-up HSM dirty-state RPC.

Statfs flow asks MDT first, optionally asks OSTs when the MDT did not return a summed result, merges block/object/free counts, downshifts values on 32-bit kernels, and optionally clips results by project quota using cached quota-derived limits.

## State And Persistence Behavior

Persistent state is remote. Mount setup changes server-side connection state and negotiates capabilities with MDT/OST imports. Metadata mutations go through MDT RPCs; size, time, flag, and truncation effects for regular files are propagated to OSTs or PCC depending on cache state. HSM dirty flags, project inheritance, xattrs, security/encryption context names, directory layouts, and linkEA data are all server-backed.

Client-local state includes mount flags, feature negotiation results, root FID, read-ahead workqueue/cache, statfs and project-statfs caches, PCC state, foreign symlink configuration, security context xattr name, root squash match result, open and layout caches, inode ACL/xattr/LMV state, and VFS inode fields. The file explicitly changes `sb->s_dev` to a stable hash for clustered NFS and restores the original value during kill-super.

## Dependencies And Integration Points

`llite_lib.c` depends on Linux VFS, mm, statfs, uid/gid, fileattr, key, and ioctl APIs; Lustre OBD connect/statfs/info/ioctl/disconnect APIs; MGC config logs; MDC/LMV/LOV metadata and layout interfaces; CL object/page/cache APIs; LDLM layout locks; PCC; llcrypt; root squash/NID utilities; lprocfs/debugfs/sysfs; quota ioctls; linkEA parsing; HSM; and llite-local file, dir, xattr, namei, mmap, NFS, foreign, and crypto modules.

It exports `lustre_super_operations` consumers through the header and installs `lustre_export_operations` for NFS export when stack size allows. It also communicates with userspace through ioctl payloads, mount options, statfs, and copied user LOV metadata.

## Risks And Edge Cases

- Mount setup has many partial-failure labels. Resource ownership across MDT connect, OST connect, CL init, root inode creation, sysfs links, and allocated buffers must stay balanced.
- Feature negotiation can silently disable requested features such as xattr cache, ACLs, encryption, name encryption, and hybrid I/O depending on server replies.
- `ll_setattr_raw()` deliberately unlocks and later relocks regular inodes around network operations; races with truncation, DIO, HSM restore, PCC, and encrypted tail-zeroing are high-risk.
- Directory LMV updates reject non-monotonic layout versions for striped directories. Tests should cover split/merge/restripe and stale reply races.
- `ll_prep_md_op_data()` owns encrypted names, security contexts, and LMV references. Missing finish calls leak or double-free state.
- Project statfs caching can return stale quota-clipped capacity until `ll_statfs_max_age` expires.
- `ll_dirty_page_discard_warn()` cannot drop dentries synchronously because it may be called in ptlrpc/page-completion contexts, so it schedules deferred `dput()`.
- `ll_umount_begin()` force-marks exports and waits only heuristically for unmount readiness.

## Test Signals

Useful tests include successful mount/unmount, read-only retry on MDT/fileset `-EROFS`, failed mount cleanup at each connection/root/CL/sysfs step, mount option parsing/display, server capability downgrades for ACL/xattr/encryption/hybrid I/O, root inode creation for normal and fileset mounts, directory LMV inheritance and layout-version conflicts, setattr/truncate on encrypted and unencrypted files, PCC setattr paths, HSM restored-file dirty handling, volatile encrypted migration without keys, statfs merging and 32-bit downshift, project quota statfs caching, ioctls for FID/path/name/UUID/encryption/project, forced unmount, open-cleanup after failed open consumption, and `md_op_data` cleanup under encrypted filename/security context combinations.
