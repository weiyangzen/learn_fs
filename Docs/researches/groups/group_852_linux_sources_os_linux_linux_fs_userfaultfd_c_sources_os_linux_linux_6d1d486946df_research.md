# Group Research: group_852_linux_sources_os_linux_linux_fs_userfaultfd_c_sources_os_linux_linux_6d1d486946df

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/userfaultfd.c -->
# File Research: sources/os/linux/linux/fs/userfaultfd.c

## Purpose
Implements Linux `userfaultfd`: a file descriptor API that lets userspace receive and resolve page faults for registered virtual memory ranges, including missing, write-protect, minor, poison, move, fork/remap/remove/unmap events, and optional `/dev/userfaultfd` creation.

## Main Functions
- Fault path:
  - `handle_userfault()`: converts eligible VM faults into `UFFD_EVENT_PAGEFAULT` messages, queues the faulting task, drops the fault lock, wakes poll waiters, and sleeps until userspace resolves or releases the context.
  - `userfaultfd_must_wait()` / `userfaultfd_huge_must_wait()`: recheck page tables after queuing to avoid sleeping on already-resolved faults.
  - `userfault_msg()`: builds the userspace-visible `uffd_msg` with exact/rounded address, write/WP/minor flags, and optional thread id.
- Context/event lifecycle:
  - `userfaultfd_ctx_get()` / `userfaultfd_ctx_put()`: refcount and free `userfaultfd_ctx`.
  - `userfaultfd_release()`: marks context released, unregisters ranges, wakes pending faults/events, and reports hangup.
  - `userfaultfd_event_wait_completion()` / `userfaultfd_event_complete()`: deliver and synchronize non-pagefault events.
- VMA lifecycle hooks:
  - `dup_userfaultfd()`, `dup_userfaultfd_complete()`, `dup_userfaultfd_fail()`: fork handling and `UFFD_EVENT_FORK`.
  - `mremap_userfaultfd_prep()` / `mremap_userfaultfd_complete()` / `mremap_userfaultfd_fail()`: remap event handling.
  - `userfaultfd_remove()`, `userfaultfd_unmap_prep()`, `userfaultfd_unmap_complete()`: remove/unmap event handling.
- File operations:
  - `userfaultfd_poll()`: reports readable pending faults/events and enforces initialized nonblocking use.
  - `userfaultfd_read_iter()` / `userfaultfd_ctx_read()`: read one or more `uffd_msg`s, refile page faults from pending to active queues, and resolve fork events into new fd numbers.
  - `userfaultfd_ioctl()`: dispatches API, register/unregister, wake, copy, zeropage, move, writeprotect, continue, and poison ioctls.
- Ioctl implementations:
  - `userfaultfd_api()`: negotiates API version, features, and ioctl masks.
  - `userfaultfd_register()` / `userfaultfd_unregister()`: validate ranges, VMA compatibility, hugepage alignment, ownership, and set/clear `VM_UFFD_*` flags.
  - `userfaultfd_copy()`, `userfaultfd_zeropage()`, `userfaultfd_continue()`, `userfaultfd_poison()`, `userfaultfd_move()`: call mm fill/move helpers and optionally wake resolved faults.
  - `userfaultfd_writeprotect()`: toggles UFFD write-protection over a range.
- Creation/init:
  - `new_userfaultfd()`, `SYSCALL_DEFINE1(userfaultfd)`, `userfaultfd_dev_ioctl()`: create contexts via syscall or misc device.
  - `userfaultfd_syscall_allowed()`: enforces `UFFD_USER_MODE_ONLY`, `CAP_SYS_PTRACE`, or sysctl permission.
  - `userfaultfd_init()`: registers `/dev/userfaultfd`, context cache, and `vm.unprivileged_userfaultfd`.

## Important Design Points
- Wait queues are split into pending page faults, active/read page faults, events, and fd poll waiters.
- Wakeups use range filtering and a `refile_seq` seqcount to avoid missing wakeups while faults move between queues.
- `handle_userfault()` is careful about VM fault retry semantics and returns `VM_FAULT_RETRY` with locks released where required.
- `mmap_changing` gates resolving ioctls during fork/remap/remove/unmap windows; callers return `-EAGAIN` or store negative result fields when the mapping is unstable.
- Feature negotiation is one-shot via `cmpxchg(&ctx->features, 0, ctx_features)` and `UFFD_FEATURE_INITIALIZED`.
- `UFFD_FEATURE_WP_ASYNC` implies `UFFD_FEATURE_WP_UNPOPULATED`.
- Fork events need special fd creation in the reader path because creating the new anon inode can sleep.
- HugeTLB has separate page-table checks and registration alignment rules.
- `UFFD_FEATURE_SIGBUS` and `UFFD_USER_MODE_ONLY` can bypass queueing and force normal SIGBUS behavior for disallowed faults.

## Cross-File Relationships
- Relies on mm/userfaultfd infrastructure declared in `include/linux/userfaultfd_k.h` and mm helpers such as `mfill_atomic_copy()`, `mfill_atomic_zeropage()`, `mfill_atomic_continue()`, `mfill_atomic_poison()`, `mwriteprotect_range()`, and `move_pages()`.
- VMA helpers such as `userfaultfd_register_range()`, `userfaultfd_clear_vma()`, `userfaultfd_release_all()`, and `vma_can_userfault()` are supplied by mm code.
- Exposes syscall behavior to userspace ABI in `include/uapi/linux/userfaultfd.h`.

## Risks / Review Notes
- Lock ordering is delicate: comments explicitly require `fd_wqh.lock` before `fault_pending_wqh.lock`.
- Wait queue entry lifetime relies on careful `list_del()`/`list_del_init()` behavior and stack-allocated wait entries.
- Returning the wrong fault code while a context is released can livelock GUP or cause unintended SIGBUS.
- Range validation must prevent wraparound and invalid page alignment; unaligned source is allowed only where explicitly intended.
- Feature bits and ioctl masks are ABI-sensitive.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/userfaultfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/utimes.c -->
# File Research: sources/os/linux/linux/fs/utimes.c

## Purpose
Implements timestamp update syscalls: `utimensat`, older `utime`/`utimes`/`futimesat` variants, and 32-bit time compatibility variants. Provides the shared VFS helper `vfs_utimes()`.

## Main Functions
- `nsec_valid()`: accepts normal nanoseconds plus `UTIME_NOW` and `UTIME_OMIT`.
- `vfs_utimes()`: builds an `iattr`, obtains mount write access, calls `notify_change()`, and handles delegated inode retry.
- `do_utimes_path()`: validates pathname flags, does lookup with optional symlink following, retries stale paths with `LOOKUP_REVAL`.
- `do_utimes_fd()`: applies updates to an open fd path.
- `do_utimes()`: dispatches fd vs path operation.
- `SYSCALL_DEFINE4(utimensat)`: copies two `__kernel_timespec` values and short-circuits when both are `UTIME_OMIT`.
- Legacy syscall helpers under `__ARCH_WANT_SYS_UTIME`: `futimesat`, `utimes`, `utime`.
- Compatibility syscalls under `CONFIG_COMPAT_32BIT_TIME`: `utime32`, `utimensat_time32`, and timeval32 variants.

## Important Design Points
- `times == NULL` means touch both atime and mtime to current time with `ATTR_TOUCH`.
- Explicit timestamp arrays set `ATTR_TIMES_SET`, even when both individual timestamps are omitted or `UTIME_NOW`.
- Both `UTIME_NOW` values collapse to `times = NULL`.
- Old timeval-based APIs reject microsecond values outside `[0, 999999]`; this also rejects `UTIME_NOW`/`UTIME_OMIT`, which are only valid for `utimensat`.
- `AT_EMPTY_PATH` and `AT_SYMLINK_NOFOLLOW` are the only accepted path flags; fd mode rejects all flags.

## Cross-File Relationships
- Uses VFS permission/setattr machinery via `notify_change()`, `mnt_want_write()`, path lookup, and delegation breaking.
- Exported `vfs_utimes()` is available to other kernel code.

## Risks / Review Notes
- `UTIME_OMIT` for both timestamps must return success without path lookup, preserving POSIX/Linux ABI behavior.
- Delegation retry must drop and reacquire inode state correctly through `break_deleg_wait()`.
- Compatibility paths need careful range checking before microseconds are multiplied to nanoseconds.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/utimes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/Kconfig -->
# File Research: sources/os/linux/linux/fs/vboxsf/Kconfig

## Purpose
Defines the kernel configuration option for VirtualBox guest shared-folder filesystem support.

## Main Contents
- `config VBOXSF_FS`: tristate option named “VirtualBox guest shared folder (vboxsf) support”.
- Depends on `(ARM64 || X86) && VBOXGUEST`.
- Selects `NLS`.
- Help text explains it implements the Linux guest side of folders exported by a VirtualBox host.

## Cross-File Relationships
- Controls compilation through `fs/vboxsf/Makefile`.
- Dependency on `VBOXGUEST` matches the wrapper layer’s use of VirtualBox guest HGCM services.

## Risks / Review Notes
- Architecture and guest-driver dependencies are essential; the source comments note assumptions around host data alignment and supported platforms.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/Makefile -->
# File Research: sources/os/linux/linux/fs/vboxsf/Makefile

## Purpose
Builds the vboxsf filesystem module.

## Main Contents
- Adds `vboxsf.o` when `CONFIG_VBOXSF_FS` is enabled.
- Aggregates module objects: `dir.o`, `file.o`, `utils.o`, `vboxsf_wrappers.o`, and `super.o`.

## Cross-File Relationships
- `shfl_hostintf.h` and `vfsmod.h` are headers used by the listed implementation objects.

## Risks / Review Notes
- No conditional object selection; feature differences are handled at runtime or via broader config.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/dir.c -->
# File Research: sources/os/linux/linux/fs/vboxsf/dir.c

## Purpose
Implements vboxsf directory file operations, dentry revalidation, and directory inode operations such as lookup, create, mkdir, atomic open, unlink/rmdir, rename, and symlink.

## Main Functions
- Directory file ops:
  - `vboxsf_dir_open()`: opens the host directory, reads all entries into a cached `vboxsf_dir_info`, then closes the host handle.
  - `vboxsf_dir_release()`: frees cached directory information.
  - `vboxsf_dir_iterate()` / `vboxsf_dir_emit()`: emits cached host entries to VFS with fake inode numbers.
  - `vboxsf_get_d_type()`: maps SHFL file type bits to Linux `DT_*`.
- Dentry handling:
  - `vboxsf_dentry_revalidate()`: rejects RCU lookup, revalidates positive dentries, and confirms negative dentries still do not exist.
- Directory inode ops:
  - `vboxsf_dir_lookup()`: stats the host path and creates/initializes a new inode.
  - `vboxsf_dir_create()` and wrappers `vboxsf_dir_mkfile()` / `vboxsf_dir_mkdir()`: create files/directories on the host and instantiate dentries.
  - `vboxsf_dir_atomic_open()`: lookup/create/open path for `O_CREAT`, attaching the host handle to the file.
  - `vboxsf_dir_unlink()`: removes files, directories, or symlinks with the correct SHFL flags.
  - `vboxsf_dir_rename()`: renames host paths, replacing existing targets for files.
  - `vboxsf_dir_symlink()`: creates host symlink and instantiates the resulting inode.

## Important Design Points
- Directories are snapshotted at open time by `vboxsf_dir_read_all()`; iteration walks cached variable-length `shfl_dirinfo` records.
- Fake inode numbers are derived from `ctx->pos + 1`; overflow truncates directory iteration on 32-bit inode configurations.
- Name conversion through NLS can skip individual invalid entries rather than failing the whole directory iteration.
- Parent inodes set `force_restat` after mutations so later revalidation pulls host-updated metadata.
- `atomic_open` handles newly-created files by preserving the host handle and installing it as `file->private_data`.

## Cross-File Relationships
- Uses `vboxsf_create_at_dentry()`, `vboxsf_dir_read_all()`, `vboxsf_path_from_dentry()`, `vboxsf_stat_dentry()`, and inode helpers from `utils.c`.
- Uses host operations from `vboxsf_wrappers.c`: create, close, remove, rename, symlink.
- Publishes `vboxsf_dir_fops`, `vboxsf_dentry_ops`, and `vboxsf_dir_iops` declared in `vfsmod.h`.

## Risks / Review Notes
- Host-provided directory data is variable-sized and only bounds-checked against buffer usage; corrupt host data triggers warnings and stops emission.
- Directory snapshots can become stale if host-side changes occur after open.
- RCU path walk is unsupported for dentry revalidation.
- Rename rejects all VFS rename flags, so newer rename semantics such as exchange or noreplace are unsupported.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/file.c -->
# File Research: sources/os/linux/linux/fs/vboxsf/file.c

## Purpose
Implements vboxsf regular file operations, pagecache address-space operations, mmap setup, open-handle tracking, and symlink target reading.

## Main Functions
- Handle management:
  - `vboxsf_create_sf_handle()`: wraps a host handle, records access flags, and links it onto the inode handle list.
  - `vboxsf_release_sf_handle()` / `vboxsf_handle_release()`: remove and close host handles via kref.
- File operations:
  - `vboxsf_file_open()`: translates Linux open flags to SHFL create/access flags and opens or creates the host file.
  - `vboxsf_file_release()`: writes back dirty pages before closing the handle.
  - `vboxsf_file_mmap_prepare()` and `vboxsf_vma_close()`: install filemap mmap ops and force writeback when VMAs close.
  - `vboxsf_reg_fops`: generic read/write, mmap, open/release, splice, and noop fsync.
- Address-space operations:
  - `vboxsf_read_folio()`: reads a page from the host handle and zero-fills the tail.
  - `vboxsf_get_write_handle()`: finds a writable host handle for writeback.
  - `vboxsf_writepages()`: writes dirty folios using an open writable handle.
  - `vboxsf_write_end()`: writes copied bytes to the host, updates size, and marks full folios uptodate when appropriate.
  - `vboxsf_reg_aops`: hooks read, writeback, dirtying, simple write begin/end, migration.
- Symlinks:
  - `vboxsf_get_link()`: asks the host for symlink target.
  - `vboxsf_lnk_iops`: exposes `get_link` and fileattr query.

## Important Design Points
- Open flag mapping preserves read/write/append access and uses SHFL result codes because host API return status alone is not enough.
- The driver has no host change notifications, inode generation, or file locking support. It relies on open-time/stat-time revalidation in `utils.c`.
- Guest writes are pushed on close and VMA close so host-side readers can see updates.
- Writeback requires a still-open writable handle; if no such handle exists, `writepages()` returns `-EBADF`.
- Partial writes do not mark folios uptodate unless the whole folio was written.

## Cross-File Relationships
- Uses host read/write/create/close/readlink wrappers from `vboxsf_wrappers.c`.
- Uses `vboxsf_path_from_dentry()` and inode state from `utils.c`/`vfsmod.h`.
- `vboxsf_reg_aops` is installed by `vboxsf_init_inode()` in `utils.c`.

## Risks / Review Notes
- Cache coherency with host-side modifications is limited; read_iter deliberately relies only on revalidation before/open rather than per-read stats.
- Writeback can fail if dirty pages outlive writable handles.
- `noop_fsync` means fsync does not issue an explicit host flush here.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/shfl_hostintf.h -->
# File Research: sources/os/linux/linux/fs/vboxsf/shfl_hostintf.h

## Purpose
Defines the VirtualBox Shared Folders guest-host ABI used by vboxsf: function numbers, constants, packed metadata structures, create/open flags, and HGCM parameter structures.

## Main Contents
- Protocol function numbers: map/query, create, close, read, write, list, information, remove, map/unmap folder, rename, flush, set UTF-8, readlink, symlink, and set symlink mode.
- Handle constants: `SHFL_ROOT_NIL`, `SHFL_HANDLE_NIL`, `SHFL_MAX_LEN`, `SHFL_MAX_MAPPINGS`, `SHFL_MAX_RW_COUNT`.
- String and metadata structures:
  - `struct shfl_string`: flexible UTF-8/UTF-16 string buffer with size and length.
  - `struct shfl_fsobjattr`, `shfl_fsobjattr_unix`, `shfl_fsobjinfo`: mode bits, Unix attributes, sizes, timestamps, allocation.
  - `struct shfl_dirinfo`: variable-length directory entry.
  - `struct shfl_fsproperties` and `shfl_volinfo`: filesystem/volume properties.
- Mode/type constants mirroring Unix file type and permission bits.
- Create/open ABI:
  - `enum shfl_create_result`.
  - `SHFL_CF_*` lookup, directory, action, access, deny, attribute, and append flags.
  - `struct shfl_createparms`.
- HGCM request parameter structures for map/unmap, create, close, read, write, list, information, remove, rename, readlink, and symlink.

## Important Design Points
- Structures shared with the host are packed or size-asserted using `VMMDEV_ASSERT_SIZE`.
- Variable-length protocol data is represented by offsets/sizes and flexible arrays.
- `shfl_string_buf_size()` centralizes buffer size calculation for host calls.
- Create/open uses result codes and returned handles together; `SHFL_HANDLE_NIL` can indicate an expected non-exceptional failure.

## Cross-File Relationships
- Included by `vfsmod.h`, then used by all vboxsf implementation files.
- `vboxsf_wrappers.c` fills these HGCM parameter structures for host calls.
- `dir.c`, `file.c`, `utils.c`, and `super.c` translate between VFS types and SHFL mode/metadata fields.

## Risks / Review Notes
- This is ABI-sensitive; changing layout, packing, enum values, or function numbers can break host compatibility.
- `struct shfl_dirinfo` is variable-length and can be unaligned when returned by the host; consumers must avoid unsafe assumptions.
- Comments include legacy/Windows-oriented protocol semantics that Linux callers must translate carefully.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/shfl_hostintf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/super.c -->
# File Research: sources/os/linux/linux/fs/vboxsf/super.c

## Purpose
Implements vboxsf filesystem registration, fs_context parsing, mount setup, superblock initialization, inode cache management, statfs, reconfiguration, and module lifecycle.

## Main Functions
- Mount option handling:
  - `vboxsf_parse_param()`: parses `nls`, `uid`, `gid`, `ttl`, `dmode`, `fmode`, `dmask`, and `fmask`.
  - `vboxsf_parse_monolithic()`: rejects obsolete binary mount data and uses generic parsing otherwise.
- Mount/superblock:
  - `vboxsf_fill_super()`: allocates `vboxsf_sbi`, loads NLS, sets up backing device, maps host folder, stats root, initializes root inode/dentry, and fills superblock fields.
  - `vboxsf_get_tree()`: ensures VirtualBox shared-folder setup then calls `get_tree_nodev()`.
  - `vboxsf_reconfigure()`: applies changed options to root inode.
- Inode/super ops:
  - `vboxsf_inode_init_once()`, `vboxsf_alloc_inode()`, `vboxsf_free_inode()`: manage `vboxsf_inode` cache and IDR removal.
  - `vboxsf_put_super()`: unmaps host folder, frees bdi id, unloads NLS, flushes RCU inode frees, destroys IDR.
  - `vboxsf_statfs()`: queries host volume info and fills `kstatfs`.
- Module setup:
  - `vboxsf_setup()`: creates inode cache, connects to guest device, sets UTF-8 mode, optionally enables symlink visibility.
  - `vboxsf_init()` / `vboxsf_fini()`: register/unregister filesystem and disconnect/destroy cache at module exit.

## Important Design Points
- Source string names the host shared folder to map.
- Default NLS is `CONFIG_NLS_DEFAULT`; UTF-8 avoids loading an NLS table.
- Readahead and IO pages are disabled on the backing device.
- `follow_symlinks` module parameter controls whether host resolves symlinks or guest sees symlink objects.
- `vboxsf_setup()` is global, serialized, and done lazily on first mount.
- `statfs()` reports synthetic file counts because host info may not provide meaningful inode counts.

## Cross-File Relationships
- Calls host wrappers: `vboxsf_connect()`, `vboxsf_disconnect()`, `vboxsf_set_utf8()`, `vboxsf_set_symlinks()`, `vboxsf_map_folder()`, `vboxsf_unmap_folder()`, `vboxsf_fsinfo()`.
- Uses inode initialization and stat helpers from `utils.c`.
- Publishes `vboxsf_fs_type` with ops implemented across vboxsf files.

## Risks / Review Notes
- Error paths must unmap folder, unload NLS, free IDA ids, destroy IDR, and free `sbi` in the correct order.
- Old binary mount data is explicitly unsupported.
- Case-sensitivity query failure is non-fatal, defaulting to case-sensitive behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/utils.c -->
# File Research: sources/os/linux/linux/fs/vboxsf/utils.c

## Purpose
Provides vboxsf utility functions for inode allocation/initialization, host stat/revalidation, setattr/getattr, path and character-set conversion, directory-buffer management, volume property query, and file attribute reporting.

## Main Functions
- Inodes:
  - `vboxsf_new_inode()`: allocates a VFS inode and assigns cyclic IDR inode number/generation.
  - `vboxsf_init_inode()`: maps SHFL metadata to VFS mode, ops, uid/gid, size, blocks, and timestamps.
- Host stat/revalidation:
  - `vboxsf_create_at_dentry()`, `vboxsf_stat()`, `vboxsf_stat_dentry()`: lookup/stat host objects.
  - `vboxsf_inode_revalidate()`: TTL/force-based restat; reinitializes inode and invalidates pagecache when mtime increases.
- VFS attributes:
  - `vboxsf_getattr()`: handles statx sync flags and fills attributes.
  - `vboxsf_setattr()`: opens host object for attribute write, separately sets mode/times and size, closes handle, and restats.
  - `vboxsf_fileattr_get()`: reports casefold flags for case-insensitive host shares.
- Paths and NLS:
  - `vboxsf_path_from_dentry()`: converts a Linux dentry path to an aligned UTF-8 `shfl_string`.
  - `vboxsf_nlscpy()`: converts host UTF-8 names to mounted NLS encoding.
- Directory cache helpers:
  - `vboxsf_dir_info_alloc()` / `vboxsf_dir_info_free()`.
  - `vboxsf_dir_read_all()`: loops host directory listing into 16 KiB buffers.
- Host volume:
  - `vboxsf_query_case_sensitive()`: queries host volume properties and stores case-insensitive state.

## Important Design Points
- Inode modes are synthesized from host mode plus mount `dmode`/`fmode` and masks.
- `S_NOATIME | S_NOCMTIME` are set because timestamps come from the host.
- Revalidation uses dentry `d_time` plus mount TTL unless `force_restat` is set.
- Pagecache invalidation is mtime-based and can be triggered by guest writes as well as host writes.
- `setattr()` handles file size separately from other file info because the host API requires separate information modes.
- Directory read treats positive end-of-dir and `-EILSEQ` as non-fatal completion.

## Cross-File Relationships
- Used by `dir.c`, `file.c`, and `super.c`.
- Calls wrappers in `vboxsf_wrappers.c`.
- Uses ABI definitions from `shfl_hostintf.h` through `vfsmod.h`.

## Risks / Review Notes
- Host-side mutation detection is best-effort and mtime-based.
- Path conversion must fit within `PATH_MAX` minus SHFL header and NUL.
- `vboxsf_setattr()` ignores ctime because userspace cannot set it directly.
- IDR inode number wrap increments generation; consumers must tolerate synthetic inode identities.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/vboxsf_wrappers.c -->
# File Research: sources/os/linux/linux/fs/vboxsf/vboxsf_wrappers.c

## Purpose
Wraps VirtualBox HGCM shared-folder service calls in Linux-friendly functions used by the vboxsf filesystem.

## Main Functions
- Connection:
  - `vboxsf_connect()`: connects to `VBoxSharedFolders` HGCM service and stores client id.
  - `vboxsf_disconnect()`: disconnects from the service.
  - `vboxsf_call()`: common HGCM call wrapper converting VirtualBox status to Linux errno.
- Folder mapping:
  - `vboxsf_map_folder()` / `vboxsf_unmap_folder()`: map and unmap host shared folder roots.
- Object operations:
  - `vboxsf_create()`, `vboxsf_close()`, `vboxsf_remove()`, `vboxsf_rename()`.
  - `vboxsf_read()` / `vboxsf_write()`: perform handle-based I/O and update byte counts.
  - `vboxsf_dirinfo()`: list directory entries and converts `VERR_NO_MORE_FILES` to positive `1`.
  - `vboxsf_fsinfo()`: get/set file or volume information.
  - `vboxsf_readlink()` / `vboxsf_symlink()`.
  - `vboxsf_set_utf8()` / `vboxsf_set_symlinks()`.

## Important Design Points
- All host calls use a fixed requestor mask `SHFL_REQUEST`.
- Parameters are explicitly typed as 32-bit, 64-bit, kernel linear address input/output, or optional zero address.
- `vboxsf_create()` may return success even when a file was not opened or created; callers must inspect `create_parms->handle` and `result`.
- `vboxsf_dirinfo()` returns `0` for data, `1` for end-of-directory, or negative errno for failure.

## Cross-File Relationships
- Consumes ABI structs from `shfl_hostintf.h`.
- Called by all higher-level vboxsf VFS code.
- Relies on VirtualBox guest utilities from `linux/vbox_utils.h` and status mapping from `linux/vbox_err.h`.

## Risks / Review Notes
- Host status and Linux errno are both relevant in some cases; `map_folder()` and `dirinfo()` explicitly inspect raw status.
- Pointer size fields must match actual SHFL buffer sizes to avoid malformed HGCM calls.
- Global `vboxsf_client_id` assumes serialized setup/teardown from `super.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/vboxsf_wrappers.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/vfsmod.h -->
# File Research: sources/os/linux/linux/fs/vboxsf/vfsmod.h

## Purpose
Internal vboxsf header defining shared data structures, constants, operation declarations, and cross-file function prototypes.

## Main Contents
- Constants/macros:
  - `DIR_BUFFER_SIZE` set to 16 KiB.
  - `VBOXSF_SBI()` and `VBOXSF_I()` accessors.
- Mount/context state:
  - `struct vboxsf_options`: ttl, uid/gid, mode override flags, modes, masks.
  - `struct vboxsf_fs_context`: parsed options and NLS name.
  - `struct vboxsf_sbi`: per-mount state including root info, inode IDR, NLS table, root handle, bdi id, and case-insensitive flag.
- Inode/directory state:
  - `struct vboxsf_inode`: force-restat flag, handle list/mutex, embedded VFS inode.
  - `struct vboxsf_dir_info` and `struct vboxsf_dir_buf`: cached directory listing storage.
- Extern declarations for inode/file/dentry/address-space ops.
- Prototypes for file, utility, and host wrapper functions.

## Important Design Points
- `handle_list_mutex` is the synchronization point for open handles on an inode.
- `ino_idr_lock` protects synthetic inode-number allocation and removal.
- The header centralizes module-internal API boundaries without exposing them outside vboxsf.

## Cross-File Relationships
- Includes `shfl_hostintf.h`.
- Used by every vboxsf implementation file.

## Risks / Review Notes
- Changes to shared structs affect multiple implementation files and inode lifetime behavior.
- `force_restat` is an int flag, not atomic; usage depends on VFS serialization and best-effort cache coherency.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/vboxsf/vfsmod.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/verity/Kconfig -->
# File Research: sources/os/linux/linux/fs/verity/Kconfig

## Purpose
Defines configuration options for fs-verity and optional builtin signature verification.

## Main Contents
- `config FS_VERITY`: bool option for read-only file-based authenticity protection.
  - Depends on `PAGE_SHIFT <= 16`.
  - Selects hash info and SHA-256/SHA-512 library support.
  - Help explains Merkle-tree verification for supported filesystems.
- `config FS_VERITY_BUILTIN_SIGNATURES`: optional builtin signature support.
  - Depends on `FS_VERITY`.
  - Selects `SYSTEM_DATA_VERIFICATION`.
  - Help warns that builtin signatures are not the only or always best signature mechanism.

## Cross-File Relationships
- Controls objects in `fs/verity/Makefile`.
- Supported filesystems call fs-verity helpers through `struct fsverity_operations`.

## Risks / Review Notes
- `PAGE_SHIFT <= 16` is tied to the pagecache Merkle-tree caching layout.
- Builtin signature support adds policy-sensitive keyring and PKCS#7 verification paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/verity/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/verity/Makefile -->
# File Research: sources/os/linux/linux/fs/verity/Makefile

## Purpose
Builds fs-verity implementation objects.

## Main Contents
- `CONFIG_FS_VERITY` builds `enable.o`, `hash_algs.o`, `init.o`, `measure.o`, `open.o`, `pagecache.o`, `read_metadata.o`, and `verify.o`.
- `CONFIG_FS_VERITY_BUILTIN_SIGNATURES` additionally builds `signature.o`.

## Cross-File Relationships
- Matches the subsystem split: enabling, hash algorithms, initialization, digest reporting, metadata loading, pagecache helpers, metadata ioctl, data verification, and optional signatures.

## Risks / Review Notes
- Signature support is intentionally optional and isolated in `signature.o`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/verity/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/verity/enable.c -->
# File Research: sources/os/linux/linux/fs/verity/enable.c

## Purpose
Implements `FS_IOC_ENABLE_VERITY`: validates userspace enable arguments, builds the Merkle tree for a file, creates fs-verity metadata, and asks the filesystem to commit verity enablement.

## Main Functions
- Merkle construction:
  - `hash_one_block()`: zero-pads a partial block, hashes it, and appends digest into the next tree level buffer.
  - `write_merkle_tree_block()`: calls filesystem `write_merkle_tree_block()` operation.
  - `build_merkle_tree()`: reads file data, hashes data blocks upward through tree buffers, writes tree blocks, and returns root hash.
- Enable flow:
  - `enable_verity()`: creates descriptor, copies salt/signature, initializes tree params, calls filesystem begin/end hooks, builds tree, creates/caches `fsverity_info`, and rolls back on error.
  - `fsverity_ioctl_enable()`: validates ioctl args, permissions, file type, read mode, append flag, mount writability, and denies concurrent writes before calling `enable_verity()`.

## Important Design Points
- Empty files have an all-zero root hash special case.
- Merkle tree blocks are written through filesystem-specific storage hooks, but tree contents are filesystem-independent.
- `deny_write_access()` stabilizes file data while hashing.
- Inode lock serializes `begin_enable_verity()` and `end_enable_verity()`, but is not held during long tree construction.
- Descriptor is re-read through `fsverity_create_info()` validation logic before final commit.
- `fsverity_set_info()` occurs before `end_enable_verity()`; other users still require `S_VERITY`, which filesystem sets at the end.
- Rollback calls `end_enable_verity(filp, NULL, 0, tree_size)`.

## Cross-File Relationships
- Uses hash and tree parameter helpers from `hash_algs.c` and `open.c`.
- Uses `fsverity_create_info()`, `fsverity_set_info()`, `fsverity_remove_info()`.
- Requires filesystem `s_vop` methods: `begin_enable_verity`, `write_merkle_tree_block`, and `end_enable_verity`.

## Risks / Review Notes
- Filesystem hooks must maintain ordering: `S_VERITY` should be set only at the end of successful `end_enable_verity()`.
- A short read while building the tree is treated as corruption/logic failure.
- The code intentionally no longer drops pagecache after enabling, accepting a small residual race tradeoff documented in comments.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/verity/enable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/verity/fsverity_private.h -->
# File Research: sources/os/linux/linux/fs/verity/fsverity_private.h

## Purpose
Private fs-verity subsystem header defining internal constants, hash/tree metadata structures, cached inode metadata, and internal function prototypes.

## Main Contents
- `FS_VERITY_MAX_LEVELS`: implementation limit of 8 Merkle levels.
- `struct fsverity_hash_alg`: supported hash algorithm metadata.
- `union fsverity_hash_ctx`: SHA-256/SHA-512 initial state storage.
- `struct merkle_tree_params`: hash algorithm, optional salted initial state, block/tree geometry, zero digest, and level start offsets.
- `struct fsverity_info`: rhashtable node, tree params, root hash, file digest, inode pointer, and optional hash-block verification bitmap.
- `FS_VERITY_MAX_SIGNATURE_SIZE`.
- Prototypes for hash algorithms, init/logging, BPF digest kfunc setup, open/info cache, descriptor loading, optional signature verification, and verify workqueue.
- Includes trace event definitions.

## Important Design Points
- `fsverity_info` is cached globally by inode pointer and remains until inode cleanup.
- Merkle tree pages are not stored in `fsverity_info`; filesystems may cache them separately.
- Hash block verification bitmap is only needed when Merkle block size differs from page size.

## Cross-File Relationships
- Included by every fs-verity C file.
- Bridges public `linux/fsverity.h` interfaces with subsystem internals.

## Risks / Review Notes
- `FS_VERITY_MAX_LEVELS`, digest sizes, and descriptor size limits are security/format constraints.
- Cached metadata lifetime depends on filesystems calling `fsverity_cleanup_inode()` when evicting inodes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/verity/fsverity_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/verity/hash_algs.c -->
# File Research: sources/os/linux/linux/fs/verity/hash_algs.c

## Purpose
Defines and implements fs-verity hash algorithm support for SHA-256 and SHA-512.

## Main Functions
- `fsverity_get_hash_alg()`: validates and returns hash algorithm metadata by fs-verity algorithm number.
- `fsverity_prepare_hash_state()`: precomputes salted initial SHA state after zero-padding salt to the hash compression block size.
- `fsverity_hash_block()`: hashes one Merkle block, using precomputed salted state if present.
- `fsverity_hash_buffer()`: hashes arbitrary buffer data with SHA-256 or SHA-512.
- `fsverity_check_hash_algs()`: init-time sanity checks algorithm numbering, digest limits, power-of-two assumptions, and `HASH_ALGO_*` mappings.

## Important Design Points
- Algorithm index 0 must remain unallocated/reserved.
- Salt is padded to the hash compression block size to avoid buffered internal hash state and keep salted hashing efficient.
- Implementation assumes digest and hash block sizes are powers of two.
- Uses crypto library SHA routines directly rather than the asynchronous crypto API.

## Cross-File Relationships
- Used by Merkle tree construction, verification, descriptor digest computation, and measurement.
- Relies on `hash_digest_size[]` mapping from kernel hash info.

## Risks / Review Notes
- Adding a new algorithm requires preserving numbering semantics and updating sanity constraints.
- The salt precompute path allocates memory and must be freed via tree params cleanup.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/verity/hash_algs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/verity/init.c -->
# File Research: sources/os/linux/linux/fs/verity/init.c

## Purpose
Initializes the fs-verity subsystem and provides rate-limited logging.

## Main Functions
- `fsverity_init_sysctl()`: registers `/proc/sys/fs/verity` sysctls when enabled; includes `require_signatures` when builtin signatures are configured.
- `fsverity_msg()`: rate-limited printk helper with optional filesystem/inode context.
- `fsverity_init()`: late initcall that validates hash algorithms, initializes info cache, workqueue, sysctl, signature keyring, and BPF kfunc support.

## Important Design Points
- Logging is globally rate-limited to avoid flooding on repeated verification failures.
- `CREATE_TRACE_POINTS` is defined here for fs-verity trace events.
- Initialization panics indirectly if critical caches/workqueues/keyrings cannot be created.

## Cross-File Relationships
- Calls init functions from `hash_algs.c`, `open.c`, `verify.c`, `signature.c`, and `measure.c`.
- Sysctl variable `fsverity_require_signatures` is defined in `signature.c`.

## Risks / Review Notes
- `late_initcall` ordering assumes dependent kernel subsystems are ready.
- Sysctl table is empty unless builtin signature support contributes an entry.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/verity/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/verity/measure.c -->
# File Research: sources/os/linux/linux/fs/verity/measure.c

## Purpose
Implements APIs to retrieve the fs-verity digest enforced for a file, plus an optional BPF LSM kfunc for digest access.

## Main Functions
- `fsverity_ioctl_measure()`: handles `FS_IOC_MEASURE_VERITY`, validates user buffer digest capacity, returns algorithm id, digest size, and file digest.
- `fsverity_get_digest()`: kernel API returning raw digest and fs-verity/hash algorithm identifiers.
- BPF support under `CONFIG_BPF_SYSCALL`:
  - `bpf_get_fsverity_digest()`: fills a dynptr with `struct fsverity_digest` and digest bytes.
  - `bpf_get_fsverity_digest_filter()`: restricts kfunc use to BPF LSM programs.
  - `fsverity_init_bpf()`: registers the kfunc id set.

## Important Design Points
- Callers must use the algorithm id with the digest; comments warn that digest bytes alone are not meaningful.
- Ioctl returns `-ENODATA` for non-verity files and `-EOVERFLOW` if the user-provided digest area is too small.
- BPF dynptr output is zero-filled past the digest when larger than needed.
- BPF kfunc is LSM-only to avoid recursion.

## Cross-File Relationships
- Reads cached `fsverity_info` created by `open.c`.
- Uses hash algorithm table from `hash_algs.c`.
- Exported APIs are used by filesystems, IMA/LSM, and other kernel consumers.

## Risks / Review Notes
- Userspace ABI requires writing the header before digest data and preserving exact error behavior.
- BPF dynptr alignment and sizing checks are important for verifier/runtime safety.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/verity/measure.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/verity/open.c -->
# File Research: sources/os/linux/linux/fs/verity/open.c

## Purpose
Loads, validates, creates, caches, and cleans up per-inode fs-verity metadata when verity files are opened or enabled.

## Main Functions
- Tree parameter setup:
  - `fsverity_init_merkle_tree_params()`: validates hash algorithm/block size, computes Merkle tree levels, level offsets, size, page count, zero-block digest, and optional salted state.
- Descriptor/info creation:
  - `compute_file_digest()`: hashes descriptor excluding builtin signature and with `sig_size` zeroed.
  - `fsverity_create_info()`: allocates `fsverity_info`, initializes tree params, copies root hash, computes file digest, verifies signature, and allocates hash-block bitmap when needed.
- Info cache:
  - `fsverity_set_info()`: inserts info into rhashtable.
  - `__fsverity_get_info()`: looks up cached info by inode pointer.
  - `fsverity_free_info()`, `fsverity_remove_info()`, `fsverity_cleanup_inode()`: lifetime cleanup.
  - `fsverity_init_info_cache()`: initializes rhashtable and usercopy-safe kmem cache.
- Descriptor loading:
  - `validate_fsverity_descriptor()`: checks size, version, reserved bits, salt size, inode size match, and signature bounds.
  - `fsverity_get_descriptor()`: obtains descriptor size and contents via filesystem `get_verity_descriptor()`.
- Open hook:
  - `ensure_verity_info()`: loads and caches metadata, handling races where another opener inserted it first.
  - `__fsverity_file_open()`: rejects writable opens and ensures metadata is loaded.

## Important Design Points
- Merkle block size must be power-of-two, at least 1024, no larger than page size, and no larger than filesystem block size.
- Tree level order stores root level first in the tree area and leaf level last; `level_start[]` maps logical level to start block.
- Bitmap for verified hash blocks is capped indirectly to avoid excessive memory.
- Descriptor `data_size` must exactly match current inode size.
- Multiple racing openers can create duplicate `fsverity_info`; the loser frees its copy after rhashtable insertion race resolution.
- Cache lookup is guarded by `S_VERITY` in public helpers, while internal insertion can happen before final flag setting during enable.

## Cross-File Relationships
- Uses hash support from `hash_algs.c` and signature support from `signature.c`.
- Called by `enable.c`, `measure.c`, `read_metadata.c`, and filesystems through exported open/cleanup helpers.
- Requires filesystem `get_verity_descriptor()` operation.

## Risks / Review Notes
- Inode-pointer keyed rhashtable requires reliable cleanup at inode eviction.
- Tree size computations must avoid overflow and remain within `ULONG_MAX` page/hash block indexing.
- Descriptor validation is a security boundary; accepting mismatched size or reserved bits would weaken ABI guarantees.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/verity/open.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/verity/pagecache.c -->
# File Research: sources/os/linux/linux/fs/verity/pagecache.c

## Purpose
Provides generic pagecache helpers for filesystems storing fs-verity Merkle tree pages in their inode mapping, plus a helper to fill zero-hash ranges.

## Main Functions
- `generic_read_merkle_tree_page()`: reads a mapping folio and returns the requested page.
- `generic_readahead_merkle_tree()`: initiates pagecache readahead for Merkle tree pages if absent or not uptodate.
- `fsverity_fill_zerohash()`: fills a folio range with repeated zero-data-block digests.

## Important Design Points
- Filesystem callers must translate Merkle-tree-relative indexes to actual pagecache indexes before using the generic helpers.
- Readahead helper asserts the mapping invalidate lock is held.
- `fsverity_fill_zerohash()` requires offset and length alignment to digest size.

## Cross-File Relationships
- Used by filesystem-specific fs-verity operations.
- Zero digest comes from `fsverity_info.tree_params.zero_digest`.

## Risks / Review Notes
- Index translation is the caller’s responsibility; wrong offsets would verify against wrong tree data.
- Readahead uses unbounded pagecache readahead and must be called with appropriate locking.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/verity/pagecache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/verity/read_metadata.c -->
# File Research: sources/os/linux/linux/fs/verity/read_metadata.c

## Purpose
Implements `FS_IOC_READ_VERITY_METADATA`, allowing userspace to read the Merkle tree byte stream, descriptor, or builtin signature of a verity file.

## Main Functions
- `fsverity_read_merkle_tree()`: copies a requested Merkle tree byte range to userspace, with optional readahead.
- `fsverity_read_buffer()`: bounded copy from a kernel buffer to userspace.
- `fsverity_read_descriptor()`: loads descriptor, strips builtin signature, zeroes `sig_size`, and returns descriptor bytes.
- `fsverity_read_signature()`: returns builtin signature bytes or `-ENODATA`.
- `fsverity_ioctl_read_metadata()`: validates arguments, bounds length to `INT_MAX`, dispatches by metadata type.

## Important Design Points
- Merkle tree metadata is exposed as a byte stream, independent of Merkle block size.
- Readahead is issued over the requested page range when filesystem provides `readahead_merkle_tree`.
- Descriptor metadata intentionally excludes the builtin signature.
- Offset plus length overflow is rejected.

## Cross-File Relationships
- Uses cached `fsverity_info` from `open.c`.
- Uses filesystem `read_merkle_tree_page()` and optional `readahead_merkle_tree()` operations.
- Uses `fsverity_get_descriptor()` from `open.c`.

## Risks / Review Notes
- Copy loop must release mapped pages on all error paths.
- Return value is byte count read, 0 on EOF, or negative errno; partial reads take precedence over later errors.
- Metadata exposure must preserve exact descriptor/signature separation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/verity/read_metadata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/verity/signature.c -->
# File Research: sources/os/linux/linux/fs/verity/signature.c

## Purpose
Implements optional fs-verity builtin PKCS#7 signature verification against the `.fs-verity` keyring.

## Main Functions
- `fsverity_verify_signature()`: validates a file’s builtin signature over its formatted fs-verity file digest, enforces `require_signatures`, reports failures, and exposes valid signatures to LSMs.
- `fsverity_init_signature()`: allocates the `.fs-verity` keyring owned by root.
- Global `fsverity_require_signatures`: sysctl-controlled policy requiring signatures on all verity files.

## Important Design Points
- Signatures are checked whenever present, even if `require_signatures` is false, because LSMs rely on this behavior.
- If the keyring is empty, signed files are rejected with `-ENOKEY` without invoking the PKCS#7 parser.
- Formatted signed digest includes magic `"FSVerity"`, fs-verity hash algorithm number, digest size, and file digest.
- Valid signature bytes are passed to `security_inode_setintegrity()` with `LSM_INT_FSVERITY_BUILTINSIG_VALID`.

## Cross-File Relationships
- Called by `fsverity_create_info()` in `open.c`.
- Initialized from `init.c`.
- Sysctl registration for `require_signatures` is in `init.c`.

## Risks / Review Notes
- This is policy/security-sensitive; comments explicitly warn to discuss behavior changes with LSM maintainers.
- Keyring permissions allow root modification unless root restricts the keyring.
- Empty-keyring short-circuit reduces PKCS#7 attack surface.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/verity/signature.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/verity/verify.c -->
# File Research: sources/os/linux/linux/fs/verity/verify.c

## Purpose
Implements fs-verity data verification for reads, including Merkle tree traversal, hash block verification caching, bio/folio helpers, Merkle readahead, and the async verification workqueue.

## Main Functions
- Readahead:
  - `fsverity_readahead()`: starts readahead for Merkle tree pages needed to verify a data page range.
- Hash block cache:
  - `is_hash_block_verified()`: checks whether a hash block was already verified, using `PG_checked` when block size equals page size or a bitmap plus `PG_checked` generation marker otherwise.
- Verification:
  - `verify_data_block()`: verifies one data block by ascending the Merkle tree to root or an already-verified hash block, then descending and verifying each saved block.
  - `fsverity_init_verification_context()`: initializes pending block batching and enables two-block SHA-256 optimized hashing when available.
  - `fsverity_add_data_blocks()`: maps aligned data blocks from a locked non-uptodate folio into pending queue.
  - `fsverity_verify_pending_blocks()`: hashes pending data blocks and verifies them against the tree.
  - `fsverity_verify_blocks()`: public folio verification helper.
  - `fsverity_verify_bio()`: block-layer bio verification helper under `CONFIG_BLOCK`.
- Workqueue:
  - `fsverity_enqueue_verify_work()`: queues async verification work.
  - `fsverity_init_workqueue()`: creates high-priority per-CPU workqueue.

## Important Design Points
- Verification can stop ascending early when it hits a previously verified hash block, then descends to verify the path below it.
- Hash pages evicted and reloaded must be reverified; `PG_checked` is used as a new-page marker even when a separate bitmap tracks sub-page hash blocks.
- Memory barriers pair with `PG_checked` to ensure bitmap clearing is visible before later checked reads.
- Data blocks wholly beyond EOF must be zero-filled, because mmap can expose page portions past EOF when Merkle block size is smaller than page size.
- Supports optimized two-block SHA-256 finup when available.
- Corruption logs include position, level, expected hash, and actual hash.
- Async workqueue is high priority and per-CPU, avoiding unbound crypto work due to scheduler latency concerns.

## Cross-File Relationships
- Uses tree params and cached info from `open.c`.
- Calls filesystem `read_merkle_tree_page()` and optional `readahead_merkle_tree()`.
- Exported helpers are called by filesystems from read-folio/readahead/bio completion paths.

## Risks / Review Notes
- Callers must pass locked, not-yet-uptodate folios with length/offset aligned to Merkle block size.
- All mapped pages must be unmapped/released on failure paths; the code has explicit cleanup loops.
- Verification cache correctness depends on `PG_checked` and bitmap memory ordering.
- A failed verification sets bio status to `BLK_STS_IOERR` or returns false for folio callers; filesystems must propagate that correctly.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/verity/verify.c -->