# Group Research: group_1423_openzfs_sources_cow_pools_openzfs_module_os_freebsd_zfs_zfs_debug_c_03b6297946ea

Scope: `Docs/research_subset_a.md`, source tree `sources/cow-pools/openzfs`.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_debug.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_debug.c

## Purpose

Implements the FreeBSD/OpenZFS in-kernel debug message buffer exposed through a raw kstat named `zfs.misc.dbgmsg`, plus low-level debug formatting helpers used by `dprintf()` and `SET_ERROR()`-style diagnostics.

## Main Data Structures

- `zfs_dbgmsg_t`
  - List node plus timestamp, allocation size, and flexible message buffer.
  - Stored in the global `zfs_dbgmsgs` list.
- Global state:
  - `zfs_dbgmsgs`: ordered list of retained debug messages.
  - `zfs_dbgmsg_size`: total allocated bytes currently retained.
  - `zfs_dbgmsgs_lock`: protects list and size.
  - `zfs_dbgmsg_maxsize`: tunable cap, default `4 << 20`.
  - `zfs_dbgmsg_kstat`: raw kstat handle.
  - `zfs_dbgmsg_enable`: module parameter advertised as enabling the debug log; this file defines it but the actual call-site gating is expected outside this file.

## Key Functions

- `zfs_dbgmsg_init()`
  - Creates the debug-message list and mutex.
  - Creates a virtual raw kstat named `zfs/dbgmsg/misc`.
  - Installs raw kstat callbacks for headers, row formatting, and cursor traversal.
- `zfs_dbgmsg_fini()`
  - Deletes the kstat if present.
  - Purges every retained message under lock.
  - Destroys the mutex.
- `__zfs_dbgmsg(char *buf)`
  - Emits DTrace probe `zfs__dbgmsg`.
  - Allocates a `zfs_dbgmsg_t`, records current time via `gethrestime_sec()`, copies the message, appends it to the list, and purges old entries until under `zfs_dbgmsg_maxsize`.
- `__dprintf(boolean_t dprint, const char *file, const char *func, int line, const char *fmt, ...)`
  - Formats `file:line:function(): message` into a fixed 1024-byte kernel allocation.
  - Strips directory prefixes from source filenames.
  - If `dprint` is true, strips one trailing newline.
  - Sends the final buffer into `__zfs_dbgmsg()`.
- `__set_error(...)`
  - When `zfs_flags & ZFS_DEBUG_SET_ERROR` is set, logs `error <errno>` through `__dprintf()`.

## Kstat Behavior

- `zfs_dbgmsg_headers()` prints `timestamp message`.
- `zfs_dbgmsg_data()` prints each retained message with its timestamp.
- `zfs_dbgmsg_addr()` advances through `zfs_dbgmsgs` using `ks_private` as cursor state.
- `zfs_dbgmsg_update()` treats a kstat write as a request to purge the whole log.

## Concurrency and Memory Notes

- All list traversal and purge operations are protected by `zfs_dbgmsgs_lock`.
- `zfs_dbgmsg_purge()` assumes the mutex is held.
- Messages are allocated with `KM_SLEEP`; logging can sleep.
- Purging subtracts each allocation’s stored `zdm_size`, avoiding recalculation.

## External Interfaces

- DTrace probe: `zfs-dbgmsg`.
- Sysctl/kstat access documented in comments as `kstat.zfs.misc.dbgmsg`.
- Module parameters:
  - `vfs.zfs.dbgmsg_enable`
  - `vfs.zfs.dbgmsg_maxsize`

## Notable Edge Cases

- If `kstat_create()` fails, debug logging still accumulates in the in-memory list, but there is no kstat export.
- `__dprintf()` truncates messages to the 1024-byte scratch buffer.
- A kstat write purges all retained entries without interpreting input.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_dir.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_dir.c

## Purpose

Implements FreeBSD ZFS directory operations and directory-related znode lifecycle helpers: name lookup, parent lookup, unlinked-set recovery, rmnode deletion, link creation/destruction, extended attribute directory creation, and sticky-directory remove permission checks.

## Lookup Path

- `zfs_match_find()`
  - Performs directory ZAP lookup.
  - Uses `zap_lookup_norm()` when normalization/case handling is enabled.
  - Uses plain `zap_lookup()` otherwise.
  - Extracts the object number from packed dirent values with `ZFS_DIRENT_OBJ()`.
- `zfs_dirent_lookup()`
  - Looks up a child entry, rejecting `.`, `..`, and `.zfs`.
  - Supports flags:
    - `ZNEW`: fail with `EEXIST` if found.
    - `ZEXISTS`: fail with `ENOENT` if absent.
    - `ZXATTR`: look up the xattr directory through `SA_ZPL_XATTR`.
  - Applies normalization and case-match policy based on `zfsvfs->z_norm` and `zfsvfs->z_case`.
  - Converts the object id to a live znode using `zfs_zget()`.
- `zfs_dd_lookup()`
  - Reads `SA_ZPL_PARENT` and returns the parent znode.
- `zfs_dirlook()`
  - Handles empty name and `.` by returning the directory itself.
  - Handles `..` through `zfs_dd_lookup()`.
  - Handles ordinary names through `zfs_dirent_lookup(..., ZEXISTS)`.
  - Enables directory prefetch on successful ordinary lookup.

## Unlinked Set and Deletion

- `zfs_unlinked_add()`
  - Adds a zero-link znode id to `zfsvfs->z_unlinkedobj`.
  - Updates dataset unlinks kstat.
- `zfs_unlinked_drain()`
  - Iterates entries in the unlinked set after crash/force-unmount recovery.
  - Validates object type, fetches znodes, locks them, forces link count to zero if necessary, and marks them `z_unlinked`.
  - Does not directly delete every object in this pass; it prepares znodes for normal inactive deletion.
- `zfs_purgedir()`
  - Deletes contents of an inactive xattr directory.
  - Assumes entries are only regular files or symlinks.
  - Returns a count of skipped/failed entries so callers can leave the directory in the unlinked set.
- `zfs_rmnode()`
  - Final znode deletion path for objects with zero links.
  - Purges xattr directories or frees file data with `dmu_free_long_range()`.
  - Finds xattr object and external ACL object.
  - Removes the znode from the unlinked set, updates kstats, deletes SA/znode state, and commits the transaction.
  - Special FreeBSD behavior: if an xattr directory exists, it is added to the unlinked set and `z_unlinked_drain_task` is enqueued to avoid recursive `zfs_zget()`/`getnewvnode()` stack growth.

## Directory Entry Encoding

- `zfs_dirent()`
  - Packs `zp->z_id`.
  - For filesystems at `ZPL_VERSION_DIRENT_TYPE` or newer, encodes file type in high bits using `IFTODT(mode) << 60`.

## Link Creation

- `zfs_link_create()`
  - Adds `name -> zp` to parent directory `dzp`.
  - Enforces `ZFS_LINK_MAX`.
  - Refuses to relink already unlinked znodes unless renaming.
  - Increments target link count for non-rename paths.
  - Adds the packed dirent to the parent ZAP.
  - Activates `SPA_FEATURE_LONGNAME` when names reach/exceed `ZAP_MAXNAMELEN`.
  - Updates target SA attributes: links, parent, flags, ctime when appropriate.
  - Updates parent directory size, link count, mtime, ctime, and flags.

## Link Destruction

- `zfs_dropname()`
  - Removes a name from the parent directory ZAP.
  - Uses normalized removal when filesystem normalization is active.
- `zfs_link_destroy()`
  - Removes a directory entry and adjusts link counts.
  - Rejects removal of non-empty directories outside rename paths.
  - If target link count drops to the directory baseline, marks it `z_unlinked`, sets links to zero, and either returns this through `unlinkedp` or adds it to the unlinked set.
  - Updates parent size/link count and timestamps.
  - Contains defensive recovery for impossible low link counts via `zfs_panic_recover()`.

## Extended Attribute Directories

- `zfs_make_xattrdir()`
  - Creates an xattr directory under a base znode.
  - Builds ACL ids, checks quota, reserves a vnode, creates a new znode, updates the parent’s `SA_ZPL_XATTR`, logs `TX_MKXATTR`, and returns the new znode.
- `zfs_get_xattrdir()`
  - Looks up an existing xattr directory.
  - Creates one when `CREATE_XATTR_DIR` is set and the filesystem is writable.
  - Returns `ENOATTR` if absent and creation was not requested.
  - Unlocks the newly created xattr vnode before returning.

## Permission Helper

- `zfs_sticky_remove_access()`
  - Implements sticky-directory removal policy.
  - Allows removal if caller owns the directory, owns the entry, can write a regular file entry, or passes `secpolicy_vnode_remove()`.
  - Bypasses checks during ZIL replay.

## Concurrency and Transactions

- Lookup and link operations assert vnode locks when not replaying.
- DMU transactions explicitly hold affected SA handles, ZAP objects, unlinked set, ACL objects, and free ranges.
- `zfs_rmnode()` coordinates with `dd_activity_lock` and broadcasts when the unlinked set becomes empty.

## Important Interactions

- Uses SA attributes for parent, xattr pointer, links, timestamps, flags.
- Uses ZAP for directory contents and unlinked set.
- Uses `zfsvfs_taskq` for deferred unlinked drain work.
- Tightly coupled with `zfs_zget()`, `zfs_znode_delete()`, `zfs_acl_ids_*()`, ZIL create logging, and dataset kstats.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_file_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_file_os.c

## Purpose

Provides the FreeBSD implementation of OpenZFS’s platform-neutral `zfs_file_*` abstraction. It adapts kernel `struct file`, vnode operations, `uio`, and FreeBSD file APIs to the interfaces used by common ZFS code.

## Open and Close

- `zfs_file_open(const char *path, int flags, int mode, zfs_file_t **fpp)`
  - Ensures process working directories are available via `pwd_ensure_dirs()`.
  - Rejects unsupported `O_EXEC` and `O_PATH`.
  - Converts POSIX-style flags to FreeBSD file flags with `FFLAGS()`.
  - Allocates a file with `falloc_noinstall()`.
  - Uses `NDINIT()` and `vn_open()` for kernel pathname open.
  - Initializes vnode file ops with `finit_vnode()` if needed.
  - Rejects non-regular files with `EACCES`.
  - Applies `O_TRUNC` via `fo_truncate()`.
- `zfs_file_close(zfs_file_t *fp)`
  - Drops the file reference with `fdrop()`.

## Read/Write

- `zfs_file_write_impl()`
  - Builds a single-segment kernel `uio` with `UIO_SYSSPACE`.
  - Requires `FWRITE`.
  - Calls `bwillwrite()` for vnode-backed files.
  - Writes through `fo_write(..., FOF_OFFSET, ...)`.
  - Updates the supplied offset by bytes actually written.
  - If no residual pointer is supplied, short writes become `EIO`.
- `zfs_file_write()`
  - Writes at `fp->f_offset` and advances `fp->f_offset` on success.
- `zfs_file_pwrite()`
  - Positional write; ignores `ashift` on FreeBSD.
- `zfs_file_read_impl()`
  - Builds a kernel `uio`, requires `FREAD`, reads through `fo_read()`, reports residual when requested, and advances the supplied offset.
- `zfs_file_read()`
  - Reads at and advances `fp->f_offset`.
- `zfs_file_pread()`
  - Positional read without changing `fp->f_offset`.

## Seek, Stat, Sync, Space Control

- `zfs_file_seek()`
  - Verifies the file ops are seekable via `DFLAG_SEEKABLE`.
  - Calls `fo_seek()` and copies the resulting offset from `td->td_uretoff.tdu_off`.
- `zfs_file_getattr()`
  - Calls `fo_stat()` with FreeBSD-version-specific signature.
  - Exposes size and mode through `zfs_file_attr_t`.
- `zfs_vop_fsync()`
  - Starts a write section, locks the vnode exclusively, calls `VOP_FSYNC(MNT_WAIT)`, unlocks, and finishes the write section.
- `zfs_file_fsync()`
  - Requires `DTYPE_VNODE`; then delegates to `zfs_vop_fsync()`.
- `zfs_file_deallocate()`
  - On newer FreeBSD, uses `fo_fspacectl(..., SPACECTL_DEALLOC, ...)`.
  - Returns `EOPNOTSUPP` on older FreeBSD.

## File Descriptor Helpers

- `zfs_file_get(int fd)`
  - Acquires a `struct file *` from a descriptor with `fget()` and `cap_no_rights`.
- `zfs_file_put(zfs_file_t *fp)`
  - Releases through `zfs_file_close()`.
- `zfs_file_off(zfs_file_t *fp)`
  - Returns `fp->f_offset`.
- `zfs_file_private(zfs_file_t *fp)`
  - Temporarily sets `curthread->td_fpop` to call `devfs_get_cdevpriv()`.
  - Restores the prior `td_fpop`.
- `zfs_file_unlink(const char *fnamep)`
  - Calls `kern_funlinkat()` with `AT_FDCWD`, `FD_NONE`, and `UIO_SYSSPACE`.

## Compatibility Notes

- Contains FreeBSD version conditionals for:
  - `NDINIT()` signature.
  - `fo_stat()` signature.
  - `vn_start_write()` flags.
  - `fo_fspacectl()` availability.
- All public functions return FreeBSD errno-style values wrapped with `SET_ERROR()` where applicable.

## Key Risks and Edge Cases

- `zfs_file_open()` closes the file if the target is not a regular vnode.
- Short write behavior depends on whether caller requests residual reporting.
- `zfs_file_private()` relies on temporarily mutating thread file-operation context; it restores it immediately after `devfs_get_cdevpriv()`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_file_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_ioctl_compat.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_ioctl_compat.c

## Purpose

Implements FreeBSD legacy ZFS ioctl compatibility when `ZFS_LEGACY_SUPPORT` is enabled. It translates older FreeBSD ZFS ioctl command numbers and legacy `zfs_cmd_legacy_t` layouts to/from current OpenZFS ioctl numbers and `zfs_cmd_t`.

## Conditional Compilation

- Entire implementation is guarded by `#ifdef ZFS_LEGACY_SUPPORT`.
- If legacy support is not enabled, this file contributes no runtime code.

## Legacy Ioctl Numbering

- `enum zfs_ioc_legacy`
  - Defines legacy command ids beginning at zero.
  - Covers pool, vdev, objset, dataset, send/receive, delegation, jail, nextboot, checkpoint, initialize, and sync-related commands.
  - `ZFS_IOC_LEGACY_NONE` is `-1` and marks unsupported/no direct mapping.

## Mapping Tables

- `zfs_ioctl_legacy_to_ozfs_[]`
  - Maps legacy ordinal request numbers to current OpenZFS `ZFS_IOC_*` values.
  - Comments document mismatches where historical FreeBSD numbering diverged from OpenZFS.
- `zfs_ioctl_ozfs_to_legacy_common_[]`
  - Maps common current OpenZFS commands back to legacy command ids.
  - Unsupported newer commands map to `ZFS_IOC_LEGACY_NONE`.
- `zfs_ioctl_ozfs_to_legacy_platform_[]`
  - Maps platform-specific commands after `ZFS_IOC_PLATFORM`.
  - Supports legacy `NEXTBOOT`, `JAIL`, and `UNJAIL`; event and bootenv commands are unsupported.

## Translation Functions

- `zfs_ioctl_legacy_to_ozfs(int request)`
  - Bounds-checks against the legacy-to-current table.
  - Returns `-1` if out of range.
  - Otherwise returns current `ZFS_IOC_*`.
- `zfs_ioctl_ozfs_to_legacy(int request)`
  - Rejects `request >= ZFS_IOC_LAST`.
  - For platform commands, subtracts `ZFS_IOC_PLATFORM + 1` and indexes the platform table.
  - For common commands, bounds-checks against the common table.
  - Returns `-1` for unmapped/out-of-range commands.

## Command Structure Conversion

- `zfs_cmd_legacy_to_ozfs(zfs_cmd_legacy_t *src, zfs_cmd_t *dst)`
  - Copies prefix fields up to `zc_objset_stats`.
  - Copies object-set stats explicitly.
  - Copies the record/field span from legacy begin record through current send object area.
  - Copies trailing fields after `zc_sendobj`, adjusted by an 8-byte layout difference.
  - Maps `zc_jailid` to `zc_zoneid`.
- `zfs_cmd_ozfs_to_legacy(zfs_cmd_t *src, zfs_cmd_legacy_t *dst)`
  - Performs the reverse structural copy.
  - Embeds current begin record into legacy `drr_u.drr_begin`.
  - Clears legacy `drr_payloadlen` and `drr_type`.
  - Copies inject/send fields.
  - Forces `zc_resumable = B_FALSE`.
  - Maps `zc_zoneid` back to `zc_jailid`.

## Important Notes

- The conversions are layout-sensitive and depend on `offsetof()` spans rather than field-by-field semantic conversion.
- The file handles ABI compatibility only; actual ioctl execution is elsewhere.
- Unsupported ioctls are represented by `-1` or `ZFS_IOC_LEGACY_NONE`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_ioctl_compat.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_ioctl_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_ioctl_os.c

## Purpose

Provides FreeBSD-specific ioctl helpers and platform ioctl registration for OpenZFS. It handles VFS hold/release glue, jail/unjail dataset ioctls, FreeBSD nextboot label writes, mount stat cache updates, and OS-specific nvlist source-size limits.

## VFS Reference Helpers

- `zfs_vfs_ref(zfsvfs_t **zfvp)`
  - Returns `ESRCH` if the pointer is null.
  - Calls FreeBSD `vfs_busy()` to hold the mount.
  - On failure, clears `*zfvp` and returns `ESRCH`.
- `zfs_vfs_held(zfsvfs_t *zfsvfs)`
  - True when `z_vfs` is non-null.
- `zfs_vfs_rele(zfsvfs_t *zfsvfs)`
  - Releases the busy mount with `vfs_unbusy()`.

## Jail Ioctls

- `zfs_ioc_jail(zfs_cmd_t *zc)`
  - Attaches dataset `zc_name` to jail/zone id `zc_zoneid` using current thread credentials.
- `zfs_ioc_unjail(zfs_cmd_t *zc)`
  - Detaches dataset `zc_name` from jail/zone id `zc_zoneid`.

## FreeBSD Nextboot Ioctl

- Input keys are defined by `zfs_keys_nextboot`:
  - `"command"` string.
  - `ZPOOL_CONFIG_POOL_GUID`.
  - `ZPOOL_CONFIG_GUID`.
- `zfs_ioc_nextboot(...)`
  - Extracts pool guid, vdev guid, and command from input nvlist.
  - Resolves pool name through `spa_by_guid()` under `spa_namespace_enter()`.
  - Opens the spa, enters vdev state lock, looks up target vdev by guid, and writes the command to label pad2 with `vdev_label_write_pad2()`.
  - Waits for synced txg before closing the spa.

## Mount Cache Update

- `zfs_ioctl_update_mount_cache(const char *dsname)`
  - Finds mounted `zfsvfs` by dataset name.
  - Calls `VFS_STATFS()` to refresh `mp->mnt_stat`.
  - Releases the VFS reference.
  - Silently ignores lookup/statfs failures.

## Nvlist Limit

- `zfs_max_nvlist_src_size_os()`
  - Returns explicit `zfs_max_nvlist_src_size` if set.
  - Otherwise defaults to one quarter of `ptob(vm_page_max_user_wired)`.

## Initialization

- `zfs_ioctl_init_os()`
  - Registers:
    - `ZFS_IOC_JAIL`
    - `ZFS_IOC_UNJAIL`
    - named ioctl `"fbsd_nextboot"` for `ZFS_IOC_NEXTBOOT`
  - Uses config security policy and no pool checks for these registrations.

## External Dependencies

- FreeBSD VFS busy/unbusy APIs.
- FreeBSD jail dataset attach/detach helpers.
- SPA namespace and vdev label writing.
- VM page wiring limit for nvlist sizing.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_ioctl_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_racct.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_racct.c

## Purpose

Accounts ZFS read/write activity into FreeBSD per-thread resource counters, optional RACCT process counters, and OpenZFS spa I/O statistics.

## Functions

- `zfs_racct_read(spa_t *spa, uint64_t size, uint64_t iops, dmu_flags_t flags)`
  - Increments current thread `ru_inblock` by `iops`.
  - When compiled with `RACCT` and `racct_enable` is true:
    - Locks `curproc`.
    - Adds `size` to `RACCT_READBPS`.
    - Adds `iops` to `RACCT_READIOPS`.
    - Unlocks `curproc`.
  - Updates pool I/O stats with `spa_iostats_read_add(spa, size, iops, flags)`.
- `zfs_racct_write(spa_t *spa, uint64_t size, uint64_t iops, dmu_flags_t flags)`
  - Increments current thread `ru_oublock` by `iops`.
  - When RACCT is active:
    - Adds `size` to `RACCT_WRITEBPS`.
    - Adds `iops` to `RACCT_WRITEIOPS`.
  - Updates pool I/O stats with `spa_iostats_write_add(spa, size, iops, flags)`.

## Conditional Behavior

- Without `RACCT`, the `size` argument is explicitly marked unused before spa stats are updated.
- Thread `rusage` and spa I/O stats are always updated.

## Concurrency

- RACCT process updates are protected by `PROC_LOCK(curproc)`.
- Spa I/O stats are delegated to the `spa_iostats_*` helpers.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_racct.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_vfsops.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_vfsops.c

## Purpose

Implements the FreeBSD VFS integration layer for ZFS. It defines ZFS mount operations, filesystem setup/teardown, property callbacks, quota handling, statfs/root/vget/export support, suspend/resume for rollback/receive, module initialization/finalization, and jail-specific ZFS parameters.

## VFS Registration and Global State

- Defines `struct vfsops zfs_vfsops` with:
  - mount, unmount, root, cached root, statfs, vget, sync, check export, file-handle-to-vnode, and quotactl hooks.
- Registers with `VFS_SET(zfs_vfsops, zfs, VFCF_DELEGADMIN | VFCF_JAIL | optional flags)`.
- Sysctls:
  - `vfs.zfs.super_owner`
  - `vfs.zfs.debug`
  - `vfs.zfs.version.acl`
  - `vfs.zfs.version.spa`
  - `vfs.zfs.version.zpl`
- Tracks mounted filesystems through `zfs_active_fs_count`.

## Temporary Property and Quota Support

- `zfs_get_temporary_prop()`
  - Reads mount-option overrides for properties such as atime, devices, exec, setuid, readonly, xattr, and nbmand.
  - Reports `"temporary"` as setpoint when a mount option overrides the dataset value.
- `zfs_getquota()`
  - Reads user/group quota and used ZAP objects.
  - Falls back to default user/group quota when no explicit quota exists.
  - Fills FreeBSD `dqblk64`.
- `zfs_quotactl()`
  - Maps FreeBSD quota commands/types to ZFS user/group quota properties.
  - Supports quota size query, quota-on as no-op, quota-off as unsupported, set quota, and get quota.
  - Uses `zfs_enter()`/`zfs_exit()` around operations.

## Sync and Readonly

- `zfs_is_readonly()`
  - Checks `VFS_RDONLY`.
- `zfs_sync()`
  - No-ops during panic and for `MNT_LAZY`.
  - For one filesystem, commits ZIL unless rebooting with suspended pool.
  - For global sync, calls `spa_sync_allpools()`.

## Property Callbacks

Registered callbacks keep `zfsvfs_t` and FreeBSD mount flags/options aligned with dataset properties:

- `atime_changed_cb()`
- `relatime_changed_cb()`
- `xattr_changed_cb()`
- `blksz_changed_cb()`
- `readonly_changed_cb()`
- `setuid_changed_cb()`
- `exec_changed_cb()`
- `nbmand_changed_cb()`
- `snapdir_changed_cb()`
- `acl_mode_changed_cb()`
- `acl_inherit_changed_cb()`
- `acl_type_changed_cb()`
- `longname_changed_cb()`

`zfs_register_callbacks()` preserves explicit mount-option overrides, registers DSL property callbacks, handles `nbmand` specially under DSL pool config lock, and restores temporary mount option state after registration.

## zfsvfs Creation and Setup

- `zfsvfs_init()`
  - Reads on-disk ZPL state into `zfsvfs_t`:
    - ZPL version, normalization, UTF-8-only, case mode, ACL type.
    - FUID and SA feature use.
    - default user/group/project quotas and object quotas.
    - root object, unlinked set, quota objects, FUID object, shares directory.
  - Sets up SA framework and optional SA upgrade callback.
  - Determines `z_use_namecache` based on normalization/case rules.
- `zfsvfs_create()`
  - Rejects overly long dataset names for FreeBSD `statfs.f_mntfromname`.
  - Owns the DMU objset with readonly forced for snapshots.
- `zfsvfs_create_impl()`
  - Initializes locks, znode list, teardown locks, FUID lock, object hold mutexes, and unlinked-drain task.
  - Calls `zfsvfs_init()`.
- `zfsvfs_setup()`
  - Rejects writes to incompatible encrypted objsets.
  - Registers callbacks.
  - On mounting:
    - Creates dataset kstats.
    - Opens ZIL.
    - Temporarily clears readonly during replay.
    - Drains unlinked set for writable filesystems.
    - Replays or destroys ZIL depending on `zil_replay_disable`.
  - Sets objset user pointer to `zfsvfs`.

## Mount Flow

- `zfs_mount()`
  - Reads dataset name from `from` option.
  - Handles delegated administration and `zfs_super_owner`.
  - Parses leading `!` as checkpoint rewind request.
  - Allows certain `.zfs` snapshot mounts with jail parameter permission.
  - Enforces privilege, delegated mount permission, mountpoint ownership/write checks, and jail dataset visibility.
  - Handles remount by re-registering callbacks under teardown write lock.
  - For root mount, imports the root pool with optional checkpoint rewind.
  - Calls `zfs_domount()`.
- `zfs_domount()`
  - Creates `zfsvfs`, attaches it to the mount, sets FreeBSD mount flags, constructs fsid, and initializes feature flags.
  - For snapshots:
    - Forces noatime and readonly.
    - Reads xattr and acltype properties.
    - Marks `z_issnap`.
    - Disables objset sync.
  - For normal filesystems, calls `zfsvfs_setup()`.
  - Enables named attributes on newer FreeBSD when compatible.
  - Sets mounted-from name and creates `.zfs` control directory for non-snapshots.
  - Increments active filesystem count on success.

## Unmount and Teardown

- `zfsvfs_teardown()`
  - Waits for zrele taskq progress.
  - Takes teardown locks.
  - Purges name cache when not unmounting.
  - Closes ZIL.
  - Finalizes znode DMU handles.
  - On unmount, marks `z_unmounted` and releases teardown locks.
  - Unregisters property callbacks, syncs dirty objsets when needed, evicts dbufs, and cancels DSL directory waiters.
- `zfs_umount()`
  - Checks unmount privilege or delegated mount permission.
  - Unmounts snapshots under `.zfs`.
  - For forced unmount, marks filesystem unmounted before `vflush(FORCECLOSE)`.
  - Flushes vnodes, cancels/drains deferred unlinked drain task, tears down `zfsvfs`, clears objset user pointer, disowns objset, destroys `.zfs`, and frees VFS state.
- `zfs_freevfs()`
  - Frees `zfsvfs` and decrements active count.

## VFS Operations

- `zfs_statfs()`
  - Reports ZFS capacity, available blocks, object counts, fs type, mount names, and max filename length.
- `zfs_root()`
  - Fetches root znode by `zfsvfs->z_root`, then locks and returns the vnode.
- `zfs_vget()`
  - Converts inode/object number to vnode.
  - Refuses virtual `.zfs` entries and shares directory with `EOPNOTSUPP` for NFS fallback.
  - Rejects unlinked znodes.
  - Sets named-attribute vnode flags on newer FreeBSD.
- `zfs_checkexp()`
  - Delegates export checks to parent filesystem mount for snapshots.
- `zfs_fhtovp()`
  - Converts short/long ZFS file handles into vnodes.
  - Handles snapshot objset ids in long fids through `zfsctl_lookup_objset()`.
  - Handles `.zfs` and snapshot directory virtual objects through control-directory lookup.
  - Validates object generation against file-handle generation.
  - Creates vnode VM object before returning.

## Suspend, Resume, and End

- `zfs_suspend_fs()`
  - Blocks VOPs and tears down `z_os` for rollback/receive style operations, leaving teardown locks held on success.
- `zfs_resume_fs(zfsvfs_t *zfsvfs, dsl_dataset_t *ds)`
  - Reacquires objset from the owned dataset.
  - Reinitializes zfsvfs and setup state.
  - Reopens ZIL and callbacks.
  - Attempts `zfs_rezget()` on all active znodes.
  - Releases teardown locks.
  - Forces unmount if setup fails.
- `zfs_end_fs()`
  - Releases teardown locks and force-unmounts a suspended filesystem.
  - Marks it unmounted.

## Version and Default Quota Mutation

- `zfs_set_version()`
  - Validates requested ZPL version.
  - Updates `ZPL_VERSION_STR`.
  - Creates SA master object and registers SA upgrade callback when upgrading to SA support.
  - Logs history and updates in-memory version/feature flags.
- `zfs_set_default_quota()`
  - Updates or removes default quota properties in `MASTER_NODE_OBJ`.
  - Updates corresponding cached `zfsvfs` default quota field.

## Module Lifecycle and ARC/Vnode Pressure

- `zfs_init()`
  - Prints filesystem version.
  - Initializes `.zfs`, znode cache/vnode ops, i386 vnode tuning, DMU objset type handler, `zfsvfs_taskq`, VNLRU marker/lock, and ARC prune callback.
- `zfs_fini()`
  - Removes prune callback, frees marker, destroys lock/taskq, finalizes `.zfs` and znodes, and restores vnode tuning.
- `zfs_busy()`
  - Reports whether any ZFS filesystems remain active.
- `zfs_prune_task()`
  - Called by ARC pruning to free ZFS vnodes through FreeBSD VNLRU.

## Jail Parameters

- Defines per-prison `struct zfs_jailparam` with `mount_snapshot`.
- Provides OSD jail methods:
  - create, get, set, check, destroy.
- Supports `zfs=inherit/new` and `zfs.mount_snapshot`.
- Prevents child jails from gaining more snapshot-mount permission than parent.
- Registers/deregisters jail OSD slot through `SYSINIT`/`SYSUNINIT`.

## Rename/Mount Name Support

- `zfsvfs_update_fromname()`
  - Walks FreeBSD mount list and updates `f_mntfromname` for renamed datasets and descendants/snapshots.

## Important Cross-File Interactions

- Calls `zfs_unlinked_drain()` from `zfs_dir.c`.
- Creates and destroys `.zfs` control directory via `zfsctl_*`.
- Depends on znode initialization and lookup functions from FreeBSD ZFS vnode/znode layers.
- Coordinates with DSL/DMU/ZIL/SPA layers for objset ownership, property callbacks, replay, sync, and pool state.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_vfsops.c -->