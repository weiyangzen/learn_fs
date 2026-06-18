# Group Research: group_996_linux_stable_sources_os_linux_linux_stable_fs_fhandle_c_sources_os_l_b679e6cf6497

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fhandle.c -->
# File Research: sources/os/linux/linux-stable/fs/fhandle.c

This file implements the VFS file-handle syscalls: `name_to_handle_at()` encodes a path into a filesystem export handle plus mount ID, and `open_by_handle_at()` decodes such a handle back into an opened file.

Major responsibilities:
- Validate user flags for handle encoding, including `AT_HANDLE_FID`, `AT_HANDLE_CONNECTABLE`, `AT_EMPTY_PATH`, symlink following, and unique mount IDs.
- Call exportfs encode/decode hooks through `exportfs_encode_fh()` and `exportfs_decode_fh_raw()`.
- Copy variable-sized `struct file_handle` payloads safely to and from userspace.
- Resolve the decode anchor from an fd, `AT_FDCWD`, `FD_PIDFS_ROOT`, or `FD_NSFS_ROOT`.
- Enforce permissions for handle decoding, including legacy `CAP_DAC_READ_SEARCH` and newer mount/user-namespace based permission checks.
- Verify connectable handles by checking that decoded dentries are reachable from the supplied root and have valid id mappings.
- Open decoded paths through filesystem-specific export `open()` hooks or `file_open_root()`.

Important design points:
- Encoding rejects filesystems that cannot encode the requested handle type.
- Connectable handles store user-visible type bits (`FILEID_IS_CONNECTABLE`, `FILEID_IS_DIR`) in `handle_type`, then strip those bits before calling filesystem decode logic.
- Decode permission handling is split between optional filesystem export permission hooks and generic `may_decode_fh()`.
- `vfs_dentry_acceptable()` is used as the exportfs acceptability callback and performs subtree/idmapping validation.
- `open_by_handle_at()` follows normal open flag handling, including `O_LARGEFILE` for native syscalls and a compat syscall variant without forced largefile.

Key invariants:
- `handle_bytes` must be nonzero for decode and no larger than `MAX_HANDLE_SZ`.
- Filesystem code must not see VFS/user flag bits embedded in `handle_type`.
- `AT_HANDLE_CONNECTABLE` conflicts with `AT_HANDLE_FID` and `AT_EMPTY_PATH`.
- Relaxed decode permissions require directory-only opens and capability checks sufficient to reach the object through the supplied mount root.
- On overflow or `FILEID_INVALID`, encode reports `-EOVERFLOW` and only copies the fixed handle header back.

External interfaces:
- Defines `name_to_handle_at`, `open_by_handle_at`, and compat `open_by_handle_at`.
- Depends on exportfs operations, mount namespace helpers, pidfs/nsfs roots, VFS open helpers, and userspace copy helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fhandle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/file.c

This file manages per-process file descriptor tables (`struct files_struct` and `struct fdtable`) and the fd-oriented APIs used by open, close, dup, exec, SCM_RIGHTS, pidfd, and syscall fast paths.

Major responsibilities:
- Implement the `file_ref_t` slowpath for safe `struct file` refcount release and saturation/dead-state handling.
- Allocate, expand, duplicate, and free dynamic fd tables and their bitmaps.
- Track open fd bits, close-on-exec bits, full bitmap words, and `next_fd`.
- Allocate fd slots via `get_unused_fd_flags()` and release reserved slots via `put_unused_fd()`.
- Publish files into reserved slots with `fd_install()` while coordinating with concurrent fdtable resize.
- Close individual fds, ranges of fds, and close-on-exec descriptors.
- Provide RCU-safe file lookup helpers: `fget()`, `fget_raw()`, `fdget()`, `fdget_pos()`, task fd lookup, and iteration.
- Implement `dup`, `dup2`, `dup3`, `f_dupfd()`, and fd replacement.
- Install received files from other processes through `receive_fd()` and `receive_fd_replace()`.

Important design points:
- Small fd tables are embedded in `files_struct`; larger tables are allocated separately and freed after RCU grace periods.
- Bitmap sizes are aligned to `BITS_PER_LONG`, and `full_fds_bits` accelerates finding free descriptors.
- `resize_in_progress` coordinates lockless `fd_install()` with fdtable expansion.
- `dup_fd()` handles fd slots that are allocated but not yet populated, preserving the invariant that reserved slots contain `NULL` until `fd_install()`.
- RCU lookup handles `SLAB_TYPESAFE_BY_RCU` reuse by refcounting first, then rechecking the fdtable pointer and slot.
- `fdget()` can borrow a file without taking a ref when the files table is unshared; otherwise it falls back to a normal refcounted lookup.
- `fdget_pos()` conditionally locks `f_pos_lock` for shared seek position correctness.

Key invariants:
- `files->file_lock` protects fd allocation, bitmap mutation, close, dup target replacement, and fdtable replacement.
- A successfully reserved fd has `open_fds` set and `fd[fd] == NULL` until `fd_install()`.
- `fd_install()` consumes the caller's file reference.
- `dup2`/`dup3` return `-EBUSY` if the target fd is reserved but not populated.
- `close_range(CLOSE_RANGE_UNSHARE)` may clone the fdtable with a punched-out closed range before installing it on the task.
- RCU readers must validate that the file pointer and fdtable did not change after acquiring a file reference.

External interfaces:
- Exports fd allocation/installation/closing/lookup APIs, `close_range`, `dup`, `dup2`, `dup3`, `receive_fd`, `iterate_fd`, and file position locking helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/file_attr.c -->
# File Research: sources/os/linux/linux-stable/fs/file_attr.c

This file implements the generic VFS layer for miscellaneous file attributes, bridging legacy ioctl interfaces, the newer `file_getattr`/`file_setattr` syscalls, LSM hooks, and filesystem `fileattr_get`/`fileattr_set` inode operations.

Major responsibilities:
- Translate between legacy `FS_*_FL` flags and `FS_XFLAG_*` xflags.
- Retrieve file attributes through `vfs_fileattr_get()`, including security checks.
- Validate and apply attribute changes through `vfs_fileattr_set()`.
- Marshal `fsxattr` and `file_attr` structures to and from userspace.
- Implement ioctl helpers for `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `FS_IOC_FSGETXATTR`, and `FS_IOC_FSSETXATTR`.
- Implement `file_getattr` and `file_setattr` syscalls with path lookup, `AT_EMPTY_PATH`, and structure-size extensibility.

Important design points:
- `fileattr_set_prepare()` centralizes generic validity checks before filesystem-specific mutation.
- Attribute setting first reads current attributes so unspecified fields can inherit existing state.
- Immutable and append-only changes require `CAP_LINUX_IMMUTABLE`.
- Project ID changes are restricted to the initial user namespace and validated as kernel project IDs.
- Extent-size, COW extent-size, inherited extent-size, and DAX xflags are constrained by file type.
- Legacy ioctl and syscall paths both converge on `vfs_fileattr_set()` and mount write accounting.

Key invariants:
- Filesystems without `fileattr_get` or `fileattr_set` return `-ENOIOCTLCMD`, translated to `-EOPNOTSUPP` for the new syscalls.
- Read-only xflags are masked out when converting user-settable attributes.
- The inode lock is held across current-attribute retrieval, validation, security checks, filesystem mutation, and notification.
- `file_setattr` and ioctl setters must acquire mount write access before mutation.
- Zero extent-size hints clear their corresponding xflag bits.

External interfaces:
- Exports `fileattr_fill_xflags`, `fileattr_fill_flags`, `vfs_fileattr_get`, `vfs_fileattr_set`, and `copy_fsxattr_to_user`.
- Defines syscall entry points `file_getattr` and `file_setattr`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/file_attr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/file_table.c -->
# File Research: sources/os/linux/linux-stable/fs/file_table.c

This file manages global `struct file` allocation, initialization, accounting, freeing, and final `fput()` teardown. It is separate from `file.c`: `file.c` manages descriptor tables, while this file manages the file objects those descriptors point to.

Major responsibilities:
- Maintain global file count accounting and sysctls: `file-nr`, `file-max`, and `nr_open`.
- Allocate normal files, unaccounted internal files, backing files, pseudo files, and cloned files.
- Initialize `struct file` fields, credentials, security blobs, fsnotify mode, read/write capability bits, mappings, and refcounts.
- Support backing files that carry a separate user-visible path and optional security state.
- Tear down files in `__fput()`: fsnotify close, epoll release, locks, LSM release, fasync, filesystem release op, cdev refs, file operations, ownership, path, mount, and credentials.
- Defer final `fput()` through task work where possible, or delayed work when needed.
- Initialize file slabs and the default global max-files value at boot.

Important design points:
- The `filp` and `bfilp` caches are `SLAB_TYPESAFE_BY_RCU`, so file initialization sets `f_ref` last.
- `alloc_empty_file()` enforces `file-max` for unprivileged users; internal no-account variants set `FMODE_NOACCOUNT`.
- Pseudo files allocate pseudo dentries and default to suppressing fsnotify events.
- `fput()` defers cleanup unless synchronous variants are requested.
- Kernel threads should use synchronous fput only when carefully justified, because normal delayed fput can interact with unmount dependencies.

Key invariants:
- Callers assigning writable mounts to newly allocated files are responsible for balancing mount writer counts.
- `FMODE_OPENED` gates the full release path; unopened files can be freed directly.
- Backing files must free security state and drop their stored user path.
- `fput_close()` and `fput_close_sync()` are optimized for known-last-reference close paths.
- `files_init()` must create slab caches before file allocation can occur.

External interfaces:
- Exports file allocation helpers, backing file helpers, `fput`, `__fput_sync`, `flush_delayed_fput`, and max-file accessors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/file_table.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/filesystems.c -->
# File Research: sources/os/linux/linux-stable/fs/filesystems.c

This file maintains the global registry of filesystem types known to the kernel and exposes lookup, registration, module autoloading, `/proc/filesystems`, and the legacy `sysfs(2)` filesystem queries.

Major responsibilities:
- Register and unregister `struct file_system_type` instances.
- Validate filesystem parameter descriptions during registration.
- Maintain the linked list of filesystems under `file_systems_lock`.
- Manage module references for looked-up filesystem types.
- Implement `get_fs_type()` lookup with optional `request_module("fs-%s")`.
- Enforce subtype support for names containing a dot.
- List block-device-backed filesystem names for init-time consumers.
- Expose `/proc/filesystems` when procfs is enabled.
- Implement the historical `sysfs` syscall variants when configured.

Important design points:
- The registry is a simple linked list protected by an rwlock.
- `get_filesystem()` assumes the caller already owns a valid module reference and increments it.
- `__get_fs_type()` takes a module reference while still protected by the registry lock.
- Registering rejects duplicate names, names containing `.`, and already-linked filesystem types.
- Unregistering unlinks the filesystem and waits for an RCU grace period before returning.

Key invariants:
- Filesystem structures must not be freed until successfully unregistered.
- A filesystem can be inspected without the lock only after a module reference has been obtained.
- Subtyped names are accepted only when the base filesystem advertises `FS_HAS_SUBTYPE`.
- Module autoload success is not sufficient; the registry is checked again after `request_module()`.

External interfaces:
- Exports `register_filesystem`, `unregister_filesystem`, and `get_fs_type`.
- Provides `/proc/filesystems`, `list_bdev_fs_names()`, and optional `sysfs(2)`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/filesystems.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/Kconfig

This Kconfig entry defines the build option for the FreeVxFS filesystem driver.

Major responsibilities:
- Declares `CONFIG_VXFS_FS` as a tristate option named "FreeVxFS file system support".
- Requires block-device support through `depends on BLOCK`.
- Selects `BUFFER_HEAD`, matching the driver's buffer-head based read path.
- Documents the driver as read-only support for VERITAS VxFS-compatible filesystems.
- Notes tested compatibility with SCO UnixWare and HP-UX VxFS variants.
- Clarifies that the mount filesystem type is `vxfs` even though the module is `freevxfs`.

Important design points:
- The help text explicitly frames the driver as format compatibility, not full vendor VxFS functionality.
- It calls out version support for VxFS 2, 3, and 4.
- It warns that OS-specific VxFS implementations may differ by endianness and superblock offset, which matches the superblock probing code.

Key invariants:
- The driver is not a write-capable filesystem.
- The module name and mount type differ: module `freevxfs`, filesystem type `vxfs`.

External interfaces:
- Produces `CONFIG_VXFS_FS`, used by the Makefile and build system.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/Makefile

This Makefile wires the FreeVxFS driver into the kernel build.

Major responsibilities:
- Builds `freevxfs.o` when `CONFIG_VXFS_FS` is enabled.
- Defines the object list that composes the module/built-in driver.

Included objects:
- `vxfs_bmap.o` for logical-to-physical block mapping.
- `vxfs_fshead.o` for fileset header discovery.
- `vxfs_immed.o` for immediate-data reads.
- `vxfs_inode.o` for inode decoding and VFS inode setup.
- `vxfs_lookup.o` for directory lookup and readdir.
- `vxfs_olt.o` for Object Location Table discovery.
- `vxfs_subr.o` for shared readpage/bmap helpers.
- `vxfs_super.o` for mount, superblock, module, and cache setup.

Key invariants:
- No write-path object is present, matching the read-only driver design.
- The aggregate object is named `freevxfs.o`, while the runtime filesystem type is registered as `vxfs`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs.h -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs.h

This header defines FreeVxFS superblock structures, byte-order helpers, VxFS mode/type constants, inode organization constants, and the superblock private-data accessor.

Major responsibilities:
- Define the VxFS superblock magic, root inode number, and free extent array size.
- Represent filesystem byte order with `VXFS_BO_LE` and `VXFS_BO_BE`.
- Define bitwise disk integer types `__fs16`, `__fs32`, and `__fs64`.
- Declare the on-disk `struct vxfs_sb` fields used by the driver.
- Declare `struct vxfs_sb_info`, the in-core VxFS superblock private state.
- Provide endian conversion helpers that depend on the mounted filesystem's byte order.
- Define VxFS file mode/type bits, including regular Unix file types and VxFS internal structural inode types.
- Define inode organization types: none, ext4-style extents, immediate data, and typed extents.
- Provide macros to test VxFS inode type and organization.

Important design points:
- The on-disk superblock definition intentionally stops after the fields this driver needs.
- `vxfs_sb_info` stores raw superblock buffer state plus discovered structural inodes, OLT location, fileset header inode, initial inode-list extent, and byte order.
- The driver supports both UnixWare-style little-endian and HP-UX-style big-endian layouts through per-superblock conversion helpers.
- Internal VxFS inode types are separated from regular VFS file types and should not be exposed as normal mode bits.

Key invariants:
- `VXFS_SUPER_MAGIC` must match after applying the detected byte order.
- `VXFS_ROOT_INO` is inode 2.
- Type checks mask with `VXFS_TYPE_MASK`.
- Organization checks use `vii_orgtype`, and unsupported organization types are rejected by mapping code.

External interfaces:
- Provides shared definitions consumed by all FreeVxFS implementation files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_bmap.c -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_bmap.c

This file implements FreeVxFS logical-to-physical block mapping for internal reads and VFS address-space operations.

Major responsibilities:
- Map ext4-style VxFS extents with direct extent descriptors and one indirect extent path.
- Map typed extents, including recursive traversal through indirect typed extent blocks.
- Reject or warn about unsupported immediate, none, and external-device typed extent organizations.
- Provide the public internal mapper `vxfs_bmap1()`.

Important design points:
- `vxfs_bmap_ext4()` treats VxFS "ext4" organization as a traditional direct-plus-indirect extent layout, unrelated to Linux ext4.
- `vxfs_bmap_typed()` walks inline typed extent descriptors and delegates indirect descriptors to `vxfs_bmap_indir()`.
- Typed extent headers encode type in the high bits and logical offset in the low bits.
- `VXFS_TYPED_DEV4` descriptors are recognized only enough to report unsupported external-device mappings.
- The mapper returns physical block zero on failure, which downstream read helpers treat as I/O failure or unmapped data.

Key invariants:
- All multi-byte on-disk fields are converted with the superblock byte-order helpers.
- Unsupported organization types must not be mapped.
- Indirect extent size larger than the filesystem block size is rejected.
- Unknown typed extent types trigger `BUG()`, reflecting an assumption that mounted metadata was already coherent enough for read-only traversal.

External interfaces:
- Exports `vxfs_bmap1()` within the driver through `vxfs_extern.h`.
- Used by `vxfs_bread()`, `vxfs_getblk()`, and generic bmap/readpage paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_dir.h -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_dir.h

This header defines the on-disk FreeVxFS directory block and directory entry formats.

Major responsibilities:
- Declare `struct vxfs_dirblk`, the per-directory-block header containing free-space and hash metadata.
- Define `VXFS_NAMELEN` as the maximum directory entry name length.
- Declare `struct vxfs_direct`, the VxFS directory entry format with inode, record length, name length, hash link, and name bytes.
- Define directory entry alignment and size helpers.
- Define `VXFS_DIRBLKOV()` to compute directory block header overhead using the mounted filesystem byte order.

Important design points:
- The directory hash chain data exists in the format but the Linux driver does not use it for lookup; it scans directory entries linearly.
- Directory records are padded to four-byte boundaries.
- Directory block overhead depends on the number of hash chains in the block header.

Key invariants:
- Names longer than `VXFS_NAMELEN` are rejected by lookup.
- Directory iteration must skip the block header overhead at the start of each filesystem block.
- `d_reclen == 0` marks the remainder of a directory block as unusable for scanning.

External interfaces:
- Used by `vxfs_lookup.c` for lookup and readdir.
- Included by `vxfs_super.c` for statfs name length reporting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_extern.h -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_extern.h

This header centralizes cross-file prototypes for the FreeVxFS driver.

Major responsibilities:
- Declare block mapping, fileset header, inode, lookup, Object Location Table, and shared page/buffer helper interfaces.
- Expose FreeVxFS address-space operations for normal and immediate-data files.
- Expose directory inode/file operations for VFS inode setup.
- Keep implementation files decoupled while avoiding broader header dependencies.

Important design points:
- The prototypes mirror the Makefile object split: bmap, fshead, inode, lookup, OLT, subroutines, and superblock code.
- Most functions are internal to the FreeVxFS driver even though declared with `extern`; they are not exported kernel symbols.
- The header distinguishes structural inode lookup (`vxfs_stiget`), block/extent based lookup (`vxfs_blkiget`), and ordinary inode lookup (`vxfs_iget`).

Key invariants:
- Callers must use the appropriate inode lookup path for the phase of mount: raw/block reads during superblock setup, pagecache-backed reads after inode lists are established.
- `vxfs_get_page()` results must be released with `vxfs_put_page()`.

External interfaces:
- Internal driver API only; no module exports are declared here.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_fshead.c -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_fshead.c

This file reads VxFS fileset headers and establishes the inode-list inodes needed for normal inode lookup.

Major responsibilities:
- Read the fileset header inode from the initial inode-list extent discovered via the OLT.
- Validate that the fileset header inode has the VxFS fileset-header type.
- Read the structural and primary fileset headers from that inode.
- Locate and validate the structural inode list inode.
- Locate and validate the primary inode list inode.
- Store the resulting inode pointers in `vxfs_sb_info`.

Important design points:
- Fileset headers are read through `vxfs_bread()` from a fake fileset header inode.
- The driver copies on-disk header bytes into allocated memory, uses the needed fields, and frees the copies after setup.
- Structural metadata is read first so that ordinary inode-list lookup can proceed through `vxfs_stiget()`.
- Errors unwind all acquired inodes and allocated fileset header buffers.

Key invariants:
- `vsi_fship` must decode as `VXFS_IFFSH`.
- `vsi_stilist` and `vsi_ilist` must decode as `VXFS_IFILT`.
- Fileset header fields must be byte-swapped through `fs32_to_cpu()`.
- Successful mount setup requires both structural and primary inode list inodes.

External interfaces:
- Provides `vxfs_read_fshead()` for `vxfs_fill_super()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_fshead.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_fshead.h -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_fshead.h

This header defines the VxFS fileset header structure fields used by the FreeVxFS driver.

Major responsibilities:
- Declare `struct vxfs_fsh`, the on-disk fileset header subset.
- Provide fields for fileset version/index, modification time, inode counts, allocation units, quota, maximum inode, IAU inode, inode-list inode numbers, and link-count table inode.
- Document that additional fields exist on disk but vary across VxFS versions and ports.

Important design points:
- The driver intentionally models only the stable fields needed to discover inode lists.
- `fsh_ilistino[0]` is used by `vxfs_read_fshead()` to find structural and primary inode-list inodes.
- All numeric fields are VxFS disk-endian values and must be converted through the mounted superblock's byte-order helpers.

Key invariants:
- This structure is not a complete vendor VxFS fileset header.
- Consumers must not assume fields beyond the declared subset are present or uniform across versions.

External interfaces:
- Used only by `vxfs_fshead.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_fshead.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_immed.c -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_immed.c

This file implements address-space reads for VxFS immediate-data inodes, whose file contents are stored directly inside the inode body.

Major responsibilities:
- Provide `vxfs_immed_read_folio()` to copy bytes from `vii_immed.vi_immed` into the requested folio.
- Mark the folio uptodate and unlock it after copying.
- Publish `vxfs_immed_aops` for immediate files, directories, and immediate symlinks where applicable.

Important design points:
- The read path does not perform block mapping; it reads from the in-core inode's immediate data buffer.
- The implementation iterates over all pages in the folio and copies a page at a time from the immediate area.
- Immediate symlinks may bypass this address-space operation and use `simple_symlink_inode_operations` with `i_link` pointing directly into the immediate buffer.

Key invariants:
- The folio is locked on entry and unlocked before return.
- Immediate data size is bounded by the inode immediate area declared in `vxfs_inode.h`.
- This is read-only support; no dirty/writeback path is provided.

External interfaces:
- Defines `vxfs_immed_aops`, referenced by `vxfs_iget()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_immed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_inode.c -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_inode.c

This file decodes VxFS disk inodes into Linux VFS inodes and selects the correct VFS operations for regular files, directories, symlinks, and special files.

Major responsibilities:
- Translate VxFS mode/type bits into Linux `umode_t`.
- Copy and endian-convert stable disk inode fields into `struct vxfs_inode_info`.
- Read inodes directly from a known extent during early mount setup.
- Read inodes through structural or primary inode-list files after metadata setup.
- Set VFS inode ownership, size, times, blocks, generation, mapping operations, file operations, inode operations, and special device numbers.
- Handle immediate-data files and symlinks.
- Evict VxFS inodes by truncating pagecache and clearing the VFS inode.

Important design points:
- `vxfs_blkiget()` uses buffer-cache reads and is intended only during `read_super` style setup before normal inode lists are available.
- `__vxfs_iget()` uses the pagecache against the inode-list inode, allowing normal cached reads.
- `vxfs_stiget()` reads from the structural inode list; `vxfs_iget()` reads from the primary inode list and uses `iget_locked()`.
- Organization-specific data is copied without endian conversion because the active union layout depends on `vii_orgtype`; mapping code converts fields when interpreting them.
- Immediate symlinks terminate the inline link buffer and point `i_link` into the inode-private immediate data.

Key invariants:
- New VFS inodes must remain locked until fully initialized or failed via `iget_failed()`.
- Regular files use `generic_ro_fops`; directories use FreeVxFS lookup/readdir operations.
- Non-immediate symlinks use page-backed symlink operations and disallow highmem.
- Special inodes use `old_decode_dev(vii_rdev)`.
- Eviction does not write data because the filesystem is read-only.

External interfaces:
- Provides `vxfs_blkiget`, `vxfs_stiget`, `vxfs_iget`, `vxfs_evict_inode`, and optional diagnostic inode dumping.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_inode.h -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_inode.h

This header defines VxFS on-disk inode structures, extent organization formats, typed extent formats, and the in-core inode-private structure.

Major responsibilities:
- Define VxFS inode size and counts for direct, indirect, immediate, and typed extent descriptors.
- Declare immediate-data, ext4-style extent, typed extent, and typed-dev4 descriptor structures.
- Declare the on-disk `struct vxfs_dinode`.
- Declare the in-core `struct vxfs_inode_info`, embedding `struct inode`.
- Provide convenience macros for union fields and the `VXFS_INO()` container helper.

Important design points:
- VxFS supports multiple inode data organizations, represented by a union in both disk and memory forms.
- Typed extent headers encode extent type in the top byte and logical offset in the lower 56 bits.
- The in-core inode stores already-converted common scalar fields, while organization-specific unions remain in disk form until interpreted.
- The inode cache is configured in `vxfs_super.c` to allow safe usercopy of the immediate-data region.

Key invariants:
- `VXFS_ISIZE` is 256 bytes and is used for inode-list block/page offset calculations.
- Immediate data is `VXFS_NIMMED` bytes.
- `VXFS_TYPED_PER_BLOCK(sb)` depends on the mounted block size.
- `VXFS_INO()` is the canonical conversion from VFS inode to VxFS inode-private data.

External interfaces:
- Used by all FreeVxFS implementation files that inspect or allocate inodes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_lookup.c -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_lookup.c

This file implements FreeVxFS directory lookup and directory iteration.

Major responsibilities:
- Define directory inode operations with `.lookup = vxfs_lookup`.
- Define directory file operations with generic seek/read, `vxfs_readdir`, and generic lease handling.
- Scan VxFS directory blocks linearly to find a matching directory entry.
- Resolve a dentry name to an inode number and then to a VFS inode.
- Emit `.` and `..` plus directory entries through `dir_emit()`.

Important design points:
- The driver does not use the on-disk directory hash chains; it scans records page by page.
- Directory block headers are skipped at filesystem block boundaries using `VXFS_DIRBLKOV()`.
- Directory scanning uses `vxfs_get_page()` and releases mapped pages with `vxfs_put_page()`.
- `ctx->pos` uses low bits to distinguish synthetic dot entries from real on-disk aligned positions.
- Directory entry types are emitted as `DT_UNKNOWN`, except synthetic `..` is emitted as `DT_DIR`.

Key invariants:
- Lookup rejects names longer than `VXFS_NAMELEN`.
- `d_reclen == 0` advances to the next filesystem block.
- Empty entries with `d_ino == 0` are skipped.
- Name comparison requires exact length and byte match.
- Found inodes are returned through `d_splice_alias()`.

External interfaces:
- Provides `vxfs_dir_inode_ops` and `vxfs_dir_operations` for `vxfs_iget()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_olt.c -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_olt.c

This file reads and parses the VxFS Object Location Table, which tells the driver where key filesystem metadata objects live.

Major responsibilities:
- Convert OLT block addresses from VxFS block size to current superblock block units.
- Read the OLT extent from disk.
- Validate the OLT magic number.
- Parse OLT entries to find the fileset header inode and initial inode-list extent.
- Store discovered values in `vxfs_sb_info`.

Important design points:
- Only the first OLT extent is supported; `vsi_oltsize > 1` is rejected with a notice.
- The parser walks variable-sized OLT records using each record's `olt_size`.
- Only the `VXFS_OLT_FSHEAD` and `VXFS_OLT_ILIST` records are acted upon; other record types are ignored.
- The helper functions assert that `vsi_fshino` and `vsi_iext` were not already set.

Key invariants:
- OLT magic must match `VXFS_OLT_MAGIC` after byte-order conversion.
- Successful parsing requires both a fileset header inode number and an initial inode-list extent.
- On failure, the buffer head is released and `-EINVAL` is returned.

External interfaces:
- Provides `vxfs_read_olt()` for `vxfs_fill_super()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_olt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_olt.h -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_olt.h

This header defines VxFS Object Location Table constants and record structures.

Major responsibilities:
- Define the OLT magic number.
- Enumerate OLT record types: free, fileset header, current usage table, inode list, device config, and superblock/log/OLT inode records.
- Declare the OLT header structure.
- Declare common, free, inode-list, current-usage-table, superblock/log, device, and fileset-header OLT entry formats.

Important design points:
- The OLT is a metadata directory for locating filesystem-wide internal objects.
- FreeVxFS uses only a subset of OLT records during mount, mainly fileset header and initial inode-list records.
- Replica fields are represented in the structures, but the implementation uses the primary entries.

Key invariants:
- Every variable OLT record begins with type and size fields compatible with `struct vxfs_oltcommon`.
- All fields are on-disk endian and require `fs32_to_cpu()` before use.
- OLT parsing depends on valid `olt_size` fields to advance through the extent.

External interfaces:
- Used by `vxfs_olt.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_olt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_subr.c -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_subr.c

This file provides shared FreeVxFS pagecache and buffer-head helpers for reading file data and metadata.

Major responsibilities:
- Define normal VxFS address-space operations with `read_folio` and `bmap`.
- Read and kmap pages from an address space through `vxfs_get_page()`.
- Release pages through `vxfs_put_page()`.
- Read a logical block of an inode into a buffer head through `vxfs_bread()`.
- Map logical file blocks to physical blocks through `vxfs_getblk()`.
- Implement synchronous folio reads using `block_read_full_folio()`.
- Implement `bmap` using `generic_block_bmap()`.

Important design points:
- `vxfs_getblk()` uses `vxfs_bmap1()` and never allocates blocks; `create` is ignored because the filesystem is read-only.
- A failed block mapping returns `-EIO`.
- `vxfs_bread()` reads physical block zero if `vxfs_bmap1()` fails, so callers must treat failed metadata reads carefully.
- Page checking is stubbed out in comments, indicating no active directory/page validation layer.

Key invariants:
- Pages returned by `vxfs_get_page()` are kmap'ed and must be released with `vxfs_put_page()`.
- Normal file reads always go through block mapping; immediate files use `vxfs_immed_aops` instead.
- No writeback or block allocation operations are provided.

External interfaces:
- Provides `vxfs_aops`, `vxfs_get_page`, `vxfs_put_page`, and `vxfs_bread`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_super.c -->
# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_super.c

This file implements FreeVxFS module setup, filesystem registration, superblock probing, mount initialization, statfs, inode cache management, and unmount cleanup.

Major responsibilities:
- Register the `vxfs` filesystem type and module aliases.
- Create and destroy the `vxfs_inode` slab cache.
- Allocate and free VxFS inodes through superblock operations.
- Release superblock-private resources on unmount.
- Report basic filesystem stats through `statfs`.
- Force mounts and reconfigurations to read-only.
- Probe possible VxFS superblock locations and byte orders.
- Read the OLT, fileset headers, inode lists, and root inode during mount.
- Create the root dentry.

Important design points:
- The driver probes block 1 for little-endian UnixWare-style VxFS and block 8 for big-endian HP-UX-style VxFS.
- The initial block size is set to the kernel minimum, then the final block size is taken from the VxFS superblock.
- Mount setup proceeds in dependency order: superblock, OLT, fileset headers, inode lists, root inode.
- `vxfs_reconfigure()` syncs the filesystem and forces `SB_RDONLY`.
- The inode cache is created with a usercopy-safe region covering inline immediate data.

Key invariants:
- The mounted filesystem is always read-only.
- Supported VxFS versions are 2 through 4.
- `sbp->s_fs_info` must contain a valid `vxfs_sb_info` before OLT and fileset header parsing.
- On mount failure, buffer heads, private superblock memory, and any acquired metadata inodes are released.
- Module cleanup unregisters the filesystem and waits for RCU inode frees before destroying the inode cache.

External interfaces:
- Registers filesystem type `vxfs`.
- Provides module init/exit functions and superblock operations used by VFS mount/unmount paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/freevxfs/vxfs_super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fs-writeback.c -->
# File Research: sources/os/linux/linux-stable/fs/fs-writeback.c

This file is the VFS writeback engine for dirty inode and dirty page-cache writeout. It schedules and performs data writeback against backing devices, superblocks, inodes, and cgroup writeback domains; inode metadata writeout is coordinated here but filesystem-specific inode serialization happens through `s_op->write_inode()`.

Major responsibilities:
- Define and queue `wb_writeback_work` items for `struct bdi_writeback`.
- Maintain dirty inode lists: `b_dirty`, `b_io`, `b_more_io`, `b_dirty_time`, and cgroup attached lists.
- Wake and run flusher work for explicit writeback, background thresholds, periodic old-data flushing, dirtytime expiration, and start-all requests.
- Move expired dirty inodes into dispatch queues and group/sort writeback by superblock.
- Write back individual inodes through `do_writepages()`, optional data wait, lazytime handling, dirty flag clearing, and `write_inode()`.
- Requeue inodes after writeback based on remaining dirty pages, skipped pages, dirtytime state, or clean state.
- Implement sync-facing APIs: `writeback_inodes_sb*`, `try_to_writeback_inodes_sb`, `sync_inodes_sb`, `write_inode_now`, and `sync_inode_metadata`.
- Track inodes under writeback on each superblock for `sync(2)` wait semantics.
- Mark inodes dirty through `__mark_inode_dirty()`, including filesystem dirty notifications and dirtytime behavior.
- Support cgroup writeback ownership, writeback domain splitting, foreign-dirtier detection, and asynchronous inode writeback-domain switching.

Important design points:
- Writeback work is per `bdi_writeback`, not only per block device; cgroup writeback can create multiple writeback domains per backing device.
- `wb_io_lists_populated()` and `wb_io_lists_depopulated()` maintain `WB_has_dirty_io` and aggregate BDI bandwidth accounting.
- Dirtytime inodes are deliberately excluded from ordinary dirty-IO wakeups until expiration or sync requires them.
- `queue_io()` batches expired inodes from delaying queues into `b_io`, preserving old-first writeback and optionally sorting by superblock.
- `writeback_sb_inodes()` temporarily drops `wb->list_lock` while doing actual inode I/O, then re-locks and requeues carefully.
- `WB_SYNC_ALL` avoids livelock by tagging and syncing the current dirty set in one large pass.
- `wait_sb_inodes()` waits for pages already under writeback even when the inode is no longer dirty.
- Cgroup writeback uses inode ownership heuristics and Boyer-Moore style majority tracking to switch inodes to the dominant writing memcg over time.
- Inode wb switching is asynchronous, RCU-synchronized, and coordinated with `wb_switch_rwsem` to avoid sync missing moved inodes.

Key invariants:
- `wb->list_lock` protects writeback lists; `inode->i_lock` protects inode dirty/sync state; lock ordering is carefully managed.
- Inodes with `I_FREEING`, `I_WILL_FREE`, or `I_NEW` are not normal flusher targets.
- `I_SYNC` pins an inode during writeback and is cleared through `inode_sync_complete()`, which wakes waiters.
- Dirty flag clearing in `__writeback_single_inode()` pairs memory barriers with `__mark_inode_dirty()` to avoid losing concurrent dirtying.
- `I_DIRTY_TIME` cannot be combined with `I_DIRTY_PAGES` in a single `__mark_inode_dirty()` call.
- Only hashed inodes, plus block-device inodes, are added to dirty lists.
- Sync of a superblock requires `s_umount` to be held and serializes waiters through `s_sync_lock`.
- Cgroup writeback must not switch DAX inodes and must flush in-flight switches during superblock teardown.

External interfaces:
- Exports writeback and sync helpers, dirty marking, cgroup writeback hooks, inode writeback-list helpers, and tracepoints.
- Integrates with backing-dev writeback workers, memory cgroups, pagecache tags, block plugging, superblock operations, and vm sysctl `dirtytime_expire_seconds`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fs-writeback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fs_context.c -->
# File Research: sources/os/linux/linux-stable/fs/fs_context.c

This file implements the VFS filesystem context abstraction used for mounting, submounting, remount/reconfigure, option parsing, logging, duplication, and cleanup.

Major responsibilities:
- Parse common superblock flags such as `ro`, `rw`, `sync`, `async`, `dirsync`, `lazytime`, and `mand`.
- Parse a generic `source` parameter when accepted by the filesystem.
- Route mount parameters through common VFS parsing, LSM parsing, filesystem-specific parsing, and source fallback.
- Parse monolithic comma-separated mount option strings.
- Allocate filesystem contexts for mounts, submounts, and reconfiguration.
- Duplicate contexts through filesystem and LSM hooks.
- Store context log messages in a bounded ring buffer or print directly.
- Free contexts, security options, namespace references, credentials, source strings, logs, and filesystem references.
- Clean a used context into an awaiting-reconfiguration state and lazily finish reinitialization.

Important design points:
- `fs_context` captures filesystem type, credentials, net namespace, user namespace, root dentry for reconfigure, superblock flags, security state, source, and filesystem-private state.
- Mount contexts use the caller's user namespace; submount and reconfigure contexts inherit from the referenced superblock.
- Parameter parsing first handles VFS-wide flags, then lets LSMs consume or reject options before filesystem parsing.
- `vfs_dup_fs_context()` copies the structure but resets owned private pointers before calling filesystem `dup()` and LSM duplication.
- `vfs_clean_context()` intentionally performs only non-failing cleanup after a successful mount/reconfigure and defers fallible reinitialization to `finish_clean_context()`.

Key invariants:
- `fc->fs_type` holds a filesystem module reference until `put_fs_context()`.
- `fc->root` pins an active superblock for reconfiguration and is released through `deactivate_super()` or `deactivate_locked_super()`.
- `fc->need_free` controls whether filesystem-specific `ops->free()` is called.
- `fc->source` ownership is transferred from `fs_parameter` by nulling `param->string`.
- Unknown parameters become contextual `invalf()` errors after VFS, LSM, filesystem, and source parsing decline them.

External interfaces:
- Exports parsing helpers, context allocation helpers, duplication, logging, and `put_fs_context()`.
- Used by modern mount APIs and filesystem `init_fs_context` implementations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fs_context.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fs_dirent.c -->
# File Research: sources/os/linux/linux-stable/fs/fs_dirent.c

This file provides small generic conversion helpers between filesystem on-disk file type values, Linux directory entry `DT_*` values, and inode mode bits.

Major responsibilities:
- Map `FT_*` on-disk filesystem file types to `DT_*` dirent file types.
- Map `DT_*` values to `FT_*` on-disk filesystem file types.
- Convert `umode_t` file modes to on-disk `FT_*` values.
- Convert `umode_t` file modes directly to `DT_*` values.

Important design points:
- Unknown or out-of-range on-disk file types degrade to `DT_UNKNOWN`.
- The `DT_*` to `FT_*` table is sparse; unspecified values default to `FT_UNKNOWN`.
- `fs_umode_to_ftype()` uses `S_DT(mode)` as the bridge from inode mode to dirent type.

Key invariants:
- `filetype >= FT_MAX` must not index the conversion table.
- Unsupported mode/type values are represented as unknown rather than guessed.
- Helpers are context-independent and perform no allocation or locking.

External interfaces:
- Exports GPL-only helpers `fs_ftype_to_dtype`, `fs_umode_to_ftype`, and `fs_umode_to_dtype`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fs_dirent.c -->