# Group Research: group_820_linux_sources_os_linux_linux_fs_orangefs_orangefs_utils_c_sources_os_dca30ac312aa

Scope checked against `Docs/research_subset_a.md`: all files are within `sources/os/linux/linux`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-utils.c -->
# File Research: sources/os/linux/linux/fs/orangefs/orangefs-utils.c

## Role

OrangeFS utility glue between VFS inode state and OrangeFS userspace protocol state. It extracts filesystem IDs from queued operations, translates OrangeFS attributes and errors into Linux VFS forms, performs getattr/setattr upcalls, and detects stale cached inodes.

## Main Responsibilities

- `fsid_of_op()` maps each `ORANGEFS_VFS_OP_*` upcall type to the correct embedded `fs_id`, returning `ORANGEFS_FS_ID_NULL` for unknown or null operations.
- Permission and flag translation is centralized in `orangefs_inode_flags()`, `orangefs_inode_perms()`, `orangefs_inode_type()`, and `ORANGEFS_util_translate_mode()`.
- `copy_attributes_from_inode()` builds an `ORANGEFS_sys_attr_s` setattr mask from `ORANGEFS_I(inode)->attr_valid`, intentionally excluding size changes.
- `orangefs_inode_getattr()` implements cached getattr refresh, full/new inode initialization, stale-type checks, symlink target caching, uid/gid/time/mode setup, and timeout refresh.
- `orangefs_inode_setattr()` submits pending attribute updates via `ORANGEFS_VFS_OP_SETATTR`, clears the dirty attr mask, and marks non-root inodes bad on writeback failure.
- `orangefs_normalize_to_errno()` converts OrangeFS encoded negative status values into Linux `-errno`.

## Important Control Flow

`orangefs_inode_getattr()` first checks cached attributes under `i_lock`. If local attribute changes are pending, it forces `write_inode_now()` and retries. It skips server refresh when cached data is still valid or dirty pages could make size stale. When it does issue a GETATTR upcall, it may omit size unless full attributes are requested. Existing inodes are checked with `orangefs_inode_is_stale()` before applying returned data.

`orangefs_inode_is_stale()` treats type changes, unknown object types, and symlink target changes as stale and calls `orangefs_make_bad_inode()`. The root inode is protected from `make_bad_inode()` because losing root operations after userspace client restart would be fatal to the mount.

## Data and ABI Notes

The error mapping table mirrors OrangeFS/PVFS userspace errno ordering. Protocol errors with `ORANGEFS_NON_ERRNO_ERROR_BIT` are mostly collapsed to `-EINVAL`, except `ORANGEFS_ECANCEL`, which becomes `-ETIMEDOUT`.

## Dependencies

Uses operation allocation/service helpers from OrangeFS core, VFS inode state helpers, OrangeFS private inode data, and protocol constants from `protocol.h`.

## Research Notes

This file is the main consistency point for OrangeFS inode metadata. Any change to protocol object types, attr masks, error encoding, or pending attribute semantics must be reflected here.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/protocol.h -->
# File Research: sources/os/linux/linux/fs/orangefs/protocol.h

## Role

Defines the kernel-side OrangeFS protocol ABI constants, object identifiers, attribute structures, ioctl command numbers, xattr limits, error encoding bits, and debug macros used by the OrangeFS client module.

## Main Contents

- `struct orangefs_khandle` is a 16-byte aligned handle. Comments explain compatibility with older 64-bit and newer 128-bit handle formats.
- `struct orangefs_object_kref` combines a kernel handle and filesystem ID.
- Inline handle helpers compare, export, and import fixed 16-byte handles.
- Error encoding constants define OrangeFS error bit layout and protocol-specific errors such as `ORANGEFS_ECANCEL`.
- Permission, inode flag, iteration token, attribute mask, xattr size, and name-size constants define the protocol limits used by upcall/downcall structures.
- `enum ORANGEFS_io_type` and `enum orangefs_ds_type` describe I/O direction and OrangeFS object kinds.
- `struct ORANGEFS_keyval_pair` and `struct ORANGEFS_sys_attr_s` define xattr and file metadata payloads.
- Device ioctl command numbers define the `/dev/orangefs` userspace interface.
- `struct ORANGEFS_dev_map_desc` is explicitly documented as needing 32-bit compatibility handling.
- `gossip_debug` and `gossip_err` provide lightweight debug/error logging wrappers.

## ABI and Compatibility Notes

The file uses fixed-width integer types and padding-oriented comments because the OrangeFS kernel module communicates with a userspace client process. Several comments explicitly warn about 32-bit userspace on 64-bit kernels and retaining field sizes or alignment.

## Dependencies

Includes Linux kernel, type, spinlock, slab, and ioctl headers, plus `orangefs-debug.h`.

## Research Notes

This is a protocol boundary file. Seemingly simple changes to field order, sizes, limits, or ioctl encodings would affect userspace client compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/protocol.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/super.c -->
# File Research: sources/os/linux/linux/fs/orangefs/super.c

## Role

Implements OrangeFS superblock lifecycle, mount context parsing, inode cache management, statfs, remount support, export file handles, and teardown.

## Main Responsibilities

- Defines global `orangefs_superblocks` list and lock for active OrangeFS mounts.
- Parses mount flags `acl`, `intr`, and `local_lock` via `fs_context`.
- Allocates private OrangeFS inodes from `orangefs_inode_cache`, initializing ref handles, fs IDs, failed-block state, and symlink target storage.
- Frees per-inode cached xattrs before returning inodes to the slab cache.
- `orangefs_statfs()` issues `ORANGEFS_VFS_OP_STATFS` and fills `kstatfs`.
- `orangefs_remount()` re-sends mount information to userspace client-core with priority/no-mutex semantics, then queries feature bits for userspace version `>= 20906`.
- Export support encodes OrangeFS handles and fs IDs into file handles.
- `orangefs_get_tree()` performs the userspace mount upcall, allocates an anonymous superblock, fills root inode/dentry, registers the superblock in the global list, and queries features.
- `orangefs_kill_sb()` sends the unmount upcall, removes the superblock from the list, synchronizes with remount-all, and frees private superblock data.

## Important Control Flow

Mount setup starts with `orangefs_init_fs_context()`, which allocates `orangefs_sb_info_s` and installs `orangefs_context_ops`. `orangefs_get_tree()` requires `fc->source`, sends `ORANGEFS_VFS_OP_FS_MOUNT`, validates non-null `fs_id`, creates an anonymous superblock, calls `orangefs_fill_sb()`, and only then links the mount into `orangefs_superblocks`.

Failure paths are careful: if `sget_fc()` succeeds but fill fails, `deactivate_locked_super()` lets `orangefs_kill_sb()` perform the unmount request, with `no_list` set because the superblock was never added to the global list.

## Data and ABI Notes

`orangefs_inode_cache_initialize()` uses `kmem_cache_create_usercopy()` and marks only the `link_target` field as usercopy-safe.

## Dependencies

Uses OrangeFS operation service helpers, root inode lookup (`orangefs_iget()`), xattr handlers, dentry ops, export ops, and the shared request mutex.

## Research Notes

This file is the mount/session authority for OrangeFS. It coordinates kernel superblocks with the userspace client’s dynamic mount table and is sensitive to restart/remount ordering.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/symlink.c -->
# File Research: sources/os/linux/linux/fs/orangefs/symlink.c

## Role

Defines OrangeFS symlink inode operations.

## Main Contents

`orangefs_symlink_inode_operations` wires symlink VFS methods to:

- `simple_get_link`
- `orangefs_setattr`
- `orangefs_getattr`
- `orangefs_listxattr`
- `orangefs_permission`
- `orangefs_update_time`

## Dependencies

Relies on symlink target caching and `inode->i_link` initialization performed during OrangeFS getattr/new inode handling.

## Research Notes

This file is intentionally minimal. Symlink behavior is mostly implemented in shared inode, permission, xattr, and getattr paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/upcall.h -->
# File Research: sources/os/linux/linux/fs/orangefs/upcall.h

## Role

Defines all OrangeFS kernel-to-userspace upcall request payload structures and the top-level `orangefs_upcall_s` union.

## Main Contents

The file declares request structures for:

- File I/O, lookup, create, symlink, getattr, setattr, remove, mkdir.
- Readdir and readdirplus.
- Rename, statfs, truncate, readahead cache flush.
- Filesystem mount and unmount.
- Xattr get/set/list/remove.
- Operation cancel and fsync.
- Parameter get/set requests, performance count requests, fs-key requests, and feature negotiation.

`struct orangefs_upcall_s` carries operation type, uid/gid, pid/tgid, retained trailer fields for compatibility, and a tagged request union.

## ABI and Compatibility Notes

The header is explicitly “sanitized” for 32/64-bit client-core interaction. Many structures include padding fields and use fixed-width types to preserve layout for userspace communication.

## Dependencies

Depends on protocol-level types such as `orangefs_object_kref`, `ORANGEFS_sys_attr_s`, `ORANGEFS_keyval_pair`, and OrangeFS constants.

## Research Notes

This is a strict ABI surface. Adding a request type or changing request layout requires matching userspace client support and downcall handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/upcall.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/waitqueue.c -->
# File Research: sources/os/linux/linux/fs/orangefs/waitqueue.c

## Role

Implements OrangeFS in-kernel operation queuing, waiting, timeout/retry behavior, interruption cleanup, and cancellation handoff to userspace client-core.

## Main Responsibilities

- `purge_waiting_ops()` marks queued operations purged when the userspace device is closing.
- `service_operation()` queues an operation on `orangefs_request_list`, wakes client-core, waits for a matching downcall, normalizes status to Linux errno, and retries purged operations when allowed.
- Supports priority operations for remount and `ORANGEFS_OP_NO_MUTEX` when request mutex is already held.
- Uses interruptible, killable, or I/O completion waits depending on flags.
- `orangefs_cancel_op_in_progress()` rewrites an in-progress I/O op into an `ORANGEFS_VFS_OP_CANCEL` request when cancellation is possible.
- `orangefs_clean_up_interrupted_operation()` marks interrupted operations as given up and removes them from the request list or in-progress hash table.
- `wait_for_matching_downcall()` translates completion, signal, purge, and timeout outcomes into success, `-EINTR`, `-EAGAIN`, `-EIO`, or `-ETIMEDOUT`.

## Important Control Flow

`service_operation()` fills pid/tgid, optionally takes `orangefs_request_mutex`, queues the op under list and op locks, wakes the daemon, and releases the mutex before waiting. If daemon service is unavailable, it uses a finite timeout except for unmount operations.

On success, the op lock is released and `downcall.status` is normalized. On failure, cleanup removes the op from whichever queue owns it and may retry if the op was purged and does not use shared memory.

## Dependencies

Uses OrangeFS global request list, in-progress hash, daemon service state, operation state bits, completions, and debug helpers.

## Research Notes

This file is the core concurrency bridge between synchronous VFS callers and asynchronous userspace servicing. Lock ordering and op-state transitions are the key invariants.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/waitqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/xattr.c -->
# File Research: sources/os/linux/linux/fs/orangefs/xattr.c

## Role

Implements OrangeFS extended attribute VFS operations, including get/set/remove/list and a small per-inode xattr cache.

## Main Responsibilities

- Filters reserved `system.pvfs2.*` keys from `listxattr()` output.
- Converts Linux `XATTR_CREATE` / `XATTR_REPLACE` flags to OrangeFS protocol flags.
- Uses a 16-bucket simple hash over xattr names for `orangefs_cached_xattr`.
- `orangefs_inode_getxattr()` rejects symlinks, checks name length, consults the cache, issues `ORANGEFS_VFS_OP_GETXATTR`, handles negative caching for missing keys, and copies values to caller buffers.
- `orangefs_inode_setxattr()` validates sizes, treats null zero-size values as remove, issues `ORANGEFS_VFS_OP_SETXATTR`, and invalidates the cached key.
- `orangefs_inode_removexattr()` issues `ORANGEFS_VFS_OP_REMOVEXATTR`, maps missing-key behavior according to replace semantics, and invalidates cache.
- `orangefs_listxattr()` iterates server-side xattr pages using OrangeFS tokens and copies only visible whole keys into the caller buffer.
- Installs a default xattr handler with empty prefix, so handler callbacks receive full names.

## Locking and Caching

All xattr operations use `ORANGEFS_I(inode)->xattr_sem`. Reads take the semaphore shared; set/remove take it exclusive. Positive cache entries are short-lived; missing keys are cached as `length == -1`.

## Edge Cases

`listxattr(size == 0)` returns an upper bound based on returned key count times `ORANGEFS_MAX_XATTR_NAMELEN`, not an exact filtered size. Returned list counts and key lengths are range-checked to guard impossible userspace/server responses.

## Dependencies

Uses OrangeFS upcalls, inode private data, VFS xattr APIs, POSIX ACL xattr names, and OrangeFS xattr protocol limits.

## Research Notes

This file hides OrangeFS-private metadata from generic xattr listing while still allowing direct operations through the full-name handler path.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/overlayfs/Kconfig

## Role

Defines Linux kernel configuration options for OverlayFS and its optional features.

## Main Options

- `OVERLAY_FS`: tristate core overlay filesystem support; selects `FS_STACK` and `EXPORTFS`.
- `OVERLAY_FS_REDIRECT_DIR`: enables redirect directory support by default.
- `OVERLAY_FS_REDIRECT_ALWAYS_FOLLOW`: follows redirects even when redirect support is disabled, defaulting to `y` for compatibility.
- `OVERLAY_FS_INDEX`: enables inode index by default to preserve lower hardlink identity across copy-up.
- `OVERLAY_FS_NFS_EXPORT`: enables NFS export support by default; depends on index and excludes metacopy.
- `OVERLAY_FS_XINO_AUTO`: enables automatic inode-number mapping on 64-bit systems.
- `OVERLAY_FS_METACOPY`: enables metadata-only copy-up by default and selects redirect-dir support.
- `OVERLAY_FS_DEBUG`: enables extra debug checks.

## Compatibility Notes

Several options warn that on-disk metadata features such as redirects, index, NFS export index, and metacopy are not backward compatible with kernels that do not understand them.

## Dependencies

These config choices feed mount defaults and compile-time feature availability across OverlayFS source files.

## Research Notes

The file documents the operational tradeoffs of feature defaults: compatibility and performance versus stronger identity/export semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/Makefile -->
# File Research: sources/os/linux/linux/fs/overlayfs/Makefile

## Role

Build definition for the OverlayFS kernel object.

## Main Contents

`obj-$(CONFIG_OVERLAY_FS) += overlay.o` builds the filesystem when enabled. `overlay-objs` links these implementation units:

`super.o`, `namei.o`, `util.o`, `inode.o`, `file.o`, `dir.o`, `readdir.o`, `copy_up.o`, `export.o`, `params.o`, and `xattrs.o`.

## Research Notes

The files in this group cover major object members of the combined `overlay.o`: namespace mutation, copy-up, export, file operations, and inode operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/copy_up.c -->
# File Research: sources/os/linux/linux/fs/overlayfs/copy_up.c

## Role

Implements OverlayFS copy-up: creating an upper object from a lower object when write, metadata update, indexing, metacopy, or export semantics require it.

## Main Responsibilities

- Provides obsolete `check_copy_up` module parameter compatibility.
- Copies xattrs and ACLs from lower to upper while ignoring OverlayFS private xattrs and respecting LSM `security_inode_copy_up_xattr()`.
- Copies file attributes, storing immutable/append-only protection in OverlayFS xattrs when needed.
- `ovl_copy_up_file()` tries `vfs_clone_file_range()` first, then falls back to chunked `do_splice_direct()` copying with `SEEK_DATA` sparse-hole optimization.
- Sets size, mode, ownership, timestamps, origin file handles, metacopy xattrs, and optional metadata fsync.
- Encodes lower/upper file handles for origin and index metadata.
- Creates index entries for copied-up directories and links indexed non-directories through index paths.
- Supports two creation strategies: workdir temporary object plus rename, or `O_TMPFILE` plus link.
- Implements metadata-only copy-up and later data copy-up for metacopy files.
- Public wrappers are `ovl_maybe_copy_up()`, `ovl_copy_up_with_data()`, and `ovl_copy_up()`.

## Important Control Flow

`ovl_copy_up_flags()` verifies lower data, climbs to the highest ancestor needing copy-up, and calls `ovl_copy_up_one()` under overlay credentials. `ovl_copy_up_one()` gathers lower stat data, decides whether metadata fsync and metacopy are needed, handles symlink targets, then serializes with `ovl_copy_up_start()`.

`ovl_do_copy_up()` decides whether indexing is required, prepares origin file handles, chooses destination directory/name, marks parent directories impure when needed, then dispatches to tmpfile or workdir copy-up. After success, it updates inode flags such as `OVL_INDEX`, `OVL_UPPERDATA`, digest flags, whiteouts, and dentry revalidation state.

## Data and Security Notes

Credential override uses `security_inode_copy_up()` so LSMs can provide copy-up credentials. Metacopy with required verity falls back to full copy if lower data lacks active fs-verity.

## Dependencies

Deeply tied to `overlayfs.h` helpers, xattr wrappers, indexdir/workdir management, file handle encoding, VFS copy/clone/splice APIs, fs-verity, and overlay inode flags.

## Research Notes

This is one of OverlayFS’s central correctness files. It preserves identity, metadata, sparse data, security labels, and copy-up atomicity while avoiding problematic lock ordering in nested overlays.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/copy_up.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/dir.c -->
# File Research: sources/os/linux/linux/fs/overlayfs/dir.c

## Role

Implements OverlayFS directory inode operations and upper-layer namespace mutations: create, link, unlink, rmdir, rename, tmpfile, whiteouts, redirects, and opaque directories.

## Main Responsibilities

- Generates temporary workdir names and cleans up temporary objects.
- Manages reusable whiteout inode creation/linking, with fallback when whiteout sharing hits link limits or errors.
- Creates real upper/workdir objects for regular files, directories, special files, symlinks, and hardlinks.
- Marks directories opaque with `OVL_XATTR_OPAQUE`.
- Instantiates overlay dentries/inodes after upper creation or hardlink creation.
- Handles creation over existing upper whiteouts with rename/exchange and ACL restoration.
- Overrides creator credentials so underlying filesystems initialize new inode ownership as the overlay caller expects.
- Implements `create`, `mkdir`, `mknod`, `symlink`, `link`, `unlink`, `rmdir`, `rename`, and `tmpfile`.
- Maintains overlay nlink accounting around hardlink/removal/rename operations.
- Implements redirect xattr creation for renamed merge/lower objects.
- Uses whiteouts to hide lower objects on remove and rename-over.

## Important Control Flow

Creation first copies up the parent, obtains write access, preallocates an overlay inode, initializes owner/mode, then creates or links an upper object under overlay credentials. Creation over whiteout uses a workdir temp object and rename/exchange so the whiteout is replaced atomically.

Removal checks lower presence and directory emptiness, copies up parent, starts nlink accounting, then either removes pure upper entries or replaces lower-visible entries with whiteouts.

Rename starts by validating flags and whether objects can be moved without copying directory trees. It copies up source and parents, possibly copies target for exchange, handles whiteout/overwrite flags, sets redirects or opaque xattrs when required, performs the upper rename, cleans exchanged whiteouts, and updates ctime/nlink state.

## Edge Cases

- Overlay creation of a char-device whiteout is rejected.
- Casefold inheritance for newly created dirs is checked against overlay configuration.
- Directories that become empty may be replaced with opaque temp dirs before cleanup.
- Absolute redirects are used when same-directory relative redirects are insufficient, especially for lower hardlinks.

## Dependencies

Uses VFS rename/create helpers, overlay workdir/upperdir helpers, xattrs, ACL helpers, credential override classes, backing tmpfile APIs, and copy-up/nlink utilities.

## Research Notes

This file is the namespace mutation core of OverlayFS. Whiteout, redirect, opaque, impure, and nlink metadata are all maintained here to make upper-layer changes represent union semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/export.c -->
# File Research: sources/os/linux/linux/fs/overlayfs/export.c

## Role

Implements OverlayFS exportfs/NFS file handle encoding and decoding.

## Main Responsibilities

- Decides whether to encode upper or lower/origin file handles.
- Copies up connectable ancestors before encoding lower directory handles when needed for later decode.
- Encodes non-connectable file handles only; parent/connectable file handles are rejected.
- Obtains overlay dentries from real upper/lower dentries, origin file handles, and index entries.
- Resolves decoded lower handles through inode cache, index dir, origin verification, and connected path lookup.
- Supports legacy `OVL_FILEID_V0` by realigning unaligned on-wire inner file handles.
- Exposes full `ovl_export_operations` for NFS export and encode-only `ovl_export_fid_operations` when handles need not be decodable.

## Important Control Flow

`ovl_check_encode_origin()` selects the file handle identity. Pure upper and non-indexed upper objects generally encode upper handles. Indexed upper and non-upper objects encode lower handles. For decodable directory handles, `ovl_connect_layer()` may copy up an ancestor to ensure later reconstruction can find a connected overlay path.

Decode flows split by `OVL_FH_FLAG_PATH_UPPER`. Upper handles decode through the upper mount and `ovl_get_dentry()`. Lower handles decode by checking origin file handles, consulting cached overlay inodes, looking up index entries, verifying origin consistency, and then obtaining connected or disconnected overlay dentries as appropriate.

## Lookup Strategy

`ovl_lookup_real()` walks from a known connected overlay ancestor toward the target real dentry. It uses name snapshots to avoid racing real dentry renames and restarts from ancestors on `-ECHILD` races.

## Limitations

`fh_to_parent`, `get_name`, and `get_parent` are effectively unsupported for connectable file handles; the code warns to use `no_subtree_check`.

## Dependencies

Relies on origin/index xattrs, lower layer descriptors, exportfs handle encoding/decoding, dcache alias lookup, and OverlayFS copy-up/index helpers.

## Research Notes

This file encodes the complex relationship between union dentries and persistent NFS handles. Index and redirect correctness are essential for stable decode.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/file.c -->
# File Research: sources/os/linux/linux/fs/overlayfs/file.c

## Role

Implements OverlayFS regular file operations by forwarding I/O to the current real backing file while preserving overlay copy-up semantics.

## Main Responsibilities

- Opens real backing files with overlay credentials after checking real inode permissions.
- Stores per-open state in `struct ovl_file`, including the initially opened real file and an optional lazily opened upper file.
- `ovl_real_file_path()` switches from lower to upper file after copy-up or for metacopy fsync paths and synchronizes changed open flags.
- `ovl_open()` verifies lower data, performs copy-up if open flags require it, strips creation/truncate-only flags, opens the real data path, and stores private data.
- Forwards `llseek`, `read_iter`, `write_iter`, `splice_read`, `splice_write`, `fsync`, `mmap`, `fallocate`, `fadvise`, `copy_file_range`, `remap_file_range`, `flush`, and lease setup.
- Updates overlay inode attributes after writes, fallocate, copy, clone, and dedupe operations.
- Handles O_DIRECT flag validation and O_APPEND immutability restrictions in `ovl_change_flags()`.

## Important Control Flow

Reads resolve the current real data file and call `backing_file_read_iter()` with overlay credentials and an access callback. Writes lock the overlay inode, refresh attributes, resolve the real file, optionally mask sync flags depending on overlay sync policy, and call `backing_file_write_iter()`.

`ovl_fsync()` avoids syncing lower files to prevent read-only filesystem errors. It only syncs upper paths when the overlay sync policy requires it and the object has upper data.

`ovl_remap_file_range()` permits clone/copy through real files, but refuses dedupe unless both input and output are already upper, because dedupe-triggered copy-up would defeat deduplication semantics.

## Dependencies

Uses `backing_file_*` helpers, overlay credentials, copy-up path selection, realdata verification, and VFS file-range APIs.

## Research Notes

This file is the open-file indirection layer. Its key invariant is that an overlay file descriptor continues to work correctly even if the dentry’s data source changes from lower/metacopy to upper after copy-up.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/inode.c -->
# File Research: sources/os/linux/linux/fs/overlayfs/inode.c

## Role

Implements OverlayFS inode operations, stat/inode number mapping, permission checks, ACL handling, file attributes, inode allocation/lookup, nlink metadata, and operation tables.

## Main Responsibilities

- `ovl_setattr()` prepares VFS attribute changes, chooses metadata-only or full-data copy-up for truncation, clears `ATTR_FILE`/`ATTR_OPEN`, applies changes to upper, and copies attributes back.
- `ovl_getattr()` gathers real stats, maps device/inode numbers through samefs/xino/fsid rules, handles metacopy block counts, forces merged directory nlink to 1, and reports overlay nlink for indexed inodes.
- `ovl_permission()` checks overlay inode permissions with caller credentials and real inode permissions with mounter credentials; write access to lower regular files is converted to read permission for future copy-up.
- Symlink, fiemap, update-time, ACL, and fileattr operations delegate to real paths with overlay credential handling.
- POSIX ACL code clones and remaps ACL entries for idmapped lower/upper mounts.
- Fileattr operations use a temporary file open for LSM ioctl checks, preserve immutable/append-only via OverlayFS protection xattrs, and merge protection flags into reported attributes.
- Defines inode operation tables for files, symlinks, special files, and address-space operations.
- Annotates inode locks for nested OverlayFS lockdep stack depths.
- Maps inode numbers using samefs, xino high bits, or non-persistent overlay inode numbers.
- Maintains indexed nlink xattr format with `U+/-N` or `L+/-N`.
- Provides inode cache lookup, trap inode creation for layer-root loop detection, hashing by lower/upper inode, and `ovl_get_inode()` construction.

## Important Control Flow

`ovl_get_inode()` decides whether an overlay inode should be keyed by lower inode, upper inode, or allocated un-hashed based on lower presence, index state, upper presence, hardlink risk, and NFS export configuration. Existing cached inodes are verified against supplied upper/lower dentries before reuse.

`ovl_hash_bylower()` is central to identity: pure uppers are not hashed by lower, indexed objects are, read-only lower objects are, but lower hardlinks that may break on copy-up and non-indexed NFS-export uppers avoid lower hashing.

## Edge Cases

- Trap inodes intentionally fail verification to prevent layer-root recursion/loops.
- Directory inode numbers may be non-persistent when xino cannot uniquely map all layers.
- `update_time()` only updates upper atime and returns `-EAGAIN` for NOWAIT atime updates.
- ACL removal from lower first checks whether the ACL exists before copy-up.

## Dependencies

Uses OverlayFS layer/path helpers, xattrs, index flags, lockdep, POSIX ACL APIs, fileattr APIs, VFS stat and permission helpers, and inode cache primitives.

## Research Notes

This file is the inode identity and metadata authority for OverlayFS. It reconciles VFS-visible inode state with real upper/lower inode state while preserving copy-up, export, hardlink, and idmapped mount semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/inode.c -->