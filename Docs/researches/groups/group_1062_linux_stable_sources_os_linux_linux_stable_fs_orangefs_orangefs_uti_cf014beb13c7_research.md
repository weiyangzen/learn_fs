# Group Research: group_1062_linux_stable_sources_os_linux_linux_stable_fs_orangefs_orangefs_uti_cf014beb13c7

Scope: subset A from `Docs/research_subset_a.md`, covering the listed OrangeFS and overlayfs files under `sources/os/linux/linux-stable/fs`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-utils.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-utils.c

## Scope

This file provides OrangeFS kernel utility glue for mapping VFS inode state to OrangeFS protocol attributes, refreshing inode attributes through userspace client upcalls, detecting stale cached inodes, writing dirty inode attributes back, extracting fsids from operation unions, translating OrangeFS protocol errors to Linux errno values, and converting Linux mode bits to OrangeFS permission bits.

## Public And Internal APIs Covered

- `fsid_of_op()` extracts the filesystem id from operation-specific upcall payloads.
- Attribute translators: `orangefs_inode_flags()`, `orangefs_inode_perms()`, `copy_attributes_from_inode()`, `orangefs_inode_type()`.
- Inode validity helpers: `orangefs_make_bad_inode()` and `orangefs_inode_is_stale()`.
- Attribute operations: `orangefs_inode_getattr()`, `orangefs_inode_check_changed()`, `orangefs_inode_setattr()`.
- Error and mode conversion: `orangefs_normalize_to_errno()` and `ORANGEFS_util_translate_mode()`.

## Control Flow And Behavior

- `orangefs_inode_getattr()` first checks OrangeFS attribute cache timeout, pending local attribute updates, and dirty page state under `inode->i_lock`. If local setattr state is pending, it forces `write_inode_now()` and retries before issuing a remote GETATTR.
- GETATTR requests ask for all low-cost attributes and only include size when the caller passes flags. New inodes can accept symlink target initialization; existing inodes validate type and symlink target to detect stale objects.
- Regular file refresh updates immutable/append/noatime flags, size, block size, byte count, and block count. Directory refresh reports `PAGE_SIZE` size and nlink 1. Symlink refresh stores the target in OrangeFS private inode storage and points `inode->i_link` at it.
- `orangefs_inode_setattr()` snapshots delayed VFS changes from `orangefs_inode->attr_valid`, converts uid/gid/mode/time masks to `ORANGEFS_sys_attr_s`, clears pending state, and sends a writeback SETATTR upcall. Failure marks the inode bad except for root.
- `orangefs_inode_check_changed()` performs a narrow GETATTR for object type and link target to test whether a cached inode is still valid.
- `orangefs_normalize_to_errno()` handles success, positive server errors, OrangeFS non-errno protocol errors such as cancel, and encoded errno values via `PINT_errno_mapping`.

## State And Data Structures

- Uses `struct orangefs_inode_s` fields including `refn`, `attr_valid`, `attr_uid`, `attr_gid`, `getattr_time`, and `link_target`.
- Uses protocol structures `struct ORANGEFS_sys_attr_s`, `struct orangefs_kernel_op_s`, and `struct orangefs_object_kref`.
- Local inode state touched includes `i_flags`, `i_mode`, `i_uid`, `i_gid`, timestamps, size, block accounting, and symlink `i_link`.

## Dependencies

- Depends on OrangeFS operation allocation/service helpers: `op_alloc()`, `service_operation()`, and `op_release()`.
- Uses OrangeFS protocol constants from `protocol.h` and operation type definitions from OrangeFS kernel headers.
- Relies on VFS helpers for inode writeback, bad inode marking, dirty-page state, uid/gid conversion, and timestamp accessors.

## Risks And Invariants

- Attribute cache checks must be serialized with local pending setattr state; otherwise stale remote attributes could overwrite local changes.
- Root inode is deliberately not converted to a bad inode after userspace client loss because losing root inode operations would destabilize the mount.
- Symlink target comparison is part of stale detection; changed remote link targets invalidate cached symlink inodes.
- Error normalization is a protocol boundary. Unknown or malformed OrangeFS errors are mapped to `-EINVAL` after logging.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/protocol.h -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/protocol.h

## Scope

This header defines OrangeFS kernel/userspace protocol primitives, object handles, object references, attribute masks and structures, permission bits, xattr limits, OrangeFS-specific errors, device ioctl numbers, userspace protocol version requirements, shared device-map descriptors, and debug logging macros.

## APIs And Constants

- Object identifiers: `struct orangefs_khandle`, `struct orangefs_object_kref`, `ORANGEFS_khandle_cmp()`, `ORANGEFS_khandle_to()`, and `ORANGEFS_khandle_from()`.
- Filesystem and protocol constants: `ORANGEFS_SUPER_MAGIC`, `ORANGEFS_KERNEL_PROTO_VERSION`, `ORANGEFS_MINIMUM_USERSPACE_VERSION`, and `ORANGEFS_FS_ID_NULL`.
- Error encoding bits: `ORANGEFS_ERROR_BIT`, `ORANGEFS_NON_ERRNO_ERROR_BIT`, `ORANGEFS_ERROR_CLASS_BITS`, `ORANGEFS_ERROR_NUMBER_BITS`, and OrangeFS protocol errors such as `ORANGEFS_ECANCEL`.
- Permission and attribute masks: OrangeFS owner/group/other permission bits, immutable/append/noatime flags, `ORANGEFS_ATTR_SYS_*`, and aggregate masks.
- Xattr limits and flags: `ORANGEFS_MAX_XATTR_NAMELEN`, `ORANGEFS_MAX_XATTR_VALUELEN`, `ORANGEFS_MAX_XATTR_LISTLEN`, `ORANGEFS_XATTR_CREATE`, and `ORANGEFS_XATTR_REPLACE`.
- Data model types: `enum ORANGEFS_io_type`, `enum orangefs_ds_type`, `struct ORANGEFS_keyval_pair`, and `struct ORANGEFS_sys_attr_s`.
- Device interface: `ORANGEFS_DEV_*` ioctl numbers, debug mask structs, and `struct ORANGEFS_dev_map_desc`.
- Declares `ORANGEFS_util_translate_mode()` and exposes `gossip_debug()` / `gossip_err`.

## Control Flow And Behavior

- Handle comparison walks bytes from high to low and assumes little-endian handle ordering.
- Handle export/import helpers always copy the 16-byte kernel handle and zero-pad the destination buffer beyond the handle size.
- `ORANGEFS_sys_attr_s` is the central attribute carrier for getattr, setattr, create, mkdir, symlink, and copy-up-style metadata exchanges with userspace.
- Device ioctl constants define the ABI used by the OrangeFS character-device path for mapping shared buffers, remounting, debug configuration, version negotiation, and client strings.

## State And Data Structures

- `struct orangefs_khandle` is 16 bytes and aligned to 8 bytes.
- `struct orangefs_object_kref` combines a handle with a signed 32-bit fs id and padding.
- `struct ORANGEFS_keyval_pair` embeds fixed-size key/value xattr buffers.
- `struct ORANGEFS_sys_attr_s` includes ownership, permissions, times, size, optional allocated strings, distributed directory hints, mirror count, object type, flags, mask, and block size.
- Device-map descriptors retain pointer/size/count fields and must be normalized for 32-bit userspace compatibility.

## Dependencies

- Includes Linux kernel types, ioctl helpers, slab declarations, spinlock types, and `orangefs-debug.h`.
- The constants are consumed by OrangeFS superblock, inode, directory, xattr, waitqueue, and device protocol code.

## Risks And Invariants

- This is a kernel/userspace ABI header; structure sizes, padding, fixed buffer lengths, and ioctl numbers must remain compatible with OrangeFS client-core.
- Xattr name/value/list limits intentionally differ from generic Linux xattr limits and are tied to OrangeFS protocol request buffers.
- Error-code bit layout is decoded by `orangefs_normalize_to_errno()`; changes must stay synchronized with server-side encoding.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/protocol.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/super.c

## Scope

This file implements OrangeFS superblock lifecycle, mount context parsing, inode slab allocation/freeing, statfs, remount after userspace client restart, export file handles, mount/unmount upcalls, root inode setup, superblock list management, and inode-cache initialization/finalization.

## Public And Internal APIs Covered

- Mount parameters: `orangefs_fs_param_spec`, `orangefs_parse_param()`, `orangefs_show_options()`, `orangefs_init_fs_context()`.
- Inode cache: `orangefs_inode_cache_initialize()`, `orangefs_inode_cache_finalize()`, allocator/free/destructor callbacks.
- Super operations: `orangefs_s_ops` with alloc/free/destroy/write_inode/drop_inode/statfs/show_options.
- Filesystem operations: `orangefs_statfs()`, `orangefs_reconfigure()`, `orangefs_remount()`, `orangefs_kill_sb()`.
- Export operations: `orangefs_encode_fh()` and `orangefs_fh_to_dentry()`.
- Mount helpers: `orangefs_get_tree()`, `orangefs_fill_sb()`, `orangefs_unmount()`.
- Stub fsid key table functions: `fsid_key_table_initialize()` and `fsid_key_table_finalize()`.

## Control Flow And Behavior

- Mount context allocation creates `struct orangefs_sb_info_s`, clears default option bits, and installs fs context operations.
- Mount options support `acl`, `intr`, and `local_lock`; reconfigure updates only runtime OrangeFS option bits, while `acl` updates superblock flags through fs context parsing.
- `orangefs_get_tree()` sends `ORANGEFS_VFS_OP_FS_MOUNT` to userspace with the source server string, validates a non-null fs id, creates an anonymous superblock, fills it, stores the source devname, adds the private superblock to the global list, and negotiates features for userspace version 2.9.6 or newer.
- `orangefs_fill_sb()` installs xattr handlers, magic, super ops, dentry ops, block size, max file size, bdi, root inode/dentry, and export ops.
- `orangefs_remount()` is used after client-core restart. It sends a priority mount operation while the request mutex is already held, updates the transient mount id, clears `mount_pending`, and refreshes feature flags.
- `orangefs_kill_sb()` kills the anonymous superblock, sends a userspace unmount operation, removes the OrangeFS private superblock from the global list, waits for any remount-all loop to finish with the request mutex, and frees private superblock memory.
- File handle encoding stores a 16-byte OrangeFS handle plus fs id, optionally followed by parent handle and fs id.

## State And Data Structures

- Global state: `orangefs_inode_cache`, `orangefs_superblocks`, `orangefs_superblocks_lock`, and `orangefs_features`.
- Private superblock state includes root handle, fs id, transient id, device name, option flags, list linkage, `mount_pending`, `no_list`, and back-pointer to `struct super_block`.
- Private inode objects are slab allocated and preserve initialized `vfs_inode` and `xattr_sem` while resetting handle, fs id, failed block index, and symlink target storage.

## Dependencies

- Uses OrangeFS operation service path for mount, unmount, statfs, feature negotiation, and write_inode setattr.
- Uses VFS fs_context, anonymous superblocks, exportfs, dentry root creation, bdi setup, inode slab APIs, seq_file option reporting, and POSIX ACL superblock flag handling.
- Depends on OrangeFS inode lookup `orangefs_iget()`, dentry ops, xattr handlers, and request mutex/list coordination from other OrangeFS files.

## Risks And Invariants

- Mount failure after a userspace mount response must send an unmount or deactivate the locked superblock to avoid stale client-core mount state.
- `no_list` tracks partially initialized superblocks so kill paths do not remove unlisted entries.
- The private inode cache is created with a usercopy region limited to `link_target`.
- Superblock list manipulation is protected by `orangefs_superblocks_lock`, while teardown also synchronizes with request-mutex users that may traverse mounts for remount-all.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/symlink.c

## Scope

This small file defines the inode operation table for OrangeFS symlinks.

## APIs And Constants

- Exports `orangefs_symlink_inode_operations`.

## Behavior

- Symlink bodies are served through `simple_get_link`, using the cached link target stored in the inode.
- Attribute changes, getattr, xattr listing, permission checks, and timestamp updates are routed to OrangeFS common handlers:
  - `orangefs_setattr`
  - `orangefs_getattr`
  - `orangefs_listxattr`
  - `orangefs_permission`
  - `orangefs_update_time`

## Dependencies

- Includes OrangeFS protocol, kernel, and buffer-map headers.
- Relies on `orangefs_inode_getattr()` initialization of `inode->i_link` for new symlink inodes.

## Risks And Invariants

- The symlink target must already be resident in OrangeFS private inode storage when `simple_get_link` is used.
- Symlink xattr get/set behavior is constrained in `xattr.c`; this table exposes only listxattr directly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/upcall.h -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/upcall.h

## Scope

This header defines the fixed-layout request side of the OrangeFS kernel-to-userspace upcall protocol. It contains one structure per VFS operation class plus the top-level `struct orangefs_upcall_s` union sent to client-core.

## APIs And Structures

- File I/O: `struct orangefs_io_request_s` with shared-buffer index, count, offset, object ref, I/O type, and readahead size.
- Namespace operations: lookup, create, symlink, remove, mkdir, rename.
- Metadata operations: getattr, setattr, truncate, fsync, statfs.
- Directory iteration: readdir and readdirplus with tokens, count, masks, and buffer index.
- Mount lifecycle: fs mount, fs unmount, fs key, and feature negotiation requests.
- Xattrs: getxattr, setxattr, listxattr, removexattr.
- Control and tuning: cancel, parameter get/set operations, performance counter requests.
- Top-level `struct orangefs_upcall_s` includes operation type, uid/gid, pid/tgid, compatibility trailer fields, and a union of request payloads.

## Control Flow And Behavior

- Kernel callers allocate `struct orangefs_kernel_op_s`, populate the appropriate member of `upcall.req`, and submit it through `service_operation()`.
- `uid`, `gid`, `pid`, and `tgid` are filled around service submission to let userspace see the credential/process context.
- Cancel operations reuse an operation object by replacing the upcall with `ORANGEFS_VFS_OP_CANCEL` and the original operation tag.
- Parameter operations cover attribute/name/capability cache limits, performance sampling, debug masks, and readahead settings.

## State And Data Structures

- Many structures include explicit padding fields to preserve 32/64-bit ABI layout.
- Name-bearing requests use fixed `ORANGEFS_NAME_MAX` or `ORANGEFS_MAX_XATTR_NAMELEN` arrays.
- `orangefs_setxattr_request_s` embeds `struct ORANGEFS_keyval_pair`, so xattr values are carried inline up to OrangeFS protocol limits.
- `orangefs_param_request_s` supports 64-bit numeric values, two 32-bit values, or a debug string.

## Dependencies

- Depends on types and constants from `protocol.h`, including object refs, system attributes, I/O types, xattr sizes, and debug string length.

## Risks And Invariants

- The header explicitly preserves protocol compatibility with older userspace; padding and unused trailer fields are part of the ABI.
- Fixed-size arrays bound every request payload; callers must validate names and values before copying into the upcall.
- Changes to enum values or structure layout must be coordinated with client-core.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/upcall.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/waitqueue.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/waitqueue.c

## Scope

This file implements in-kernel queuing and completion waiting for OrangeFS operations submitted to the userspace client-core daemon. It handles request list insertion, daemon wakeup, interruption, purge/retry after daemon exit, timeout handling, cancellation, and cleanup of abandoned operations.

## Public And Internal APIs Covered

- `purge_waiting_ops()` marks all queued request-list operations purged when the device closes.
- `service_operation()` submits an operation and waits for a matching downcall.
- `orangefs_cancel_op_in_progress()` converts an in-progress operation into a cancel request.
- Internal helpers: `orangefs_clean_up_interrupted_operation()` and `wait_for_matching_downcall()`.

## Control Flow And Behavior

- `service_operation()` stamps the operation with current pid/tgid, optionally acquires `orangefs_request_mutex`, initializes status, queues the operation on `orangefs_request_list`, marks it waiting, wakes daemon waiters, and releases the mutex before sleeping.
- Priority operations are inserted at the head of the request list. This is used for remount operations after client restart.
- If the daemon is not in service, normal operations wait only up to `op_timeout_secs`; unmount operations avoid waiting.
- Completion waits use `wait_for_completion_io_timeout()` for writeback, interruptible timeout for interruptible operations, and killable timeout otherwise.
- Successful downcalls are normalized through `orangefs_normalize_to_errno()` before returning.
- Interrupted, timed-out, or purged operations are marked `OP_VFS_STATE_GIVEN_UP` and removed from whichever list owns them: pending request list, in-progress hash list, or copy-to/from-daemon transient state.
- Purged operations may retry up to `ORANGEFS_PURGE_RETRY_COUNT`; shared-memory I/O operations return to their caller for retry because buffer ownership is involved.
- `orangefs_cancel_op_in_progress()` preserves the old tag as the cancel target, frees the shared-memory slot later, assigns a new tag to the cancel op, and queues it if the daemon is active.

## State And Data Structures

- Global synchronization: `orangefs_request_mutex`, `orangefs_request_list_lock`, `orangefs_request_list_waitq`, and `orangefs_htable_ops_in_progress_lock`.
- Per-operation state includes `op_state`, `list`, `lock`, `waitq`, `attempts`, `tag`, `slot_to_free`, `uses_shared_memory`, `upcall`, and `downcall`.

## Dependencies

- Relies on OrangeFS device code to move operations from request list to in-progress table, copy upcalls/downcalls, set serviced state, and complete `op->waitq`.
- Uses OrangeFS daemon service-state helpers and operation state macros from kernel headers.

## Risks And Invariants

- `wait_for_matching_downcall()` returns with `op->lock` held, and callers must release or pass it to cleanup exactly as documented.
- Cleanup must distinguish list-empty copy races from waiting and in-progress states to avoid freeing or reusing an operation while daemon copy is active.
- `ORANGEFS_OP_NO_MUTEX` is only safe when the caller already holds the request mutex.
- Cancellation requires the original operation still be in progress; otherwise the cancel request is not queued.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/waitqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/xattr.c

## Scope

This file implements OrangeFS VFS extended attribute operations: get, set, remove, list, default xattr handler registration, reserved OrangeFS key filtering, create/replace flag translation, and a small per-inode xattr cache.

## Public And Internal APIs Covered

- VFS-facing functions: `orangefs_inode_getxattr()`, `orangefs_inode_setxattr()`, `orangefs_listxattr()`.
- Internal helpers: `is_reserved_key()`, `convert_to_internal_xattr_flags()`, `xattr_key()`, `find_cached_xattr()`, `orangefs_inode_removexattr()`.
- Xattr handler callbacks: `orangefs_xattr_get_default()` and `orangefs_xattr_set_default()`.
- Exports `orangefs_xattr_handlers`.

## Control Flow And Behavior

- `orangefs_inode_getxattr()` rejects symlink xattr reads, validates name length, checks a per-inode hash cache under `xattr_sem`, and supports size probes with `size == 0`.
- Negative cache entries use `length == -1` to return `-ENODATA` without a remote upcall until timeout.
- GETXATTR upcalls copy the key and key length, normalize `-ENOENT` to `-ENODATA`, validate returned value length, copy and zero-fill user buffers, then update or create a short-lived cache entry.
- `orangefs_inode_setxattr()` validates name/value sizes, maps Linux `XATTR_CREATE` / `XATTR_REPLACE` to OrangeFS flags, treats `size == 0 && value == NULL` as removexattr, sends SETXATTR, and invalidates any cached key.
- `orangefs_inode_removexattr()` sends REMOVEXATTR and maps missing-key behavior according to replace semantics.
- `orangefs_listxattr()` iterates using OrangeFS list tokens, validates returned key counts and lengths, filters out internal `system.pvfs2.` keys, and copies only whole keys that fit the caller buffer.
- The default handler uses an empty prefix so VFS passes full xattr names to OrangeFS.

## State And Data Structures

- Per-inode xattr cache is a 16-bucket hash table of `struct orangefs_cached_xattr`, protected by `orangefs_inode->xattr_sem`.
- Cache entries store key, value, length, timeout, and hash node.
- Listxattr upcalls use `ORANGEFS_ITERATE_START` and continue until `ORANGEFS_ITERATE_END`.

## Dependencies

- Uses OrangeFS operation service path for GETXATTR, SETXATTR, LISTXATTR, and REMOVEXATTR.
- Uses Linux xattr and POSIX ACL xattr helpers for flag constants and ACL name recognition.
- Cache storage is freed in `orangefs_free_inode()` from `super.c`.

## Risks And Invariants

- Reserved `system.pvfs2.` keys are intentionally hidden from listxattr output to discourage user modification of OrangeFS internal metadata.
- Returned list counts and lengths are validated defensively; impossible userspace-client responses become `-EIO`.
- The cache timeout code is partially disabled in lookup comments, but callers still check timeout before accepting cached values.
- Write/remove paths must invalidate cached keys under write lock to prevent stale xattr reads.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/Kconfig

## Scope

This Kconfig file defines overlayfs build selection and default feature toggles for redirects, redirect following, index, NFS export, xino inode mapping, metacopy, and debug checks.

## Configuration Options

- `OVERLAY_FS`: tristate overlay filesystem support; selects `FS_STACK` and `EXPORTFS`.
- `OVERLAY_FS_REDIRECT_DIR`: default-on behavior for directory rename redirects when enabled.
- `OVERLAY_FS_REDIRECT_ALWAYS_FOLLOW`: default `y`; preserves backward-compatible redirect following even when redirects are otherwise off.
- `OVERLAY_FS_INDEX`: default feature for index directory mapping of lower inodes to upper inodes, preserving lower hardlinks on copy-up.
- `OVERLAY_FS_NFS_EXPORT`: depends on overlayfs index and not metacopy; defaults NFS export support.
- `OVERLAY_FS_XINO_AUTO`: 64-bit-only default for automatic inode number mapping using high bits.
- `OVERLAY_FS_METACOPY`: metadata-only copy-up default; selects redirect-dir support.
- `OVERLAY_FS_DEBUG`: enables extra debugging checks.

## Behavior And Tradeoffs

- Redirect, index, NFS export, and metacopy options are explicitly documented as not backward compatible with older kernels that do not understand the corresponding overlay metadata.
- NFS export creates a fuller index and may add mount-time verification overhead.
- XINO improves unified inode numbering at the cost of possible 32-bit inode compatibility issues for applications.
- Metacopy defers data copy-up until write open, improving metadata-heavy workloads but interacting with redirect and NFS export constraints.

## Dependencies

- These options are consumed by overlayfs parameter defaults and compile-time conditionals across the overlayfs implementation.
- `OVERLAY_FS_NFS_EXPORT` depends on `OVERLAY_FS_INDEX` and conflicts with `OVERLAY_FS_METACOPY`.

## Risks And Invariants

- Default-enabled incompatible metadata features can make mounts behave unexpectedly on older kernels.
- The Kconfig dependency graph prevents enabling NFS export by default with metacopy because that combination is not supported by this configuration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/Makefile

## Scope

This Makefile wires the overlayfs module/object build into the kernel build system.

## Build Rules

- `obj-$(CONFIG_OVERLAY_FS) += overlay.o` builds overlayfs when the Kconfig option is enabled.
- `overlay-objs` combines the implementation objects:
  - `super.o`
  - `namei.o`
  - `util.o`
  - `inode.o`
  - `file.o`
  - `dir.o`
  - `readdir.o`
  - `copy_up.o`
  - `export.o`
  - `params.o`
  - `xattrs.o`

## Dependencies And Role

- This file defines the compilation unit boundaries for the overlayfs subsystem.
- The listed objects provide mount/lookup/utilities/inode/file/directory/readdir/copy-up/export/parameter/xattr functionality for the final `overlay.o`.

## Risks And Invariants

- Any new overlayfs source file must be added to `overlay-objs` or it will not link into the module/built-in filesystem.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/copy_up.c -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/copy_up.c

## Scope

This file implements overlayfs copy-up: copying lower objects into upper/work/index directories, copying data and metadata, handling metacopy, preserving selected xattrs/file attributes/ACLs, setting origin and index file handles, maintaining nlink metadata, using temporary files or workdir temps, and exposing public copy-up entry points.

## Public And Internal APIs Covered

- Public helpers: `ovl_copy_xattr()`, `ovl_set_attr()`, `ovl_encode_real_fh()`, `ovl_get_origin_fh()`, `ovl_set_origin_fh()`, `ovl_maybe_copy_up()`, `ovl_copy_up_with_data()`, `ovl_copy_up()`.
- Copy-up core: `ovl_copy_up_flags()`, `ovl_copy_up_one()`, `ovl_do_copy_up()`, `ovl_copy_up_workdir()`, `ovl_copy_up_tmpfile()`.
- Data/metadata helpers: `ovl_copy_up_file()`, `ovl_copy_up_data()`, `ovl_copy_up_metadata()`, `ovl_copy_up_meta_inode_data()`.
- Index/origin helpers: `ovl_create_index()`, `ovl_set_upper_fh()`, `ovl_link_up()`.
- Credential helpers via scoped cleanup classes for LSM-provided copy-up credentials.
- Module parameter `check_copy_up` is retained as obsolete and always reports `N`.

## Control Flow And Behavior

- Copy-up starts by verifying/lazily locating lower data, then repeatedly copies the topmost ancestor that lacks an upper until the target is copied.
- Metadata-only copy-up is chosen for regular files when metacopy is enabled and the open flags do not require data writes or truncation. Required fs-verity mode forces fallback unless lower data has active verity.
- Data copy-up first tries `vfs_clone_file_range()`. If cloning cannot copy the entire file, it falls back to chunked `do_splice_direct()` with 1 MiB chunks and optional sparse-hole skipping via `SEEK_DATA`.
- Metadata copy-up copies xattrs with LSM filtering, handles POSIX ACLs via ACL APIs, copies selected fileattr flags, stores origin file handles, writes metacopy xattrs and optional fs-verity digest state, restores size/ownership/mode/timestamps, and fsyncs metadata when strict sync policy requires it.
- Workdir copy-up creates a temp object in workdir or indexdir, copies data and metadata, then renames into place under appropriate rename locking.
- O_TMPFILE copy-up writes data/metadata into an unnamed upper tmpfile and links it into the destination.
- Indexed non-directories may be copied directly into the index dir and then hardlinked to the upper dir. Indexed directories are copied to the index area and receive a separate index entry.
- If a dentry already has metacopy metadata but later needs data, `ovl_copy_up_meta_inode_data()` copies lower data into the existing upper file, restores `security.capability` if writing cleared it, removes the metacopy xattr, and marks upper data present.
- Public open-time copy-up skips special files and only acts when open flags require copy-up.

## State And Data Structures

- `struct ovl_copy_up_ctx` carries parent/dentry, lower path, source and parent stats, symlink target, destination dir/name, workdir, origin file handle, origin/index/metacopy flags, digest state, and metadata fsync policy.
- File-handle xattrs use `struct ovl_fh` with magic/version/type/flags/length/uuid and inner exportfs fid.
- Inode flags affected include `OVL_INDEX`, `OVL_HAS_DIGEST`, `OVL_VERIFIED_DIGEST`, and upperdata state.
- Uses overlay xattrs such as origin, upper, metacopy, nlink, and impure markers.

## Dependencies

- Relies on VFS file APIs, exportfs file-handle encoding, splice, clone_file_range, fsync, xattr, ACL, fileattr, fs-verity, LSM copy-up hooks, and scoped credential override helpers.
- Depends heavily on overlayfs helpers from other files for path lookup, temp creation, rename wrappers, xattr wrappers, index naming, metacopy/digest helpers, nlink helpers, lowerdata verification, and inode update.

## Risks And Invariants

- Copy-up must avoid exposing partially initialized upper objects; temp/workdir plus rename/link sequences enforce that.
- Data must be copied before xattrs because writing data can clear `security.capability`.
- Sparse-hole seeking is opportunistic and must fall back to normal copying if unsupported.
- Strict sync policy changes fsync placement to preserve atomic copy-up semantics on filesystems with weak metadata ordering.
- UID/GID must be mappable in the current user namespace before copy-up.
- Copy-up locking deliberately avoids holding upper sb writers across lower llseek in nested overlay cases.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/copy_up.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/dir.c

## Scope

This file implements overlayfs directory inode operations: create, mkdir, mknod, symlink, hardlink, unlink, rmdir, rename, tmpfile, whiteout handling, cleanup, temp object creation, opaque directory handling, redirect xattrs, credential overrides for creation, and parent/dentry state updates.

## Public And Internal APIs Covered

- Public helpers: `ovl_cleanup()`, `ovl_tempname()`, `ovl_cleanup_and_whiteout()`, `ovl_create_real()`, `ovl_create_temp()`.
- Creation paths: `ovl_create_upper()`, `ovl_create_over_whiteout()`, `ovl_create_or_link()`, `ovl_create_object()`, VFS callbacks `ovl_create()`, `ovl_mkdir()`, `ovl_mknod()`, `ovl_symlink()`, `ovl_link()`.
- Removal paths: `ovl_remove_upper()`, `ovl_remove_and_whiteout()`, `ovl_do_remove()`, `ovl_unlink()`, `ovl_rmdir()`.
- Rename paths: `ovl_set_redirect()`, `ovl_rename_start()`, `ovl_rename_upper()`, `ovl_rename_end()`, `ovl_rename()`.
- Tmpfile support: `ovl_tmpfile()`, `ovl_create_tmpfile()`.
- Operation table: `ovl_dir_inode_operations`.

## Control Flow And Behavior

- Temporary names are generated from an atomic counter and used in workdir/index operations.
- Whiteouts are created in workdir. A shared whiteout inode is reused through hardlinks until link creation fails with non-`EMLINK`, after which sharing is disabled.
- Cleanup removes temporary dentries with directory-aware unlink/rmdir wrappers and logs failures.
- Creating a real upper object dispatches by mode to create, mkdir, mknod, symlink, or hardlink. Directory creation validates inherited casefold state.
- Creation over a whiteout creates a temp object, applies mode/ACL adjustments, then renames over the whiteout. Directory creation over whiteout uses exchange plus cleanup to preserve whiteout semantics.
- Overlay creation first copies up the parent, gets write access, preallocates an overlay inode, initializes ownership, overrides creator credentials to the new inode uid/gid, creates or links the upper object, then instantiates the overlay dentry.
- Hardlink creation copies up the old object and new parent, starts nlink tracking, ensures metacopy hardlinks have redirects, and links the upper dentry into the new parent.
- Remove/rmdir checks merged directory emptiness, copies up the parent, starts nlink tracking, and either removes pure upper objects or replaces lower-positive objects with whiteouts.
- Directory clearing for non-empty merged whiteout cleanup creates an opaque temp directory, copies xattrs/attrs, exchanges it with the upper dir, cleans contained whiteouts, and drops the stale overlay dentry.
- Rename refuses unsupported flags, avoids copying up whole directory trees when redirects are unavailable, copies up source/target parents as needed, handles whiteout/exchange cases, sets redirects or opaque xattrs when moving merge/lower objects, performs upper rename, updates nlink and ctime, and marks modified dirs.
- Tmpfile support uses backing tmpfile open on the upper parent, wraps the real file in `struct ovl_file`, instantiates the overlay dentry, and ensures cleanup if `finish_open()` does not complete.

## State And Data Structures

- Module parameter `redirect_max` bounds absolute redirect xattr length.
- `struct ovl_renamedata` extends VFS `renamedata` with opaque-dir cleanup, nlink update, overwrite, and cleanup-whiteout flags.
- Parent/dentry flags affected include upper alias, revalidation data, opaque, whiteouts, impure, redirect string, and nlink xattrs.
- Uses `OVL_TEMPNAME_SIZE`, whiteout cache state in `struct ovl_fs`, and per-inode overlay nlink state.

## Dependencies

- Depends on overlayfs copy-up, lookup, xattr, ACL, readdir empty-check/whiteout cleanup, inode/nlink helpers, file wrapper allocation, and VFS rename/create/remove wrappers.
- Uses VFS locking helpers such as `start_creating`, `start_removing`, `start_renaming`, `start_renaming_two_dentries`, and scoped credential helpers.
- Uses LSM `security_dentry_create_files_as()` for creation credentials.

## Risks And Invariants

- Upper dentry identity is revalidated under locks before remove/rename to detect stale races.
- Whiteouts and opaque dirs must preserve overlay visibility semantics during atomic replacement.
- Redirect xattrs are required to avoid copying up full directory trees; failure falls back to `-EXDEV`.
- Nested overlay locking order is sensitive around write access, rename locks, and lower/upper inode locks.
- Creation over whiteouts must handle ACLs and umask-mutated modes before making the object visible.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/export.c -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/export.c

## Scope

This file implements overlayfs exportfs/NFS file-handle support: deciding upper vs lower handle encoding, forcing copy-up of connectable ancestors, encoding overlay file handles, decoding upper/lower handles back to overlay dentries, consulting index/origin metadata, reconnecting directory paths, and exposing export operation tables.

## Public And Internal APIs Covered

- Export ops: `ovl_encode_fh()`, `ovl_fh_to_dentry()`, `ovl_fh_to_parent()`, `ovl_get_name()`, `ovl_get_parent()`.
- Operation tables: `ovl_export_operations` and `ovl_export_fid_operations`.
- Encoding helpers: `ovl_check_encode_origin()`, `ovl_connect_layer()`, `ovl_connectable_layer()`, `ovl_dentry_to_fid()`.
- Decode/reconnect helpers: `ovl_upper_fh_to_d()`, `ovl_lower_fh_to_d()`, `ovl_fid_to_fh()`, `ovl_get_dentry()`, `ovl_obtain_alias()`, `ovl_lookup_real()`, `ovl_lookup_real_ancestor()`, `ovl_lookup_real_inode()`, `ovl_lookup_real_one()`.

## Control Flow And Behavior

- Encoding usually uses lower file handles for non-upper or indexed-origin objects to preserve stable identity across copy-up, and upper file handles for pure upper, non-indexed upper, and root.
- For decodable NFS export of lower directories, `ovl_connect_layer()` may copy up a connectable ancestor before encoding so future decode can reconnect from the lower real dentry to an overlay dentry.
- `ovl_dentry_to_fid()` encodes either an upper or lower real inode with `ovl_encode_real_fh()` and returns the byte length needed by exportfs.
- Connectable parent file handles are not supported; `fh_to_parent` returns `-EACCES` and warns to use `no_subtree_check`.
- Decoding upper handles requires an upper mount and maps the decoded upper dentry into an overlay dentry.
- Decoding lower handles first validates origin file handles and layer acceptability, checks inode cache aliases, consults index entries, verifies origin/index consistency, then obtains a connected directory dentry or disconnected non-directory alias.
- Directory reconnect walks from a known connected ancestor toward the target real dentry, looking up overlay children by real names and restarting if overlay rename races break parentage.
- Old unaligned file-handle format `OVL_FILEID_V0` is copied into an aligned buffer before validation.

## State And Data Structures

- Uses `struct ovl_fh` encoded inside exportfs `fid` buffers, including flags such as `OVL_FH_FLAG_PATH_UPPER`.
- Uses overlay layers, lower stacks, index dentries, origin handles, dcache aliases, and inode hash lookups.
- `OVL_E_CONNECTED` dentry flag caches positive connected-layer results.

## Dependencies

- Depends on exportfs encoding/decoding, overlayfs origin/index helpers, copy-up, lookup, dentry allocation, inode lookup, layer metadata, and real path decoding.
- Uses dentry name snapshots to avoid use-after-free when racing with underlying layer rename.

## Risks And Invariants

- Non-connectable lower directory handles must be made connectable at encode time or decode can fail later.
- Directory decode must reject disconnected, unhashed, moved-out, or stale underlying dentries.
- Inode/dentry cache aliases are verified against real upper/lower dentries to avoid returning mismatched overlay objects.
- `fh_to_parent`, `get_name`, and `get_parent` are intentionally unsupported for subtree-check style export.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/file.c

## Scope

This file implements overlayfs regular file operations by opening and caching real backing files, routing reads/writes/splice/fallocate/fsync/mmap/fadvise/copy-range/remap/flush to the correct real file, synchronizing overlay position and attributes, handling lazy upper-file open after copy-up/metacopy transitions, and enforcing flag/permission behavior.

## Public And Internal APIs Covered

- File wrapper lifecycle: `struct ovl_file`, `ovl_file_alloc()`, `ovl_file_free()`.
- Open/close: `ovl_open()`, `ovl_release()`, `ovl_open_realfile()`.
- Real-file resolution: `ovl_real_file()`, `ovl_real_file_path()`, `ovl_change_flags()`.
- File operations: `ovl_llseek()`, `ovl_read_iter()`, `ovl_write_iter()`, `ovl_splice_read()`, `ovl_splice_write()`, `ovl_fsync()`, `ovl_mmap()`, `ovl_fallocate()`, `ovl_fadvise()`, `ovl_copy_file_range()`, `ovl_remap_file_range()`, `ovl_flush()`.
- Operation table: `ovl_file_operations`.

## Control Flow And Behavior

- Open verifies lowerdata, performs copy-up if open flags require it, strips create/truncate-only flags before opening the real file, and stores the real backing file in `file->private_data`.
- `ovl_open_realfile()` checks permissions on the real inode using overlay mounter credentials, adjusts `O_NOATIME` if needed, and opens the backing file.
- `ovl_real_file_path()` detects when the originally opened real file no longer matches the current real data path, usually after copy-up or metacopy data copy-up. It lazily opens and caches an upper file with `cmpxchg_release()`.
- Flag changes are propagated to real files for append, nonblock, ndelay, and direct I/O, with immutable append and O_DIRECT capability checks.
- `llseek` keeps overlay `f_pos` as the master copy while delegating nontrivial seek semantics, including holes/data, to the real file under overlay inode lock.
- Reads and splice reads delegate through backing-file helpers with mounter credentials and atime/mtime/ctime synchronization callbacks.
- Writes, splice writes, fallocate, copy_file_range, and clone/remap operations lock the overlay inode, refresh mode/attrs, remove privileges where appropriate, operate on real files, and then refresh overlay size/timestamps.
- `fsync` only syncs upper data; lower-only objects and datasync on merge dirs avoid lower fsync to prevent read-only errors.
- Dedupe does not trigger copy-up and is rejected unless both files already have upper inodes.

## State And Data Structures

- `struct ovl_file` stores the initially opened `realfile` and an optional lazily opened `upperfile`.
- Overlay inode flags and upperdata/metacopy state decide whether the real backing file is upper, lower, or metadata-only upper.
- Uses `backing_file_ctx` callbacks for credential override and post-I/O attr updates.

## Dependencies

- Relies on overlayfs copy-up/lowerdata verification, path resolution, inode attr copy, sync policy, upperdata state, and directory real-file support.
- Uses kernel backing-file helpers, VFS I/O APIs, lease helper, fileattr privilege removal, and mounter credentials.

## Risks And Invariants

- The overlay file position must remain authoritative across backing file changes.
- Lazy upperfile caching must verify the cached file still maps to the expected upper inode, otherwise returns `-EIO`.
- Dedupe cannot copy up because that would duplicate data rather than deduplicate it.
- Write paths must update overlay metadata after backing-file operations so stat results remain coherent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/inode.c

## Scope

This file implements overlayfs inode operations and inode lifecycle: setattr, getattr/stat inode mapping, permission checks, symlink targets, POSIX ACL get/set with idmapped layers, timestamp updates, fiemap, fileattr get/set including protected immutable/append flags, inode operation tables, lockdep class annotation for nested overlays, inode number mapping, inode initialization, nlink xattr accounting, inode hashing/lookup/trap inodes, and overlay inode creation.

## Public And Internal APIs Covered

- VFS inode operations: `ovl_setattr()`, `ovl_getattr()`, `ovl_permission()`, `ovl_update_time()`, `ovl_fileattr_get()`, `ovl_fileattr_set()`, and symlink `ovl_get_link()`.
- ACL APIs under `CONFIG_FS_POSIX_ACL`: `ovl_get_acl_path()`, `do_ovl_get_acl()`, `ovl_set_acl()`.
- Fileattr helpers: `ovl_real_fileattr_get()`, `ovl_real_fileattr_set()`.
- Inode setup: `ovl_new_inode()`, `ovl_inode_init()`, `ovl_get_inode()`, `ovl_lookup_inode()`, `ovl_get_trap_inode()`, `ovl_lookup_trap_inode()`.
- Nlink helpers: `ovl_set_nlink_upper()`, `ovl_set_nlink_lower()`, `ovl_get_nlink()`.
- Operation tables: regular file, symlink, special inode ops, and overlay address-space ops.

## Control Flow And Behavior

- `ovl_setattr()` validates attributes on the overlay inode, chooses metadata-only or data copy-up for size changes, strips unsupported `ATTR_FILE` and `ATTR_OPEN`, gets write access for truncation, applies changes to the upper dentry under mounter credentials, and copies attrs back to the overlay inode.
- `ovl_getattr()` obtains real stats, overlays effective immutable/append statx flags, preserves stable st_dev/st_ino across copy-up when possible, handles origin/index semantics, fixes metacopy block reporting, maps inode numbers through samefs/xino/pseudo-dev rules, sets merge-dir nlink to 1, and reports overlay nlink for indexed upper files.
- Permission checking first applies generic permission against the overlay inode with task credentials, then checks underlying real inode permissions with mounter credentials. Lower write checks are converted to read checks when copy-up would be needed.
- Symlink reads delegate to the real dentry under overlay credentials.
- ACL retrieval can clone and idmap ACL entries from idmapped lower/upper mounts so cached ACLs on underlying filesystems are not mutated. RCU ACL lookup drops out for idmapped mounts.
- ACL setting copies up lower objects when necessary, checks owner/capability rules, handles SGID stripping through `ovl_setattr()`, and sets or removes ACL xattrs on the real upper object.
- Atime updates touch the upper path only when present and copy the resulting atime to the overlay inode.
- Fiemap delegates to the real data inode.
- Fileattr set copies up, writes protected immutable/append state to overlay private xattrs, applies fileattr to upper, merges real flags with protected overlay flags, and refreshes ctime. Fileattr get reads real attributes and overlays protected flags.
- Inode initialization copies attrs/flags from real inode, maps inode numbers, installs operation tables by mode, marks ACLs uncached, sets `S_NOCMTIME`, and annotates locks based on overlay stack depth.
- Indexed nlink xattrs store union nlink deltas relative to upper or lower inode nlink using `U+N` / `L+N` text encoding.
- `ovl_get_inode()` decides whether to hash by upper or lower inode, reuses cached inodes after strict verification, creates anonymous inodes for lower hardlinks that will be broken on copy-up, initializes flags such as index/const-ino/whiteouts/impure, and checks protected fileattr xattrs.

## State And Data Structures

- Overlay inode private data tracks upper dentry, lower stack entry, redirects, lowerdata redirect, flags, and lock.
- Inode number mapping uses overlay `last_ino`, samefs detection, xino high bits, layer fsid, and pseudo-devs.
- Trap inodes are dead directory inodes keyed by layer root real inode to detect lookup loops/conflicting layer roots.
- Protected fileattr flags are represented both in overlay inode `i_flags` and overlay private xattrs.

## Dependencies

- Depends on overlayfs path/type helpers, copy-up, xattrs, origin/index verification, credentials, nlink helpers, lowerdata path resolution, and directory/file operation tables from sibling files.
- Uses VFS permission, stat, ACL, fileattr, fiemap, inode hash, lockdep, idmapped mount, and security ioctl hooks.

## Risks And Invariants

- st_dev/st_ino mapping must remain stable across copy-up when possible while avoiding collisions across layers.
- Overlay permission semantics intentionally combine caller authorization on overlay inode with mounter authorization on underlying inode.
- ACL idmapping must clone before rewriting entries to avoid corrupting underlying filesystem-wide ACL cache.
- Inode cache reuse requires verifying stored upper/lower real inodes against lookup dentries, especially for directories and NFS decode paths.
- Nested overlay lock classes must reflect stack depth to keep lockdep from reporting false recursive inode-lock cycles while still catching real inversions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/inode.c -->