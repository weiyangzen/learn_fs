# Group Research: group_1889_xnu_sources_os_darwin_xnu_bsd_vfs_Makefile_sources_os_darwin_xnu_bs_04153e602f61

Scope checked: `Docs/research_subset_a.md` includes `sources/os/darwin/xnu`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/Makefile -->
# File Research: sources/os/darwin/xnu/bsd/vfs/Makefile

This 25-line make fragment participates in the XNU kernel build/export system for `bsd/vfs`.

It imports the shared XNU make definitions from `${SRCROOT}/makedefs` via `MakeInc.cmd`, `MakeInc.def`, `MakeInc.rule`, and `MakeInc.dir`. The only local data file named for install is `vfs_support.h`.

Export/install behavior:
- `INSTALL_MI_LIST`, `INSTALL_SF_MI_LCL_LIST`, and `INSTALL_KF_MI_LIST` all include `vfs_support.h`.
- `INSTALL_MI_DIR` is `vfs`.
- `EXPORT_MI_LIST` exports `vfs_support.h`, `vfs_disk_conditioner.h`, and `vfs_exclave_fs.h`.
- `EXPORT_MI_DIR` is also `vfs`.

This file contains no compilation rules of its own; it declares VFS public/support headers and delegates rule execution and directory traversal to the shared XNU make include files.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/doc_tombstone.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/doc_tombstone.c

This file implements per-thread document-ID tombstone tracking used by Darwin VFS rename/delete/create flows to preserve document identity across application “safe save” patterns.

Core data model:
- Tombstone state is stored on the current `uthread` in `ut->t_tombstone`.
- The state records the prior parent vnode, parent vid, item vnode, item vid, file id, document id, and filename.
- The implementation assumes related safe-save operations happen on the same thread.

Functions:
- `doc_tombstone_get()` lazily allocates a zeroed `struct doc_tombstone` for the current thread using `kalloc_type`.
- `doc_tombstone_clear(struct doc_tombstone *ut, vnode_t *old_vpp)` clears the stored parent/name/document-id fields and, if requested, tries to return a still-valid old item vnode with an iocount.
- `doc_tombstone_should_ignore_name(const char *nameptr, int len)` filters temporary names beginning with `atmp` or ending in `.bak`/`.tmp`.
- `doc_tombstone_should_save(struct doc_tombstone *ut, struct vnode *vp, struct componentname *cnp)` refuses to save if the component name is missing, or if an existing tombstone for the same vnode would be overwritten by an ignorable temp name.
- `doc_tombstone_save(struct vnode *dvp, struct vnode *vp, struct componentname *cnp, uint64_t doc_id, ino64_t file_id)` records the parent/name and document identity for a vnode.

Important correctness details:
- Vnode identity is checked using `vnode_vid()` because stored vnode pointers may be recycled.
- `doc_tombstone_clear()` rechecks the vid after `vnode_get()` and rejects vnodes marked `VL_TERMINATE`.
- The caller remains responsible for generating corresponding fsevents.
- Temporary-file filtering exists specifically to avoid losing useful tombstone state during unusual safe-save sequences from applications.

This file is small but sits on a sensitive VFS identity-preservation path: it prevents replacement-style saves from accidentally losing document IDs when the “real” file is removed and recreated through temporary filenames.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/doc_tombstone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/kpi_vfs.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/kpi_vfs.c

This 6536-line file is the main exported Darwin VFS/vnode KPI wrapper implementation. It exposes stable kernel-facing entry points around filesystem `vfsops` and vnode operation vectors, plus many mount, vnode, context, attribute, notification, extended-attribute, and compatibility helpers.

Major responsibilities:
- Wrap `struct vfsops` callbacks through `VFS_*` functions.
- Register/unregister filesystems and build vnode operation vectors.
- Manage `vfs_context_t` creation, credential/thread access, and process policy queries.
- Expose mount and vnode accessors/mutators.
- Normalize vnode attributes and provide fallback extended-security storage.
- Wrap `VNOP_*` operations with argument structs, DTrace hooks, notifications, and compatibility shims.
- Handle AppleDouble compatibility for filesystems without native extended attributes.

VFS operation wrappers:
- `VFS_MOUNT`, `VFS_START`, `VFS_UNMOUNT`, `VFS_ROOT`, `VFS_QUOTACTL`, `VFS_GETATTR`, `VFS_SETATTR`, `VFS_SYNC`, `VFS_VGET`, `VFS_FHTOVP`, `VFS_VPTOFH`, `VFS_IOCTL`, and `VFS_VGET_SNAPDIR`.
- These guard against `dead_mountp` and missing callbacks, returning `ENOTSUP`.
- Several default a missing context to `vfs_context_current()`.
- `VFS_MOUNT` enforces 64-bit readiness for 64-bit callers.

Mount KPI helpers:
- Accessors return type names/numbers, throttle masks, mount ids, flags, mount labels, statfs data, filesystem private data, native xattr support, device block size, covered vnode, device vnode, IO attributes, max symlink length, and idle time.
- Mutators set/clear mount command flags, auth-cache TTL flags, opaque auth flags, extended security, system/system-data/swap/noswap flags, filesystem private data, device vnode, IO attributes, and owner uid/gid.
- `vfs_setdevvp()` validates block-device type and major number before storing `mnt_devvp`.

Filesystem registration:
- `vfs_fsadd()` validates the `vfs_fsentry`, rejects non-threadsafe filesystems, allocates a `vfstable`, assigns static or dynamic filesystem type numbers using `vfs_typenum_arr`, maps `VFS_TBL*` flags to `VFC_*` and mount flags, allocates vnode operation vectors, fills explicit operations, validates operation descriptors, supplies default operations, adds the filesystem with `vfstable_add()`, and calls optional `vfs_init`.
- `vfs_fsremove()` refuses removal while refcounted mounts exist, clears the type number bitmap, deletes the vfstable, and frees operation descriptors only after successful deletion.
- This path is central to loadable/registered filesystem integration.

Context handling:
- `vfs_context_pid`, `vfs_context_proc`, `vfs_context_thread`, `vfs_context_task`, `vfs_context_cwd`, `vfs_context_ucred`, `vfs_context_issuser`, `vfs_context_iskernel`, `vfs_context_suser`, and audit-token/signal helpers expose process/thread/credential state.
- `vfs_context_create()` copies a context and refs credentials.
- `vfs_context_create_with_proc()` creates a context from a process and marks a referenced thread by tagging the low bit of `vc_thread`.
- `vfs_context_rele()` unrefs credentials and deallocates tagged referenced threads.
- Policy helpers expose trigger resolution, lease breaking, filesystem-block-size nocache writes, mtime skipping, and entitled reserve access from process/thread policy bits.
- `vfs_context_current()` aliases `current_thread_ro()` after static offset checks.

Vnode accessors and flags:
- Provides vnode type/mode conversion, root vnode lookup, vid/mount/type/fsnode/rdev/tag/parent/name access, mount metadata access, and compound-operation capability checks.
- Boolean helpers identify root/system/swap/tty/mount/recycled/rage/nocache/no-readahead/open-event/standard/noflush/file-type/device-alias/named-stream/shadow state.
- Set/clear helpers mutate vnode flags under vnode spin locks for nocache, open events, no-readahead, fast-device candidate, auto candidate, noflush, and mounted-on state.
- `vnode_lookup_continue_needed()` requests continued lookup for mount crossings, trigger resolution, and symlink-follow/trailing-slash cases.

Attribute and extended-security handling:
- `vnode_get_filesec()` reads `KAUTH_FILESEC_XATTR`, validates size, magic, ACL entry count, and converts disk-endian security data to host order.
- `vnode_set_filesec()` writes filesec/ACL data through xattrs after converting to disk byte order.
- `vnode_getattr()` rejects unknown attributes, suppresses extended-security requests when disabled, calls `VNOP_GETATTR`, falls back to xattr-backed filesec data for ACL/owner/group UUIDs, normalizes ignored ownership, synthesizes missing iosize/flags/filerev/gen/size/allocation/change-time/type/fsid values, and updates vfsstat when needed.
- `vnode_setattr()` rejects unknown attributes, blocks writes on read-only mounts, protects swap vnodes outside development/debug kernel builds, restricts named streams, validates truncation by vnode type, strips ownership changes on ignore-ownership mounts, rejects extended security when unsupported, calls `VNOP_SETATTR`, then uses `vnode_setattr_fallback()` for unsupported security attributes.
- `vnode_setattr_fallback()` performs read/modify/write of xattr-backed filesec data or removes the xattr when ACL and UUID fields are empty.
- Attribute changes drive fsevents and invalidate vnode authorization caches when permission-relevant fields change.

Notifications and monitoring:
- `vnode_notify()` maps VFS vnode event bits to kqueue notes, maps permission changes to `NOTE_ATTRIB`, directory content changes to `NOTE_WRITE`, posts knotes, and optionally creates fsevents.
- `vfs_get_notify_attributes()` initializes the attribute mask needed for notifications.
- `vnode_ismonitored()` checks vnode knote presence.
- `vfs_settriggercallback()` installs a trigger callback on a mounted filesystem by fsid when trigger support is compiled in.
- Later `VNOP_*` wrappers consistently call DTrace macros and post kqueue notes for successful mutations.

VNOP wrappers:
- Lookup and creation: `VNOP_LOOKUP`, `VNOP_COMPOUND_OPEN`, `VNOP_CREATE`, `VNOP_MKNOD`, `VNOP_SYMLINK`.
- File lifecycle and metadata: `VNOP_OPEN`, `VNOP_CLOSE`, `VNOP_ACCESS`, `VNOP_GETATTR`, `VNOP_SETATTR`, `VNOP_INACTIVE`, `VNOP_RECLAIM`, `VNOP_PATHCONF`, `VNOP_SETLABEL`.
- I/O and VM: `VNOP_READ`, `VNOP_WRITE`, `VNOP_IOCTL`, `VNOP_SELECT`, `VNOP_FSYNC`, `VNOP_MMAP_CHECK`, `VNOP_MMAP`, `VNOP_MNOMAP`, `VNOP_PAGEIN`, `VNOP_PAGEOUT`, `VNOP_STRATEGY`, `VNOP_BWRITE`.
- Namespace mutation: `VNOP_REMOVE`, `VNOP_COMPOUND_REMOVE`, `VNOP_LINK`, `VNOP_RENAME`, `VNOP_RENAMEX`, `VNOP_COMPOUND_RENAME`, `VNOP_MKDIR`, `VNOP_COMPOUND_MKDIR`, `VNOP_RMDIR`, `VNOP_COMPOUND_RMDIR`, plus convenience dispatchers `vn_remove`, `vn_rename`, `vn_mkdir`, `vn_rmdir`.
- Directory enumeration and metadata bulk APIs: `VNOP_READDIR`, `VNOP_READDIRATTR`, `VNOP_GETATTRLISTBULK`, optional `VNOP_SEARCHFS`.
- Cloning/copying/xattrs: `VNOP_COPYFILE`, `VNOP_CLONEFILE`, `VNOP_GETXATTR`, `VNOP_SETXATTR`, `VNOP_REMOVEXATTR`, `VNOP_LISTXATTR`.
- Block and verification APIs: `VNOP_BLKTOOFF`, `VNOP_OFFTOBLK`, `VNOP_VERIFY`, `VNOP_BLOCKMAP`.
- Event/filter APIs: `VNOP_KQFILT_ADD`, `VNOP_KQFILT_REMOVE`, `VNOP_MONITOR`.
- Named stream APIs when enabled: `VNOP_GETNAMEDSTREAM`, `VNOP_MAKENAMEDSTREAM`, `VNOP_REMOVENAMEDSTREAM`.

Rename and compound operation behavior:
- `vn_rename()` chooses compound rename when available, otherwise calls `VNOP_RENAMEX` or legacy `VNOP_RENAME`.
- It handles `VFS_RENAME_SECLUDE` legacy fallback through `CN_SECLUDE_RENAME`.
- Successful renames inherit restricted/datavault flags from the destination directory when needed.
- MAC notifications are emitted for normal and swap renames when MACF is enabled.
- `post_rename()` posts directory write/link events, target delete events, and source rename events.
- Compound variants run lookup post-hooks and clean up returned vnodes on non-`EKEEPLOOKING` errors.

AppleDouble compatibility:
- Enabled under `CONFIG_APPLEDOUBLE` for filesystems without native xattrs.
- `xattrfile_remove()` removes stale or forced `._<name>` AppleDouble files, using a 180-second stale threshold for non-empty files based on modify/change time.
- `xattrfile_setattr()` mirrors uid/gid/mode changes onto the AppleDouble companion file.
- Create, mkdir, symlink, compound open, remove, rmdir, and rename paths remove or rename stale companion files as appropriate.
- Linking to an existing `._` AppleDouble file is rejected for non-native-xattr regular files.

Important edge cases:
- Many APIs intentionally default `ctx` to current context, but `VNOP_READ` and `VNOP_WRITE` reject null contexts with `EINVAL`.
- `VNOP_MMAP_CHECK` and `VNOP_VERIFY` treat `ENOTSUP` as non-fatal success in their compatibility contracts.
- `VNOP_BLOCKMAP` caps malformed run lengths to the requested size.
- `vnode_setneedinactive()` marks removed/replaced vnodes for later inactive processing and purges name cache state.
- Authorization caches are invalidated on permission/xattr-relevant mutations.
- `vfs_context_create_with_proc()` uses low-bit tagging in `vc_thread`, so all access goes through `VFS_CONTEXT_GET_THREAD()`.

Overall, `kpi_vfs.c` is the Darwin VFS KPI boundary layer: it shields kernel callers and filesystems from raw operation-vector mechanics, centralizes compatibility behavior, and provides consistent policy, tracing, notification, authorization-cache, and attribute normalization around filesystem operations.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/kpi_vfs.c -->