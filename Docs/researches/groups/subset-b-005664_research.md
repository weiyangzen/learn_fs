# subset-b-005664 Research

Grouped source research for core VFS descriptor, file attribute, filesystem registration, mount-context, directory-type, writeback code, plus the FreeVxFS read-only filesystem driver. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fhandle.c -->
# sources/distributed-fs/ceph-client/fs/fhandle.c

## Purpose

`sources/distributed-fs/ceph-client/fs/fhandle.c` implements the VFS file-handle syscalls `name_to_handle_at()` and `open_by_handle_at()`. It bridges path lookup, filesystem export operations, mount identity reporting, and permission-gated decoding of persistent file handles back into `struct path` and `struct file` objects. The complete 462-line file was read for this report.

## Important APIs, Types, and Functions

Key entry points are `SYSCALL_DEFINE5(name_to_handle_at)`, `SYSCALL_DEFINE3(open_by_handle_at)`, and the compat `open_by_handle_at` variant. Internal helpers include `do_sys_name_to_handle()`, `get_path_anchor()`, `vfs_dentry_acceptable()`, `may_decode_fh()`, `handle_to_path()`, `do_handle_to_path()`, `file_open_handle()`, and `do_handle_open()`. The code depends on `struct file_handle`, `struct path`, `struct export_operations`, and `struct handle_to_path_ctx` from VFS internals.

## Control Flow

`name_to_handle_at()` validates user flags, performs `filename_lookup()`, then calls `exportfs_encode_fh()` through `do_sys_name_to_handle()`. It returns mount IDs in either legacy integer or unique `u64` form, copies the variable-size handle back to userspace, and maps handle overflow to `-EOVERFLOW`. `open_by_handle_at()` reads and validates the userspace handle, anchors decoding to an fd, cwd, pidfs root, or nsfs root, checks export permission hooks or generic capability policy, decodes through `exportfs_decode_fh_raw()`, and opens the resulting path through filesystem `->open` or `file_open_root()`.

## State and Persistence Behavior

The persistent state is external: file handles are stable filesystem export identifiers, not state owned by this file. Runtime state is stack/local allocation plus path and mount references. Permission state is derived from capabilities, mount namespaces, idmapped mounts, and encoded handle flags such as connectable and directory-only.

## Dependencies and Integration Points

This code integrates with exportfs, namei lookup, namespace roots, mount internals, idmapping checks, file opening, `FD_ADD`, and user-copy APIs. Filesystems expose behavior through `s_export_op`, optionally overriding generic decode permission or open handling.

## Risks and Edge Cases

Risk concentrates around permission regressions for handle decoding, disconnected dentries, connectable handle subtree checks, user namespace id mappings, and malformed handle sizes/types. `vfs_dentry_acceptable()` deliberately performs racy path ancestry checks without `rename_lock`; that is acceptable for the documented approximation but sensitive to policy changes.

## Test Signals

Useful tests include xfstests/exportfs coverage for handle encode/decode, capability matrix tests for `CAP_DAC_READ_SEARCH` and `CAP_SYS_ADMIN`, malformed userspace handle tests, AT flag validation, idmapped mount cases, connectable directory-only decoding, and filesystem-specific NFS-export handle round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fhandle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/file.c -->
# sources/distributed-fs/ceph-client/fs/file.c

## Purpose

`sources/distributed-fs/ceph-client/fs/file.c` manages per-process `files_struct` descriptor tables and common fd lifecycle syscalls. It covers fdtable allocation/growth, descriptor bitmaps, close/close-range, RCU-safe file lookup, fd installation, duplication, close-on-exec, received-fd installation, and iteration. The complete 1533-line file was read for this report.

## Important APIs, Types, and Functions

Exported or syscall-facing APIs include `__file_ref_put()`, `dup_fd()`, `get_unused_fd_flags()`, `put_unused_fd()`, `fd_install()`, `close_fd()`, `close_range()`, `file_close_fd()`, `do_close_on_exec()`, `get_file_rcu()`, `get_file_active()`, `fget()`, `fget_raw()`, `fget_task()`, `fget_task_next()`, `fdget()`, `fdget_raw()`, `fdget_pos()`, `__f_unlock_pos()`, `set_close_on_exec()`, `get_close_on_exec()`, `replace_fd()`, `receive_fd()`, `receive_fd_replace()`, `dup3`, `dup2`, `dup`, `f_dupfd()`, and `iterate_fd()`. Core structures are `files_struct`, `fdtable`, `file_ref_t`, fd bitmaps, and `struct fd`.

## Control Flow

Fd allocation uses `alloc_fd()` to scan `open_fds` and `full_fds_bits`, expand tables under `files->file_lock` when necessary, mark the slot open, and leave `fdt->fd[fd]` NULL until `fd_install()`. Growth allocates a new fdtable outside the spinlock, synchronizes with lockless installers via RCU and barriers, copies descriptors/bitmaps, then publishes with `rcu_assign_pointer()`. Close paths clear the fd slot under the lock and then call `filp_close()` outside it. Duplication and replacement expand the table, get a reference on the source file, atomically replace the target slot, and close the displaced file after dropping the lock.

## State and Persistence Behavior

State is per-task or shared-thread-group runtime state, not file-backed persistence. `files_struct` carries an atomic share count, resize state, waitqueue, next-fd hint, embedded small fdtable, and optional expanded RCU-freed tables. `struct file` lifetimes are protected by file refcounts and SLAB_TYPESAFE_BY_RCU validation. Close-on-exec state is bitmap-backed and consumed by `do_close_on_exec()` during exec.

## Dependencies and Integration Points

This file integrates with syscall wrappers, `rlimit(RLIMIT_NOFILE)`, `sysctl_nr_open`, RCU, speculative-execution index masking, socket receive hooks, LSM `security_file_receive()`, `filp_close()`, process task locking, `close_range` unshare semantics, and the Rust file API expectations documented in comments.

## Risks and Edge Cases

The riskiest areas are fdtable resize/install races, reserved-but-uninstalled fd slots, RCU file reuse, descriptor-table sharing during close-range unshare, and memory ordering between reference acquisition and pointer validation. The code intentionally returns `-EBUSY` for `dup2` races against userspace fd reservation. Changes to barriers or bitmap invariants can become use-after-free, leaked file references, or fd aliasing bugs.

## Test Signals

Signals include LTP and kselftest coverage for `dup*`, `close_range`, `SCM_RIGHTS`, `pidfd_getfd`, exec close-on-exec, fd exhaustion, concurrent open/dup/close stress, KCSAN/lockdep for fdtable resize races, and syzkaller coverage for malformed fd inputs and shared `files_struct` corner cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/file_attr.c -->
# sources/distributed-fs/ceph-client/fs/file_attr.c

## Purpose

`sources/distributed-fs/ceph-client/fs/file_attr.c` implements generic VFS helpers and syscalls for miscellaneous file attributes, bridging legacy FS flags, XFS-style `fsxattr`, and the newer extensible `file_attr` ABI. The complete 486-line file was read for this report.

## Important APIs, Types, and Functions

Exported helpers are `fileattr_fill_xflags()`, `fileattr_fill_flags()`, `vfs_fileattr_get()`, `copy_fsxattr_to_user()`, and `vfs_fileattr_set()`. Ioctl helpers are `ioctl_getflags()`, `ioctl_setflags()`, `ioctl_fsgetxattr()`, and `ioctl_fssetxattr()`. Syscalls are `file_getattr` and `file_setattr`. Internal conversion and validation helpers include `fileattr_to_file_attr()`, `file_attr_to_fileattr()`, `copy_fsxattr_from_user()`, and `fileattr_set_prepare()`.

## Control Flow

Get paths call the filesystem `inode_operations->fileattr_get()` after LSM approval, then translate the resulting `struct file_kattr` into the requested user ABI. Set paths copy and validate user input, acquire write access to the mount, verify ownership/capability and current attributes under `inode_lock()`, merge missing fields from old attributes, call generic validation, invoke `security_inode_file_setattr()`, call the filesystem `->fileattr_set()`, and notify xattr watchers.

## State and Persistence Behavior

The file itself owns no persistent state. It mediates persistent inode flags and project/quota/extent-hint fields stored by filesystems. It preserves readonly xflag masks on set, merges unspecified fields from current attributes, and normalizes zero extent-size hints by clearing matching xflags.

## Dependencies and Integration Points

Dependencies include LSM hooks, fscrypt flag preparation, idmapped mount ownership checks, namespace project-id validation, mount write counts, `filename_lookup()`, `copy_struct_to_user()`, and filesystem `fileattr_get/set` operations. Ioctl paths share the same VFS setter/getter as syscalls.

## Risks and Edge Cases

Important risks are capability checks for immutable/append flags, project-id changes outside the initial user namespace, DAX/extent hint validity on non-regular files or non-directories, ABI size handling for extensible `file_attr`, and correct error translation from `-ENOIOCTLCMD`/`-ENOTTY` to `-EOPNOTSUPP`.

## Test Signals

Useful coverage includes ioctl and syscall round trips, immutable/append capability tests, idmapped mount ownership cases, project quota namespace restrictions, fscrypt flag interactions, unsupported-filesystem error mapping, ABI size fuzzing, and filesystem-specific xfstests for ext4, XFS, btrfs, and overlay paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/file_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/file_table.c -->
# sources/distributed-fs/ceph-client/fs/file_table.c

## Purpose

`sources/distributed-fs/ceph-client/fs/file_table.c` allocates, initializes, accounts, and releases `struct file` objects. It owns global file count sysctls, `filp` slab caches, backing-file containers, pseudo-file allocation helpers, and the deferred `fput()` destruction pipeline. The complete 665-line file was read for this report.

## Important APIs, Types, and Functions

Key APIs include `backing_file_user_path()`, `backing_file_set_user_path()`, security accessors for backing files, `get_max_files()`, `alloc_empty_file()`, `alloc_empty_file_noaccount()`, `alloc_empty_backing_file()`, `alloc_file_pseudo()`, `alloc_file_pseudo_noaccount()`, `alloc_file_clone()`, `flush_delayed_fput()`, `fput()`, `__fput_sync()`, `fput_close_sync()`, `fput_close()`, `files_init()`, and `files_maxfiles_init()`. Internal work centers on `init_file()`, `file_init_path()`, `__fput()`, `__fput_deferred()`, and the `backing_file` wrapper.

## Control Flow

Allocation checks global file limits unless the caller chooses a no-account path, allocates from SLAB_TYPESAFE_BY_RCU caches, initializes credentials, security blobs, locks, mode/flag state, fsnotify mode, error cursors, and finally the reference counter. Path-based allocation fills inode, mapping, file operations, access mode, readcount, and open mode. Final `fput()` drops the last reference, schedules task work where possible, or falls back to delayed work. `__fput()` runs close notifications, eventpoll cleanup, locks removal, LSM release, fasync shutdown, `->release`, cdev release, path and mount puts, and cache free.

## State and Persistence Behavior

Persistent storage is not modified directly, but close and release callbacks may flush filesystem/device state. Runtime state includes global `files_stat`, a percpu `nr_files` counter, sysctl-exposed limits, two slab caches, delayed fput lists, task-work callbacks, and per-file credentials, fsnotify, position, mapping, and error cursor state.

## Dependencies and Integration Points

This file integrates with LSM allocation/release hooks, fsnotify, file locks, eventpoll, task_work, mount/dentry lifetime management, character device refs, percpu counters, sysctl registration, kmemleak annotations, and pseudo-file users such as anon inodes and kernel-internal backing files.

## Risks and Edge Cases

Risks include global file limit enforcement under inaccurate percpu counters, freeing SLAB_TYPESAFE_BY_RCU objects before RCU users are safe, using synchronous fput in contexts that can deadlock unmount, mount writer count imbalance when callers attach writable paths incorrectly, and backing-file security/user-path cleanup.

## Test Signals

Signals include file-max and nr_open sysctl tests, open/close stress under file limit pressure, LSM allocation failure injection, delayed fput/task_work coverage, unmount with delayed file references, eventpoll and fasync close tests, and KASAN/KCSAN/RCU debug for file object reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/file_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/filesystems.c -->
# sources/distributed-fs/ceph-client/fs/filesystems.c

## Purpose

`sources/distributed-fs/ceph-client/fs/filesystems.c` maintains the kernel registry of filesystem drivers. It supports registration/unregistration, module reference acquisition, legacy `sysfs(2)` filesystem queries, `/proc/filesystems`, block-device filesystem name listing, and module autoload through `get_fs_type()`. The complete 295-line file was read for this report.

## Important APIs, Types, and Functions

Exported APIs are `register_filesystem()`, `unregister_filesystem()`, and `get_fs_type()`, with `get_filesystem()` and `put_filesystem()` managing module refs. Internal helpers include `find_filesystem()`, `__get_fs_type()`, legacy `fs_index()`, `fs_name()`, `fs_maxindex()`, `list_bdev_fs_names()`, and `filesystems_proc_show()`.

## Control Flow

Filesystem registration validates parameter descriptions, rejects names containing `.`, prevents double-linking, and inserts into the global singly linked list under `file_systems_lock`. Unregistration removes the exact object, clears `next`, then waits for RCU readers. Lookup parses optional subtype suffixes, tries the current registry under read lock with `try_module_get()`, calls `request_module("fs-%.*s")` if missing, and rejects subtype use unless `FS_HAS_SUBTYPE` is set.

## State and Persistence Behavior

The only persistent runtime state is the global `file_systems` list protected by `file_systems_lock`. Registry contents last until module unload or built-in lifetime. `/proc/filesystems` and legacy syscall output are live views of that list.

## Dependencies and Integration Points

This file integrates with module ownership, `fs_parser` parameter validation, `/proc`, seq_file, kernel module autoloading, the mount path's filesystem type lookup, and init-time block filesystem enumeration.

## Risks and Edge Cases

Risks include module reference handling while walking the registry, duplicate registrations, subtype parsing mistakes, `/proc/filesystems` racing with unregister, and stale success from `request_module()` that still leaves no registered filesystem. Registration forbids names with dots because dot suffixes represent subtypes.

## Test Signals

Coverage should include module filesystem load/unload, duplicate registration failure, subtype mount behavior, `/proc/filesystems` output, `sysfs(2)` if configured, autoload success/failure, and lockdep/KCSAN around concurrent mount lookup and unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/filesystems.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/freevxfs/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/Kconfig` defines the build-time configuration option for the FreeVxFS filesystem driver. The complete 27-line file was read for this report.

## Important APIs, Types, and Functions

The sole config symbol is `VXFS_FS`, a tristate option named "FreeVxFS file system support (VERITAS VxFS(TM) compatible)". It depends on `BLOCK` and selects `BUFFER_HEAD`.

## Control Flow

There is no runtime control flow. Kconfig selection enables the driver as built-in or module and ensures the buffer-head dependency is available.

## State and Persistence Behavior

The file affects kernel build configuration only. It does not own runtime state or on-disk persistence.

## Dependencies and Integration Points

It integrates with the kernel build system, block-device filesystem support, and `fs/freevxfs/Makefile`. The help text documents read-only support for VxFS versions 2, 3, and 4, with known SCO UnixWare and HP-UX image coverage.

## Risks and Edge Cases

Risks are mostly build/configuration drift: the driver uses buffer-head APIs, requires block devices, and supports only read-only mounting despite VxFS being a full filesystem format. The help text typo "VxFX" is cosmetic.

## Test Signals

Useful signals are `allyesconfig`, modular build, built-in build, dependency checks with `BLOCK=n`, module autoload via `mount -t vxfs`, and documentation/help consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/freevxfs/Makefile

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/Makefile` wires the FreeVxFS driver objects into the kernel build. The complete 9-line file was read for this report.

## Important APIs, Types, and Functions

The build target is `obj-$(CONFIG_VXFS_FS) += freevxfs.o`. The composite object is assembled from `vxfs_bmap.o`, `vxfs_fshead.o`, `vxfs_immed.o`, `vxfs_inode.o`, `vxfs_lookup.o`, `vxfs_olt.o`, `vxfs_subr.o`, and `vxfs_super.o`.

## Control Flow

There is no runtime control flow. Kbuild compiles the listed objects when `CONFIG_VXFS_FS` is enabled and links them into `freevxfs.o`.

## State and Persistence Behavior

The file affects build outputs only and owns no runtime state.

## Dependencies and Integration Points

It integrates with Kconfig's `VXFS_FS` symbol and the Linux Kbuild composite-object convention. Object order places support modules before `vxfs_super.o`, which contains module init/exit and filesystem registration.

## Risks and Edge Cases

Risk is limited to build omissions: if a source file is added but not listed, symbols will be missing or dead code will not compile. If `vxfs_super.o` were omitted, the module would not register the filesystem.

## Test Signals

Build tests for built-in and module configurations are sufficient, along with `modinfo freevxfs` and link-time symbol resolution checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs.h -->
# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs.h

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs.h` defines the FreeVxFS superblock ABI, byte-order helpers, VxFS mode/type constants, inode organization constants, and in-core superblock private state. The complete 257-line file was read for this report.

## Important APIs, Types, and Functions

Important definitions include `VXFS_SUPER_MAGIC`, `VXFS_ROOT_INO`, `struct vxfs_sb`, `struct vxfs_sb_info`, `enum vxfs_byte_order`, `__fs16/__fs32/__fs64`, `fs16_to_cpu()`, `fs32_to_cpu()`, `fs64_to_cpu()`, `enum vxfs_mode`, `VXFS_TYPE_MASK`, `VXFS_IS*` type predicates, `VXFS_ORG_*`, organization predicates, and `VXFS_SBI()`.

## Control Flow

The header has no independent runtime flow. Runtime users set `vxfs_sb_info.byte_order` during superblock probing, then all on-disk integer reads pass through the endian helpers. Type and organization macros steer inode setup, block mapping, immediate-data handling, and metadata discovery.

## State and Persistence Behavior

`struct vxfs_sb` mirrors on-disk superblock fields, including version, block geometry, free counts, OLT location, inode sizing, and legacy version fields. `struct vxfs_sb_info` stores the mounted instance's raw superblock buffer, structural inodes, OLT extent, fileset header inode, initial inode-list extent, and byte order.

## Dependencies and Integration Points

This header is shared by every FreeVxFS implementation file. It depends on Linux integer types and endian conversion helpers and integrates with VFS `super_block->s_fs_info` through `VXFS_SBI()`.

## Risks and Edge Cases

The struct layout is an on-disk ABI; incorrect field offsets or endian conversion mistakes can corrupt all higher-level interpretation. The driver only models a subset of full VxFS superblock fields, so unsupported versions or ports may contain valid metadata beyond the modeled structure.

## Test Signals

Signals include mounting little-endian UnixWare and big-endian HP-UX images, validating statfs values, sparse/smatch checks for `__bitwise` endian misuse, and regression images for VxFS versions 2 through 4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_bmap.c -->
# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_bmap.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_bmap.c` maps FreeVxFS logical file blocks to physical disk blocks for internal reads and generic block mapping. It handles ext4-style VxFS extents and typed extents. The complete 271-line file was read for this report.

## Important APIs, Types, and Functions

The exported internal API is `vxfs_bmap1(struct inode *, long)`. Internal helpers are `vxfs_bmap_ext4()`, `vxfs_bmap_indir()`, `vxfs_bmap_typed()`, and diagnostic `vxfs_typdump()`. It consumes `struct vxfs_inode_info`, `struct vxfs_ext4`, `struct vxfs_typed`, `struct vxfs_typed_dev4`, and organization/type constants from `vxfs_inode.h`.

## Control Flow

`vxfs_bmap1()` dispatches by inode organization. Ext4-style mapping walks direct extents first, then reads an indirect block and indexes it for remaining logical blocks. Typed mapping scans the inode's inline typed extents; data extents return block plus offset, indirect extents recurse into extent blocks, and DEV4 extents are reported but unsupported. Unknown extent types trigger `BUG()`.

## State and Persistence Behavior

The code reads mapping state from on-disk inode extent descriptors and indirect extent blocks; it does not mutate metadata. Buffer heads are acquired with `sb_bread()` and released with `brelse()`.

## Dependencies and Integration Points

`vxfs_subr.c` calls `vxfs_bmap1()` from `vxfs_bread()`, `vxfs_getblk()`, and `generic_block_bmap()` paths. Inode setup in `vxfs_inode.c` assigns address-space operations that eventually invoke this mapper for regular files, symlinks, directories, and metadata inodes.

## Risks and Edge Cases

Malformed extent sizes, indirect block addresses, unsupported DEV4 extents, and unknown type values can produce failed reads or kernel warnings. The ext4 indirect indexing expression is subtle and historically fragile; boundary tests are important. Recursion in typed indirect extents can consume stack on adversarial images.

## Test Signals

Use fixture images with direct extents, indirect extents, typed data extents, holes/unmapped blocks, immediate files, and unsupported DEV4 descriptors. Fuzzed VxFS images plus KASAN/UBSAN can exercise malformed extent records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_bmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_dir.h -->
# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_dir.h

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_dir.h` defines FreeVxFS on-disk directory block and entry formats plus record-size helpers. The complete 68-line file was read for this report.

## Important APIs, Types, and Functions

Key definitions are `struct vxfs_dirblk`, `struct vxfs_direct`, `VXFS_NAMELEN`, `VXFS_DIRPAD`, `VXFS_NAMEMIN`, `VXFS_DIRROUND()`, `VXFS_DIRLEN()`, and `VXFS_DIRBLKOV()`.

## Control Flow

The header has no runtime flow. `vxfs_lookup.c` uses these layouts to skip the per-block hash/free-space header, walk variable-length directory entries, compare names, and emit directory entries to VFS.

## State and Persistence Behavior

The structures model on-disk directory records. `d_ino`, `d_reclen`, `d_namelen`, and `d_hashnext` are endian-tagged fields read through the superblock byte-order helpers.

## Dependencies and Integration Points

The file depends on `fs16_to_cpu()` for the `VXFS_DIRBLKOV()` macro and integrates directly with directory lookup/readdir page walking.

## Risks and Edge Cases

Malformed `d_nhash`, `d_reclen`, or `d_namelen` fields can affect directory scanning because the implementation performs little structural validation. Name length is capped at 256 bytes, matching the fixed `d_name` array.

## Test Signals

Signals include directory images with empty entries, long names, block-boundary entries, hash overhead variations, zero record-length terminators, and fuzzed directory blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_dir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_extern.h -->
# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_extern.h

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_extern.h` declares cross-file interfaces used inside the FreeVxFS driver. The complete 49-line file was read for this report.

## Important APIs, Types, and Functions

Declarations include `vxfs_bmap1()`, `vxfs_read_fshead()`, `vxfs_immed_aops`, `vxfs_dumpi()` under diagnostic builds, `vxfs_blkiget()`, `vxfs_stiget()`, `vxfs_iget()`, `vxfs_evict_inode()`, `vxfs_dir_inode_ops`, `vxfs_dir_operations`, `vxfs_read_olt()`, `vxfs_aops`, `vxfs_get_page()`, `vxfs_put_page()`, and `vxfs_bread()`.

## Control Flow

The header has no execution. It defines the static driver layering: superblock mount code calls OLT and fileset-header readers, those read metadata inodes, inode code assigns directory and address-space operations, and subroutines call the block mapper.

## State and Persistence Behavior

No storage is owned by the header. It exposes functions that operate on superblock private state, inode private state, pagecache pages, and buffer heads.

## Dependencies and Integration Points

It provides a local integration surface between the eight FreeVxFS object files listed in the Makefile. The prototypes also encode which symbols are intentionally shared inside the driver rather than file-local.

## Risks and Edge Cases

Risk is signature drift: missing or stale prototypes can hide type mismatches or break builds when driver internals change. Since this is a C internal header, it also determines diagnostic-only availability of `vxfs_dumpi()`.

## Test Signals

Build coverage with `W=1`, sparse, and both diagnostic/non-diagnostic configurations is the main signal, plus link-time validation of the composite module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_extern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_fshead.c -->
# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_fshead.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_fshead.c` reads FreeVxFS fileset headers during mount and resolves the primary inode list and structural inode list. The complete 166-line file was read for this report.

## Important APIs, Types, and Functions

The external API is `vxfs_read_fshead(struct super_block *)`. Internal helpers are diagnostic `vxfs_dumpfsh()` and `vxfs_getfsh()`. It uses `struct vxfs_fsh`, `vxfs_blkiget()`, `vxfs_stiget()`, `vxfs_bread()`, and inode type predicates.

## Control Flow

`vxfs_read_fshead()` first reads the fileset-header inode from the initial inode-list extent discovered in the OLT. It verifies the inode is a fileset header, reads structural and primary fileset header blocks from that inode, then loads the structural inode-list inode and primary inode-list inode. Each list inode is checked for the inode-list type before mount can continue.

## State and Persistence Behavior

The function populates `vxfs_sb_info` fields `vsi_fship`, `vsi_stilist`, and `vsi_ilist`, which remain pinned until unmount. Temporary copied `struct vxfs_fsh` buffers are heap allocated and freed after the relevant inode numbers are extracted.

## Dependencies and Integration Points

This file sits between OLT discovery in `vxfs_olt.c` and normal inode lookup in `vxfs_inode.c`. `vxfs_super.c` calls it after block size and OLT setup, before loading the root inode.

## Risks and Edge Cases

Malformed fileset headers can leak references if cleanup paths regress; current code carefully frees `pfp`, `sfp`, and iputs loaded inodes on failure. It trusts several on-disk fields after type checks, so fuzzed images can still force odd inode-list reads.

## Test Signals

Fixture mounts should cover valid primary/structural fileset headers, missing fileset-header inode, wrong inode type, unreadable header blocks, invalid inode-list type, and cleanup under mount failure with kmemleak enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_fshead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_fshead.h -->
# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_fshead.h

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_fshead.h` defines the on-disk FreeVxFS fileset header subset consumed by the Linux driver. The complete 43-line file was read for this report.

## Important APIs, Types, and Functions

The key type is `struct vxfs_fsh`, containing version/index/time fields, inode counts, IAU information, inode-list inode numbers, and link-count table inode number.

## Control Flow

There is no runtime flow. `vxfs_fshead.c` copies this structure from metadata blocks and reads selected fields through endian helpers.

## State and Persistence Behavior

The structure models persistent fileset metadata. The header intentionally stops before version/port-specific trailing fields, so the driver only relies on the common prefix it needs to locate inode lists.

## Dependencies and Integration Points

It depends on `__fs32` from `vxfs.h` and integrates with `vxfs_read_fshead()` during mount.

## Risks and Edge Cases

The main risk is ABI mismatch across VxFS variants. If a supported image has a different common-prefix layout, the driver may choose the wrong inode-list inode. The comments explicitly acknowledge that later fields vary by version and port.

## Test Signals

Mount tests against HP-UX and SCO images, endian conversion checks, and fileset-header fixture parsing across VxFS versions 2-4 are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_fshead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_immed.c -->
# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_immed.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_immed.c` implements address-space operations for VxFS immediate-data files, where file contents are stored directly inside the inode. The complete 53-line file was read for this report.

## Important APIs, Types, and Functions

The external object is `const struct address_space_operations vxfs_immed_aops`. Its only operation is `vxfs_immed_read_folio()`.

## Control Flow

When the pagecache requests a folio for an immediate inode, `vxfs_immed_read_folio()` computes a source pointer into `VXFS_INO(host)->vii_immed.vi_immed` at `folio_pos(folio)`, copies one page per folio page with `memcpy_to_page()`, marks the folio uptodate, and unlocks it.

## State and Persistence Behavior

The persisted data was already copied from the on-disk inode into `vxfs_inode_info` during inode load. Reads copy from that in-core immediate buffer into pagecache; no write path exists because the driver is read-only.

## Dependencies and Integration Points

`vxfs_inode.c` selects `vxfs_immed_aops` for immediate regular files/directories and sets inline symlink data directly for immediate symlinks. The code depends on folio/pagecache APIs and the FreeVxFS inode layout.

## Risks and Edge Cases

Immediate data capacity is small (`VXFS_NIMMED` is 96 bytes), but the read helper copies `PAGE_SIZE` chunks per folio page from the inline buffer without local length clamping. Correctness depends on pagecache read sizes and inode size limiting access; malformed sizes can be risky.

## Test Signals

Tests should include immediate symlinks, small immediate regular files, immediate directories if present, short reads at EOF, and fuzzed inode sizes under KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_immed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_inode.c -->
# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_inode.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_inode.c` translates VxFS on-disk inodes into Linux VFS inodes and provides inode lookup helpers for normal, structural, and extent-based metadata inodes. The complete 314-line file was read for this report.

## Important APIs, Types, and Functions

Important functions are `vxfs_blkiget()`, `vxfs_stiget()`, `vxfs_iget()`, and `vxfs_evict_inode()`, plus diagnostic `vxfs_dumpi()`. Internal helpers are `vxfs_transmod()`, `dip2vip_cpy()`, and `__vxfs_iget()`.

## Control Flow

`dip2vip_cpy()` endian-converts common disk inode fields into `vxfs_inode_info`, copies organization-specific data without conversion, and initializes VFS inode mode, uid/gid, link count, size, times, blocks, and generation. `vxfs_blkiget()` reads metadata inodes directly from a known extent via buffer cache during mount. `__vxfs_iget()` reads normal inodes from the inode-list mapping through pagecache. `vxfs_iget()` uses `iget_locked()`, fills new inodes, chooses address-space operations based on immediate vs mapped organization, and assigns regular, directory, symlink, or special inode operations.

## State and Persistence Behavior

The file populates in-core inode private state from persistent disk inodes. It does not write back VxFS metadata. Eviction truncates pagecache and clears VFS inode state.

## Dependencies and Integration Points

It integrates with mount setup (`vxfs_fshead.c`), directory lookup (`vxfs_lookup.c`), address-space operations (`vxfs_aops`, `vxfs_immed_aops`), generic read-only file ops, symlink inode operations, and old device decoding for special files.

## Risks and Edge Cases

Risks include trusting disk inode sizes, organization types, and device numbers; immediate symlink termination depends on inline buffer capacity; and metadata inodes loaded with `new_inode()` use generated inode numbers rather than disk numbers. Unsupported or malformed mode/type combinations can lead to wrong VFS operation assignment.

## Test Signals

Mount fixture images with regular files, directories, symlinks, immediate symlinks, device nodes, structural inodes, and corrupt inode-list blocks. KASAN and inode lifetime tracing are useful around failed `iget` and eviction paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_inode.h -->
# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_inode.h

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_inode.h` defines FreeVxFS on-disk inode layouts, extent organization records, and the in-core inode private structure. The complete 169-line file was read for this report.

## Important APIs, Types, and Functions

Key definitions include `VXFS_ISIZE`, `VXFS_NDADDR`, `VXFS_NIADDR`, `VXFS_NIMMED`, `VXFS_NTYPED`, typed extent masks, `VXFS_TYPED_PER_BLOCK()`, typed extent type constants, `struct vxfs_immed`, `struct vxfs_ext4`, `struct vxfs_typed`, `struct vxfs_typed_dev4`, `struct vxfs_dinode`, `struct vxfs_inode_info`, field alias macros, and `VXFS_INO()`.

## Control Flow

The header has no independent flow. Its union layouts determine how `vxfs_inode.c` copies inode data and how `vxfs_bmap.c` maps extents.

## State and Persistence Behavior

`struct vxfs_dinode` is persistent on-disk state, including mode, ownership, size, timestamps, organization type, allocation metadata, generation, and organization-specific payload. `struct vxfs_inode_info` embeds the Linux `struct inode` and stores converted VxFS private fields for runtime use.

## Dependencies and Integration Points

It is included by most FreeVxFS source files and bridges VxFS disk structures to VFS inode instances through `VXFS_INO()`.

## Risks and Edge Cases

On-disk layout drift is the main risk. The organization union is copied raw, so all consumers must endian-convert fields at use time. The `vdi_fixextsize` alias appears to reference `regular` while the union member is named `i_regular`, which is a latent macro issue if used.

## Test Signals

Sparse endian checks, compile coverage for all macros, fixtures for each organization type, and fuzzing of typed extents and immediate payload sizes are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_lookup.c -->
# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_lookup.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_lookup.c` implements FreeVxFS directory lookup and readdir support. It walks VxFS directory pages, finds matching directory entries, and exposes directory operations to VFS. The complete 273-line file was read for this report.

## Important APIs, Types, and Functions

External operation tables are `vxfs_dir_inode_ops` and `vxfs_dir_operations`. Internal functions are `vxfs_find_entry()`, `vxfs_inode_by_name()`, `vxfs_lookup()`, and `vxfs_readdir()`.

## Control Flow

Lookup checks name length, scans directory pages with `vxfs_find_entry()`, extracts the found inode number, loads the target with `vxfs_iget()`, and returns through `d_splice_alias()`. Directory scanning emits `.` and `..` first, then walks entries from `ctx->pos`, skips per-block directory headers, advances by `d_reclen`, ignores deleted entries with zero inode, and calls `dir_emit()` with `DT_UNKNOWN`.

## State and Persistence Behavior

Directory state is read-only on-disk directory blocks exposed through pagecache. `ctx->pos` is the persistent userspace iteration cursor for an open directory stream. No directory modifications are supported.

## Dependencies and Integration Points

The code uses `vxfs_get_page()`/`vxfs_put_page()`, directory layout macros from `vxfs_dir.h`, byte-order helpers from `vxfs.h`, inode lookup from `vxfs_inode.c`, and generic VFS directory helpers including `generic_file_llseek`, `generic_read_dir`, and `generic_setlease`.

## Risks and Edge Cases

Malformed directory records can affect scanning because `d_reclen` and header overhead are trusted after minimal checks. The code returns `-ENOMEM` for any page read error in readdir, losing the original error. `vxfs_inode_by_name()` manually does `kunmap()` and `put_page()` rather than `vxfs_put_page()`, so consistency is worth preserving.

## Test Signals

Tests should cover lookup hits/misses, long names, empty directories, deleted entries, entries spanning page/block boundaries, stable `telldir`/`seekdir` behavior, corrupt zero or oversized record lengths, and directory fuzzing under KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_olt.c -->
# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_olt.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_olt.c` reads the FreeVxFS Object Location Table during mount and extracts the fileset-header inode and initial inode-list extent. The complete 105-line file was read for this report.

## Important APIs, Types, and Functions

The external API is `vxfs_read_olt(struct super_block *, u_long)`. Internal helpers are `vxfs_get_fshead()`, `vxfs_get_ilist()`, and `vxfs_oblock()`.

## Control Flow

`vxfs_read_olt()` reads the OLT extent from the location recorded in the superblock, validates the OLT magic, rejects multi-block OLTs, then scans records from the header size to the extent end. It handles `VXFS_OLT_FSHEAD` by recording `vsi_fshino` and `VXFS_OLT_ILIST` by recording `vsi_iext`. Mount continues only if both values were found.

## State and Persistence Behavior

The function populates `vxfs_sb_info.vsi_fshino` and `vsi_iext`. It reads but does not retain the OLT buffer after parsing.

## Dependencies and Integration Points

`vxfs_super.c` calls this after setting the final block size and before reading fileset headers. It uses OLT record layouts from `vxfs_olt.h` and endian helpers from `vxfs.h`.

## Risks and Edge Cases

The scanner advances by on-disk `olt_size` without robust bounds or zero-size validation, so malformed OLT records can break scanning. Multi-block OLTs are explicitly unsupported. Duplicate FSHEAD or ILIST records trigger `BUG_ON()` in helper functions.

## Test Signals

Fixture images should include valid OLT, bad magic, missing FSHEAD, missing ILIST, duplicate entries, multi-block OLT, and fuzzed record sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_olt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_olt.h -->
# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_olt.h

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_olt.h` defines the on-disk FreeVxFS Object Location Table header and record types. The complete 120-line file was read for this report.

## Important APIs, Types, and Functions

Definitions include `VXFS_OLT_MAGIC`, OLT type constants (`VXFS_OLT_FREE`, `FSHEAD`, `CUT`, `ILIST`, `DEV`, `SB`), `struct vxfs_olt`, `struct vxfs_oltcommon`, `struct vxfs_oltfree`, `struct vxfs_oltilist`, `struct vxfs_oltcut`, `struct vxfs_oltsb`, `struct vxfs_oltdev`, and `struct vxfs_oltfshead`.

## Control Flow

There is no runtime flow. `vxfs_olt.c` uses the common record prefix to switch on record type and cast to specific record structures.

## State and Persistence Behavior

All structures describe persistent OLT metadata. The Linux driver currently consumes only fileset-header and initial-inode-list records, while the header also models free, current-usage-table, superblock/log/OLT, and device records.

## Dependencies and Integration Points

The header depends on `__fs32` from the FreeVxFS superblock header and is used during mount metadata discovery.

## Risks and Edge Cases

The common-prefix cast pattern depends on every record starting with type and size. Record size, alignment, and endian conversion must be handled by consumers; the header itself provides no validation.

## Test Signals

Signals include OLT parser fixtures for each record type, endian checks, size/alignment tests, and fuzzed record streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_olt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_subr.c -->
# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_subr.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_subr.c` provides shared FreeVxFS pagecache and block-read helpers plus normal address-space operations for mapped files. The complete 152-line file was read for this report.

## Important APIs, Types, and Functions

The external operation table is `vxfs_aops`, with `read_folio` and `bmap`. Exported internal helpers are `vxfs_get_page()`, `vxfs_put_page()`, and `vxfs_bread()`. Internal helpers are `vxfs_getblk()`, `vxfs_read_folio()`, and `vxfs_bmap()`.

## Control Flow

`vxfs_get_page()` calls `read_mapping_page()` and maps the page with `kmap()` for directory/inode-list consumers. `vxfs_bread()` maps a logical block through `vxfs_bmap1()` and reads the resulting physical block. `vxfs_getblk()` fills a buffer head via `map_bh()` for successful mappings. `vxfs_read_folio()` delegates to `block_read_full_folio()`, and `vxfs_bmap()` delegates to `generic_block_bmap()`.

## State and Persistence Behavior

The code reads persistent file data and metadata into pagecache or buffer cache. It does not allocate blocks or write metadata; `create` in `vxfs_getblk()` is ignored because the driver is read-only.

## Dependencies and Integration Points

It integrates with `vxfs_bmap1()`, VFS address-space operations, buffer-head I/O, pagecache helpers, directory lookup, inode-list reads, and fileset-header reads.

## Risks and Edge Cases

Physical block zero maps to `-EIO` in `vxfs_getblk()` but `vxfs_bread()` still calls `sb_bread()` even if `vxfs_bmap1()` returns zero. Page mapping uses legacy `kmap()`/`kunmap()` and depends on callers balancing `vxfs_put_page()`. Error propagation from lower-level mapping is limited.

## Test Signals

Tests include reading regular files, directories, symlinks, metadata inodes, block holes/unmapped extents, bmap ioctl paths, read errors, and highmem builds that exercise kmap balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_subr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_super.c -->
# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_super.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_super.c` implements FreeVxFS module registration, mount context handling, superblock probing/filling, statfs, inode cache management, and unmount cleanup. The complete 347-line file was read for this report.

## Important APIs, Types, and Functions

Important functions are `vxfs_put_super()`, `vxfs_statfs()`, `vxfs_reconfigure()`, `vxfs_alloc_inode()`, `vxfs_free_inode()`, `vxfs_try_sb_magic()`, `vxfs_fill_super()`, `vxfs_get_tree()`, `vxfs_init_fs_context()`, `vxfs_init()`, and `vxfs_cleanup()`. Important objects are `vxfs_super_ops`, `vxfs_context_ops`, `vxfs_fs_type`, and `vxfs_inode_cachep`.

## Control Flow

Module init creates a usercopy-safe inode cache and registers filesystem type `vxfs`. Mount uses `get_tree_bdev()` to call `vxfs_fill_super()`, forces read-only, allocates `vxfs_sb_info`, sets an initial block size, probes little-endian UnixWare superblock at block 1 and big-endian HP-UX superblock at block 8, validates VxFS version 2-4, sets final block size, reads OLT, reads fileset headers, loads the root inode, and creates the root dentry. Reconfigure syncs and preserves read-only. Unmount drops pinned metadata inodes, releases the raw superblock buffer, and frees private info.

## State and Persistence Behavior

Runtime mount state is stored in `super_block` and `vxfs_sb_info`. The driver is read-only (`SB_RDONLY` forced), so it does not modify persistent VxFS data. Statfs reads free/block counters from the raw superblock.

## Dependencies and Integration Points

This file integrates with the VFS filesystem registry, fs_context API, block-device mount helper, buffer-head superblock reads, OLT/fileset/inode loaders, dentry root creation, slab cache lifecycle, module aliases, and RCU barrier cleanup before cache destruction.

## Risks and Edge Cases

Risks include incomplete cleanup on mount failure, limited superblock location/version support, trusting raw geometry values before deeper validation, usercopy cache range correctness for inline immediate data, and read-only enforcement during remount/reconfigure.

## Test Signals

Signals include module load/unload, mount valid little-endian and big-endian images, unsupported version rejection, wrong magic at both offsets, OLT/fileset failure cleanup under kmemleak, statfs output, forced read-only remount, and slab/RCU debug on module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fs-writeback.c -->
# sources/distributed-fs/ceph-client/fs/fs-writeback.c

## Purpose

`sources/distributed-fs/ceph-client/fs/fs-writeback.c` implements the VFS writeback engine for dirty inodes and pagecache data. It manages dirty inode lists, flusher work items, background and periodic writeback, sync writeback, lazytime expiration, cgroup writeback ownership, and exported helpers for inode metadata flushing. The complete 2996-line file was read for this report.

## Important APIs, Types, and Functions

Core structures and state include `struct wb_writeback_work`, `dirtytime_expire_interval`, `bdi_writeback` dirty lists, and optional `struct inode_switch_wbs_context`. Exported APIs include `wb_wait_for_completion()`, `wbc_attach_fdatawrite_inode()`, `wbc_detach_inode()`, `wbc_account_cgroup_owner()`, `inode_io_list_del()`, `writeback_inodes_sb_nr()`, `writeback_inodes_sb()`, `try_to_writeback_inodes_sb()`, `sync_inodes_sb()`, `write_inode_now()`, `sync_inode_metadata()`, and `__mark_inode_dirty()`. Other important functions include `wb_queue_work()`, `inode_io_list_move_locked()`, `queue_io()`, `__writeback_single_inode()`, `writeback_single_inode()`, `writeback_sb_inodes()`, `wb_writeback()`, `wb_do_writeback()`, and `wb_workfn()`.

## Control Flow

Dirtying starts in `__mark_inode_dirty()`: filesystem dirty callbacks run for inode dirtiness, state bits are set with memory barriers, the inode is attached to a writeback context, and it is queued on `b_dirty` or `b_dirty_time`. Flusher workers take queued `wb_writeback_work` items, move expired dirty inodes to `b_io`, group work by superblock, set `I_SYNC`, call `do_writepages()`, optionally wait data, sync lazytime, write inode metadata, then requeue or detach the inode based on remaining dirty state. Sync paths split work across cgroup writeback instances, wait for completions, and then wait for existing writeback on the superblock's writeback inode list.

## State and Persistence Behavior

Runtime state spans inode dirty bits (`I_DIRTY_*`, `I_SYNC`, `I_SYNC_QUEUED`, `I_WB_SWITCH`), per-wb lists (`b_dirty`, `b_io`, `b_more_io`, `b_dirty_time`, `b_attached`), work queues, completion counters, bandwidth stats, and sysctl-controlled lazytime expiration. Persistent effects occur through filesystem `writepages`, `write_inode`, and `sync_lazytime` operations that write data and metadata to storage.

## Dependencies and Integration Points

The file integrates with pagecache tags, backing-device writeback, block plug flushing, memcg/cgroup writeback, superblock locking, filesystem super operations, dirty throttling thresholds, tracepoints, sysctl, workqueues, RCU, and hung-task progress reporting.

## Risks and Edge Cases

High-risk areas are lock ordering between inode locks, wb list locks, superblock `s_umount`, and cgroup switch semaphores; memory barriers around dirty-bit clearing and lockless dirty checks; inode lifetime while waiting on `I_SYNC`; cgroup ownership switching across RCU/workqueues; lazytime inodes not counted as dirty I/O; and avoiding livelock under continuously redirtied mappings.

## Test Signals

Signals include xfstests generic sync/fsync/writeback cases, cgroup writeback ownership tests, memcg dirty throttling, lazytime expiration sysctl tests, writeback under umount, fault injection in `writepages`/`write_inode`, lockdep/KCSAN, tracepoint inspection, hung-task wait progress, and stress with concurrent dirtying, reclaim, sync, and cgroup deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fs-writeback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fs_context.c -->
# sources/distributed-fs/ceph-client/fs/fs_context.c

## Purpose

`sources/distributed-fs/ceph-client/fs/fs_context.c` implements the VFS filesystem-context lifecycle and common mount-parameter parsing. It is the common infrastructure behind new mounts, submounts, reconfiguration, duplicated contexts, parameter logging, and cleanup/reinitialization. The complete 568-line file was read for this report.

## Important APIs, Types, and Functions

Exported APIs include `vfs_parse_fs_param_source()`, `vfs_parse_fs_param()`, `vfs_parse_fs_qstr()`, `vfs_parse_monolithic_sep()`, `generic_parse_monolithic()`, `fs_context_for_mount()`, `fs_context_for_submount()`, `vfs_dup_fs_context()`, `logfc()`, and `put_fs_context()`. Other important functions include `alloc_fs_context()`, `fs_context_for_reconfigure()`, `fc_drop_locked()`, `parse_monolithic_mount_data()`, `vfs_clean_context()`, and `finish_clean_context()`.

## Control Flow

Parameter parsing first recognizes common superblock flags (`ro`, `rw`, `sync`, `async`, `lazytime`, and related options), lets LSM hooks consume security options, delegates to filesystem `parse_param`, and falls back to default `source` handling. Context allocation initializes purpose-specific references for mount, submount, or reconfigure, pins filesystem type, creds, net namespace, user namespace, and optionally root/superblock. Freeing reverses those references and calls filesystem/LSM cleanup. Cleaning after a mount success discards temporary state and later reinitializes if the context is reused for reconfigure.

## State and Persistence Behavior

The file owns transient mount configuration state: `fs_context` flags, masks, source string, credentials, namespaces, security data, filesystem-private pointers, root dentry, log buffer, phase, and purpose. It does not directly persist filesystem data, but it determines flags and parameters used to create or reconfigure superblocks.

## Dependencies and Integration Points

It integrates with fs_parser constants, LSM fs_context hooks, mount namespace/user namespace/network namespace lifetime, filesystem `init_fs_context`, `parse_param`, `parse_monolithic`, `dup`, and `free` operations, printk logging, and mount internals.

## Risks and Edge Cases

Risks include double source assignment, wrong parameter ownership after string stealing, log ring lifetime and allocation failures, duplicated context cleanup when filesystem `dup` or LSM dup fails, reconfigure cleanup split across `vfs_clean_context()` and `finish_clean_context()`, and reference balancing for active superblocks in reconfigure contexts.

## Test Signals

Coverage includes new mount API tests, monolithic option parsing with LSM options, source parameter validation, duplicated context failure injection, submount security inheritance, remount/reconfigure reuse, log buffer wraparound, and leak detection across failed mounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fs_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fs_dirent.c -->
# sources/distributed-fs/ceph-client/fs/fs_dirent.c

## Purpose

`sources/distributed-fs/ceph-client/fs/fs_dirent.c` provides small exported conversion helpers between generic filesystem on-disk file type values, POSIX mode bits, and userspace dirent `DT_*` values. The complete 105-line file was read for this report.

## Important APIs, Types, and Functions

The exported helpers are `fs_ftype_to_dtype()`, `fs_umode_to_ftype()`, and `fs_umode_to_dtype()`. Static lookup tables are `fs_dtype_by_ftype[]` and `fs_ftype_by_dtype[]`.

## Control Flow

`fs_ftype_to_dtype()` bounds-checks the `FT_*` input and returns `DT_UNKNOWN` for invalid values. `fs_umode_to_ftype()` maps mode bits through `S_DT(mode)` into `FT_*`. `fs_umode_to_dtype()` composes those two conversions.

## State and Persistence Behavior

There is no mutable or persistent state. The static tables are compile-time constants used by filesystems that store generic file type values or need to emit directory-entry types.

## Dependencies and Integration Points

The file depends on `linux/fs_dirent.h` definitions for `FT_*` and `DT_*`, and exports GPL symbols for filesystem implementations.

## Risks and Edge Cases

The main risk is table drift if `FT_*`, `DT_*`, or `S_DT()` semantics change. Invalid file types intentionally degrade to unknown rather than failing.

## Test Signals

Unit-style checks for every `FT_*`, every supported `DT_*`, representative `S_IF*` modes, and out-of-range `filetype` values would cover behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fs_dirent.c -->
