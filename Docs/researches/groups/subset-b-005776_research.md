# subset-b-005776 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/userfaultfd.c -->
# sources/distributed-fs/ceph-client/fs/userfaultfd.c

Purpose: Implements the Linux `userfaultfd` ABI: creating userfaultfd contexts, registering VMA ranges for missing/minor/write-protect faults, delivering page-fault and mapping-change events to userspace, and applying userspace resolutions through `UFFDIO_*` ioctls.

Important APIs, types, and functions: Defines local wait/event helpers around `struct userfaultfd_ctx`, `struct userfaultfd_wait_queue`, `struct userfaultfd_fork_ctx`, `struct userfaultfd_unmap_ctx`, and `struct userfaultfd_wake_range`. Externally relevant functions include `handle_userfault()`, `dup_userfaultfd()`, `dup_userfaultfd_complete()`, `dup_userfaultfd_fail()`, `mremap_userfaultfd_prep()`, `mremap_userfaultfd_complete()`, `mremap_userfaultfd_fail()`, `userfaultfd_remove()`, `userfaultfd_unmap_prep()`, `userfaultfd_unmap_complete()`, `userfaultfd_wp_unpopulated()`, `userfaultfd_wp_async()`, and `SYSCALL_DEFINE1(userfaultfd)`. File operations route reads, poll, release, and ioctls through `userfaultfd_fops`; `/dev/userfaultfd` uses `USERFAULTFD_IOC_NEW`.

Control flow: `new_userfaultfd()` allocates a context, grabs the current mm, and publishes an anon inode fd. Userspace must call `UFFDIO_API`, which validates feature bits, reports available ioctls, and marks the context initialized. `UFFDIO_REGISTER` validates range alignment, VMA compatibility, ownership, hugetlb constraints, and requested modes before setting `VM_UFFD_*` flags. Page faults enter `handle_userfault()`, enqueue a stack wait entry, drop the fault lock, wake fd pollers, and sleep until userspace resolves the fault. Reads move pending faults to the active fault queue, return `struct uffd_msg`, and complete mapping events such as fork/remap/remove/unmap. Resolution ioctls call mm helpers such as `mfill_atomic_copy()`, `mfill_atomic_zeropage()`, `mwriteprotect_range()`, `mfill_atomic_continue()`, `mfill_atomic_poison()`, and `move_pages()`, then wake affected faults unless `DONTWAKE` is requested.

State and persistence: State is entirely in-memory: context refcounts, mm references, feature flags, `released`, `mmap_changing`, wait queues for pending faults, resolved faults, events, and fd pollers. Registered state lives in VMA flags and `vm_userfaultfd_ctx`. The sysctl `vm.unprivileged_userfaultfd` controls unprivileged kernel-fault handling; no on-disk data is written.

Dependencies and integration points: Integrates tightly with mm fault handling, VMA splitting/clearing helpers, hugetlb, PTE marker/write-protect support, anon inode fd creation, miscdevice registration, sysctl, poll/read/ioctl, capabilities, and LSM/security expectations around `CAP_SYS_PTRACE`. Mapping event hooks are called by fork, mremap, unmap, and remove paths.

Risks and test signals: Highest risks are missed wakeups during pending-to-active queue refile, mmap-lock retry mistakes, stale VMA ownership, races with release, wrong range validation, feature negotiation drift, and mm lifetime bugs. Test with blocking and nonblocking reads, poll on initialized/uninitialized fds, concurrent `UFFDIO_COPY/ZEROPAGE/CONTINUE/WAKE`, write-protect async/unpopulated modes, hugetlb and shmem minor faults, fork/remap/remove/unmap events, fd release while faults are sleeping, sysctl/capability denial, and `/proc/<pid>/fdinfo` counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/userfaultfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/utimes.c -->
# sources/distributed-fs/ceph-client/fs/utimes.c

Purpose: Implements VFS timestamp update helpers and the `utimensat`, `futimesat`, `utimes`, `utime`, and compat time32 syscall front ends.

Important APIs, types, and functions: Exports `vfs_utimes()`. Internal helpers include `nsec_valid()`, `do_utimes_path()`, `do_utimes_fd()`, `do_utimes()`, `do_futimesat()`, and `do_compat_futimesat()`, plus syscall definitions for native and `CONFIG_COMPAT_32BIT_TIME` variants.

Control flow: Syscalls copy and normalize userspace time structures, reject invalid nanosecond/usec fields, and short-circuit the double-`UTIME_OMIT` no-op before path lookup. `do_utimes()` dispatches to fd or path mode. Path mode resolves with `LOOKUP_FOLLOW` unless `AT_SYMLINK_NOFOLLOW` is set, retries stale dentries with `LOOKUP_REVAL`, then calls `vfs_utimes()`. `vfs_utimes()` obtains mount write access, builds `iattr` flags for touch, explicit set, `UTIME_NOW`, and `UTIME_OMIT`, calls `notify_change()` under the inode lock, and breaks delegations before retrying.

State and persistence: The only persistent effect is filesystem inode atime/mtime/ctime mutation through `notify_change()`. The helper deliberately sets `ATTR_TIMES_SET` for explicit calls even when both individual timestamps are omitted, preserving permission semantics.

Dependencies and integration points: Depends on VFS path lookup, file descriptor lookup, mount write accounting, idmapped mount handling via `mnt_idmap()`, inode locking, delegation breaking, user copy helpers, and architecture config symbols that select legacy syscalls.

Risks and test signals: Risks include permission regressions for `times == NULL` versus explicit times, invalid time truncation in legacy timeval paths, symlink and `AT_EMPTY_PATH` behavior, stale path retry mistakes, and delegation retry loops. Test no-op omit/omit, fd mode, path mode with and without symlink following, read-only mounts, delegated files, invalid nanoseconds/useconds, compat 32-bit times, and idmapped mount ownership checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/utimes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/Kconfig -->
# sources/distributed-fs/ceph-client/fs/vboxsf/Kconfig

Purpose: Declares the kernel configuration option for the VirtualBox guest shared folder filesystem.

Important APIs, types, and functions: Defines `CONFIG_VBOXSF_FS` as a tristate option named "VirtualBox guest shared folder (vboxsf) support". It depends on `(ARM64 || X86) && VBOXGUEST` and selects `NLS`.

Control flow: The Kconfig entry controls whether the vboxsf module is built in, built as a module, or omitted. Selecting it makes the Kbuild rules in the same directory build the vboxsf object set.

State and persistence: No runtime state. The selected config determines availability of the `vboxsf` filesystem type and whether NLS conversion support is linked.

Dependencies and integration points: Integrates with the VirtualBox guest driver (`VBOXGUEST`), architecture support limited to ARM64 and X86, and kernel NLS facilities used by mount option parsing and filename conversion.

Risks and test signals: Risks are build exposure on unsupported architectures or without the VirtualBox guest device. Test all three tristate modes, X86 and ARM64 configs, dependency exclusion, and module autoload by filesystem alias.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/Makefile -->
# sources/distributed-fs/ceph-client/fs/vboxsf/Makefile

Purpose: Provides Kbuild rules for compiling the vboxsf filesystem.

Important APIs, types, and functions: Uses `obj-$(CONFIG_VBOXSF_FS) += vboxsf.o` and composes `vboxsf-y` from `dir.o`, `file.o`, `utils.o`, `vboxsf_wrappers.o`, and `super.o`.

Control flow: When `CONFIG_VBOXSF_FS` is enabled, Kbuild links the listed objects into the single vboxsf module or built-in object. Directory operations, regular file operations, shared utilities, host-call wrappers, and superblock/module registration are all required pieces.

State and persistence: No runtime state. The object list determines which exported internal symbols are available at link time.

Dependencies and integration points: Integrates with Kbuild and the Kconfig option in this directory. The object grouping matches declarations in `vfsmod.h`.

Risks and test signals: Risks are missing an object after symbol changes or accidentally linking unused host ABI code. Test module and built-in builds and verify `modinfo vboxsf` exposes the filesystem alias from `super.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/dir.c -->
# sources/distributed-fs/ceph-client/fs/vboxsf/dir.c

Purpose: Implements vboxsf directory file operations, dentry revalidation, lookup, create, mkdir, atomic open, unlink/rmdir, rename, and symlink inode operations.

Important APIs, types, and functions: Defines `vboxsf_dir_fops`, `vboxsf_dentry_ops`, and `vboxsf_dir_iops`. Key helpers are `vboxsf_dir_open()`, `vboxsf_dir_emit()`, `vboxsf_dir_iterate()`, `vboxsf_dentry_revalidate()`, `vboxsf_dir_lookup()`, `vboxsf_dir_create()`, `vboxsf_dir_atomic_open()`, `vboxsf_dir_unlink()`, `vboxsf_dir_rename()`, and `vboxsf_dir_symlink()`.

Control flow: Opening a directory sends a host create/open request for the dentry, verifies `SHFL_FILE_EXISTS`, reads all entries into `vboxsf_dir_info`, and closes the host handle. Iteration walks buffered variable-sized `shfl_dirinfo` records and emits fake inode numbers based on position. Lookup stats the host path and instantiates a new VFS inode when found. Create and atomic open issue `SHFL_FN_CREATE`, instantiate dentries from returned host attributes, and optionally retain a host file handle for the opened file. Removal, rename, and symlink convert dentries to shared-folder paths and call the corresponding host wrappers.

State and persistence: Directory listings are cached only for the opened directory file. Persistent changes happen on the VirtualBox host shared folder via create/remove/rename/symlink host calls. Parent inodes set `force_restat` after mutations so later revalidation refreshes cached attributes.

Dependencies and integration points: Depends on `utils.c` for path conversion, inode allocation, stat, and revalidation; `file.c` for handle wrapping during atomic open; and `vboxsf_wrappers.c` for host HGCM calls. Integrates with VFS dcache, dentry operations, name lookup, and inode operation tables.

Risks and test signals: Risks include corrupt host directory records, fake inode overflow, stale dentries under host-side changes, path conversion failures, incorrect directory-versus-file rename flags, symlink support differences, and leaked handles on error. Test readdir with many and malformed names, NLS conversion failures, negative and positive dentry revalidation, exclusive create, atomic open create, unlink/rmdir/symlink, rename over existing targets, and parent timestamp restat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/file.c -->
# sources/distributed-fs/ceph-client/fs/vboxsf/file.c

Purpose: Implements vboxsf regular file operations, address-space operations, mmap behavior, host handle lifetime, pagecache read/writeback, and symlink target reads.

Important APIs, types, and functions: Defines `struct vboxsf_handle`, `vboxsf_create_sf_handle()`, `vboxsf_release_sf_handle()`, `vboxsf_reg_fops`, `vboxsf_reg_iops`, `vboxsf_reg_aops`, and `vboxsf_lnk_iops`. Internal paths include `vboxsf_file_open()`, `vboxsf_file_release()`, `vboxsf_file_mmap_prepare()`, `vboxsf_read_folio()`, `vboxsf_get_write_handle()`, `vboxsf_writepages()`, `vboxsf_write_end()`, and `vboxsf_get_link()`.

Control flow: Open maps Linux open flags to `SHFL_CF_*` create and access flags, calls host create/open, wraps the returned handle, and attaches it to `file->private_data`. Handles are refcounted and also listed per inode so writeback can find a writable host handle independent of the initiating file. Reads fill folios through `vboxsf_read()`, zero the tail, and mark completion. Writes go through generic buffered write paths, with `write_end()` immediately writing copied bytes to the host and writeback flushing dirty folios through an available writable handle. mmap installs filemap fault operations and flushes writes on VMA close.

State and persistence: Persistent data lives on the host filesystem. Guest state includes open host handles, the inode handle list, pagecache contents, and `force_restat` markers after writes or opens. Cache coherency is intentionally limited: host-side changes are detected primarily on open/revalidation by mtime comparison.

Dependencies and integration points: Depends on VFS generic file helpers, pagecache/folio APIs, writeback, mmap, krefs, and vboxsf host wrappers. Symlink reads use path conversion and `SHFL_FN_READLINK`.

Risks and test signals: Risks include host handle leaks, writeback without a writable handle, stale cached data after host-side writes, short host reads/writes, page tail zeroing mistakes, mmap write visibility, and symlink buffer truncation. Test read/write/truncate/append modes, buffered writeback after closing writers, mmap dirty close, host-side modification before and after open, unlink while open, and symlink target reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/shfl_hostintf.h -->
# sources/distributed-fs/ceph-client/fs/vboxsf/shfl_hostintf.h

Purpose: Defines the guest-to-host VirtualBox Shared Folders ABI used by vboxsf wrapper calls.

Important APIs, types, and functions: Declares SHFL function numbers, root and file handle sentinel values, `struct shfl_string`, mode/type flags, `struct shfl_fsobjattr`, `struct shfl_fsobjinfo`, `enum shfl_create_result`, create/access flags, `struct shfl_createparms`, `struct shfl_dirinfo`, volume/property structs, and HGCM parameter structs for map/unmap, create, close, read, write, list, readlink, information, remove, rename, and symlink. `shfl_string_buf_size()` computes wire buffer sizes.

Control flow: Runtime code fills these packed parameter structs with `vmmdev_hgcm_function_parameter` descriptors, then `vboxsf_call()` sends them to the host service. The host returns handles, result codes, byte counts, object info, directory entries, and volume information through these layouts.

State and persistence: The header defines protocol state but stores none itself. Its structs represent persistent host object attributes as observed or modified through the shared folder service, including times, size, allocation, mode, and optional Unix attributes.

Dependencies and integration points: Depends on `linux/vbox_vmmdev_types.h` and is consumed by all vboxsf implementation files. Layout assertions via `VMMDEV_ASSERT_SIZE` protect host ABI compatibility.

Risks and test signals: Risks are ABI layout drift, packed-struct alignment assumptions, wrong parameter direction tags, path length accounting, enum/value mismatch with the host, and oversized read/write buffers. Test against multiple VirtualBox host versions, 32-bit and 64-bit guests, symlink-capable and old hosts, long UTF-8 names, all file types, large I/O up to `SHFL_MAX_RW_COUNT`, and statfs volume info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/shfl_hostintf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/super.c -->
# sources/distributed-fs/ceph-client/fs/vboxsf/super.c

Purpose: Registers the vboxsf filesystem, parses mount/reconfigure options, connects to the VirtualBox shared folder host service, maps a host share into a superblock, and manages superblock/inode caches.

Important APIs, types, and functions: Defines mount parameters `nls`, `uid`, `gid`, `ttl`, `dmode`, `fmode`, `dmask`, and `fmask`; module parameter `follow_symlinks`; `vboxsf_super_ops`; `vboxsf_context_ops`; and `vboxsf_fs_type`. Main functions are `vboxsf_parse_param()`, `vboxsf_fill_super()`, `vboxsf_alloc_inode()`, `vboxsf_free_inode()`, `vboxsf_put_super()`, `vboxsf_statfs()`, `vboxsf_setup()`, `vboxsf_get_tree()`, `vboxsf_reconfigure()`, `vboxsf_init_fs_context()`, module init, and module exit.

Control flow: Mount setup lazily creates the inode cache, connects to the guest device, selects UTF-8 and symlink behavior, parses options, loads NLS when needed, allocates a BDI id, maps the named host folder, stats the root, initializes a root inode, and attaches `vboxsf_sbi` to the superblock. Reconfigure updates options and reapplies them to the root inode. Unmount unmaps the host folder, frees BDI/NLS/IDR state, and destroys superblock private data. Module exit disconnects and destroys the inode cache once global setup was performed.

State and persistence: Runtime state includes global setup flags, inode slab cache, BDI id allocator, the host client connection, and per-superblock `vboxsf_sbi` with options, root handle, NLS table, inode IDR, and root host attributes. Host folder mappings persist until unmount.

Dependencies and integration points: Integrates with fs_context mount API, anonymous superblocks, VFS inode allocation/freeing, NLS, backing-device info, VirtualBox guest HGCM wrappers, module parameters, and module/filesystem registration.

Risks and test signals: Risks include partial mount cleanup leaks, old binary mount data rejection, NLS lifetime mistakes, root inode initialization failures, remount option drift, stale IDR entries before RCU inode freeing, and guest-device removal. Test mount/unmount loops, invalid option masks, non-UTF8 names, old mount helper data, missing VirtualBox guest device, symlink mode toggle, statfs, reconfigure, and module unload after active mounts are gone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/utils.c -->
# sources/distributed-fs/ceph-client/fs/vboxsf/utils.c

Purpose: Provides shared vboxsf utility code for inode allocation/initialization, host stat operations, inode revalidation, getattr/setattr, path and filename charset conversion, and directory listing buffers.

Important APIs, types, and functions: Exports `vboxsf_new_inode()`, `vboxsf_init_inode()`, `vboxsf_create_at_dentry()`, `vboxsf_stat()`, `vboxsf_stat_dentry()`, `vboxsf_inode_revalidate()`, `vboxsf_getattr()`, `vboxsf_setattr()`, `vboxsf_path_from_dentry()`, `vboxsf_nlscpy()`, `vboxsf_dir_info_alloc()`, `vboxsf_dir_info_free()`, and `vboxsf_dir_read_all()`.

Control flow: New inodes get cyclic IDR inode numbers and generation bumps on wraparound. Initialization maps SHFL mode bits to Linux mode bits, applies mount masks/overrides, selects regular/directory/symlink operation tables, sets owner ids, size, block counts, and timestamps. Revalidation stats the host when TTL expires or `force_restat` is set, reinitializes the inode, and invalidates cached pages when mtime advanced. Setattr opens the host object for attribute writes, sends separate information calls for mode/times and size, then restats. Path conversion builds root-relative raw dentry paths and optionally converts through the configured NLS table to UTF-8.

State and persistence: Maintains guest inode numbers in the superblock IDR, inode cached attributes, pagecache invalidation state, and directory-list buffers. Persistent effects occur on the host through `SHFL_INFO_SET` for mode, times, and size.

Dependencies and integration points: Depends on VFS inode/dentry/path APIs, NLS conversion, folio/pagecache invalidation, IDR, mount options from `vboxsf_sbi`, and host wrappers for create, fsinfo, and directory info.

Risks and test signals: Risks include mode/type mismatches during revalidation returning `-ESTALE`, stale pagecache when mtime granularity or host changes are odd, path buffer overflow, invalid UTF-8/NLS conversion, setattr partial updates, IDR wrap generation behavior, and directory buffer leaks. Test TTL and forced restat paths, host-side edits, chmod/truncate/utime, non-ASCII names, long paths, type changes under cached dentries, directory reads with `-EILSEQ`, and inode number reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/vboxsf_wrappers.c -->
# sources/distributed-fs/ceph-client/fs/vboxsf/vboxsf_wrappers.c

Purpose: Wraps VirtualBox guest HGCM calls into typed vboxsf operations for mapping folders, opening/creating objects, I/O, metadata, directory listing, removal, rename, symlink, and protocol feature setup.

Important APIs, types, and functions: Defines global `vboxsf_client_id`, `vboxsf_connect()`, `vboxsf_disconnect()`, `vboxsf_call()`, `vboxsf_map_folder()`, `vboxsf_unmap_folder()`, `vboxsf_create()`, `vboxsf_close()`, `vboxsf_remove()`, `vboxsf_rename()`, `vboxsf_read()`, `vboxsf_write()`, `vboxsf_dirinfo()`, `vboxsf_fsinfo()`, `vboxsf_readlink()`, `vboxsf_symlink()`, `vboxsf_set_utf8()`, and `vboxsf_set_symlinks()`.

Control flow: `vboxsf_connect()` obtains the VirtualBox guest device and connects to the `VBoxSharedFolders` service, storing the client id. Each wrapper constructs the relevant `shfl_*` parameter block, marks pointer directions and sizes, calls `vboxsf_call()`, then copies back output fields such as root handles, byte counts, file counts, or host status. `vboxsf_call()` translates guest-device or host status failures into Linux errno values.

State and persistence: Persistent guest-side state is the HGCM client id. Host-side state includes mapped root handles and open object handles that must be closed or unmapped by callers.

Dependencies and integration points: Depends on `vboxguest` APIs (`vbg_get_gdev()`, `vbg_hgcm_connect()`, `vbg_hgcm_call()`, `vbg_hgcm_disconnect()`), VirtualBox status translation, and ABI structs from `shfl_hostintf.h`. Higher vboxsf layers depend on these wrappers for every host-visible operation.

Risks and test signals: Risks include wrong parameter type/direction, stale client id after device removal, missed output length updates, host status translation changes, and handle leaks from caller error paths. Test old host map-folder behavior, guest-device hot removal, read/write short counts, end-of-directory mapping from `VERR_NO_MORE_FILES`, statfs info, symlink feature negotiation, and all wrappers under host permission failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/vboxsf_wrappers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/vfsmod.h -->
# sources/distributed-fs/ceph-client/fs/vboxsf/vfsmod.h

Purpose: Central private header for the vboxsf filesystem, defining shared state structures, constants, operation-table declarations, and cross-file helper prototypes.

Important APIs, types, and functions: Defines `DIR_BUFFER_SIZE`, `VBOXSF_SBI()`, `VBOXSF_I()`, `struct vboxsf_options`, `struct vboxsf_fs_context`, `struct vboxsf_sbi`, `struct vboxsf_inode`, `struct vboxsf_dir_info`, and `struct vboxsf_dir_buf`. Declares all vboxsf operation tables and helper/wrapper functions used across `dir.c`, `file.c`, `utils.c`, `super.c`, and `vboxsf_wrappers.c`.

Control flow: This file has no executable control flow. It establishes the module-internal contracts: superblocks own mount options and host root handles, inodes embed VFS inode plus restat and handle-list state, and directory reads produce a list of fixed-size buffers containing variable-sized host entries.

State and persistence: Defines the in-memory state layout for mounted shared folders and cached inodes. Persistent host state is accessed through declared wrapper functions rather than stored here.

Dependencies and integration points: Includes backing-device and IDR support plus the shared-folder host interface. It is the integration point that lets each vboxsf translation unit share private structures without exposing them outside the module.

Risks and test signals: Risks are structure layout changes not reflected in allocation/free code, missing prototypes after API changes, and lock ownership misunderstandings for `handle_list_mutex` and `ino_idr_lock`. Test by building with sparse/lockdep and exercising open/writeback while handles are added and removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/vfsmod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/Kconfig -->
# sources/distributed-fs/ceph-client/fs/verity/Kconfig

Purpose: Defines configuration options for fs-verity and optional in-kernel builtin signature verification.

Important APIs, types, and functions: Defines `CONFIG_FS_VERITY`, depending on `PAGE_SHIFT <= 16` and selecting `CRYPTO_HASH_INFO`, `CRYPTO_LIB_SHA256`, and `CRYPTO_LIB_SHA512`. Defines `CONFIG_FS_VERITY_BUILTIN_SIGNATURES`, depending on `FS_VERITY` and selecting `SYSTEM_DATA_VERIFICATION`.

Control flow: Enabling `FS_VERITY` builds the core file-based Merkle tree verification code. Enabling builtin signatures adds keyring and PKCS#7 verification support compiled from `signature.c`.

State and persistence: No runtime state. The configuration determines whether filesystems can expose fs-verity ioctls and whether the `.fs-verity` keyring and signature sysctl exist.

Dependencies and integration points: Integrates with supported filesystems through `struct fsverity_operations`, with crypto library implementations for SHA-256/SHA-512, and with system data verification when builtin signatures are selected.

Risks and test signals: Risks include enabling on unsupported page sizes or omitting crypto dependencies. Test configs with and without builtin signatures, page-size constraints, and supported filesystems that select or call fs-verity helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/Makefile -->
# sources/distributed-fs/ceph-client/fs/verity/Makefile

Purpose: Provides Kbuild object selection for fs-verity core and optional builtin signature support.

Important APIs, types, and functions: Builds `enable.o`, `hash_algs.o`, `init.o`, `measure.o`, `open.o`, `pagecache.o`, `read_metadata.o`, and `verify.o` when `CONFIG_FS_VERITY=y`. Adds `signature.o` when `CONFIG_FS_VERITY_BUILTIN_SIGNATURES=y`.

Control flow: Kbuild links the listed translation units into the kernel fs-verity implementation. Optional signature code is excluded entirely when the config is disabled, relying on inline stubs in `fsverity_private.h`.

State and persistence: No runtime state. Object selection determines which exports and init paths are available.

Dependencies and integration points: Integrates with the Kconfig options and the private header’s conditional prototypes/stubs.

Risks and test signals: Risks are missing a core object after symbol movement or building signature code without its config dependencies. Test all config combinations and module-less built-in link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/enable.c -->
# sources/distributed-fs/ceph-client/fs/verity/enable.c

Purpose: Implements `FS_IOC_ENABLE_VERITY`, building a file’s Merkle tree, constructing and validating the fs-verity descriptor, caching `fsverity_info`, and asking the filesystem to finalize verity enablement.

Important APIs, types, and functions: Defines `struct block_buffer`, `hash_one_block()`, `write_merkle_tree_block()`, `build_merkle_tree()`, `enable_verity()`, and exported `fsverity_ioctl_enable()`.

Control flow: The ioctl copies and validates `fsverity_enable_arg`, requires a regular readable fd with write permission but no writable access, rejects append/dir/non-regular files, obtains mount write access, and calls `deny_write_access()`. `enable_verity()` creates a descriptor, copies salt and optional builtin signature, initializes Merkle parameters, calls filesystem `begin_enable_verity()` under inode lock, builds the Merkle tree by reading every data block and cascading hashes into tree blocks, creates/verifies `fsverity_info`, inserts it into the global hash, and calls filesystem `end_enable_verity()` with descriptor and tree size. On build or validation failure it rolls back with `end_enable_verity(NULL, 0, tree_size)`.

State and persistence: Writes Merkle tree blocks and the descriptor to filesystem-specific storage through `fsverity_operations`. On success the filesystem sets `S_VERITY`, making the file read-only and verifiable; in-memory `fsverity_info` is cached before finalization.

Dependencies and integration points: Depends on filesystem `begin_enable_verity`, `write_merkle_tree_block`, and `end_enable_verity` operations, kernel reads, mount write accounting, file write denial, signals, tracepoints, hash helpers, descriptor parsing, and optional signature verification.

Risks and test signals: Risks include racing file size changes, partial tree writes, descriptor/signature size overflow, block-size incompatibility, rollback failures, stale pagecache assumptions, and finalization without `S_VERITY`. Test empty files, large files, interrupted builds, invalid salt/signature/reserved fields, unsupported hash/block sizes, concurrent writers, read-only mounts, duplicate enable, filesystem operation failures, and post-enable read verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/enable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/fsverity_private.h -->
# sources/distributed-fs/ceph-client/fs/verity/fsverity_private.h

Purpose: Private fs-verity header defining internal data structures, constants, logging helpers, conditional feature stubs, and prototypes shared by core implementation files.

Important APIs, types, and functions: Defines `FS_VERITY_MAX_LEVELS`, `struct fsverity_hash_alg`, `union fsverity_hash_ctx`, `struct merkle_tree_params`, `struct fsverity_info`, and `FS_VERITY_MAX_SIGNATURE_SIZE`. Declares hash, init/logging, BPF, open/info-cache, signature, and workqueue functions and includes fs-verity trace events.

Control flow: No runtime control flow. The header encodes invariants used by all fs-verity code: supported tree depth, hash algorithm metadata, precomputed salted hash state, tree topology fields, per-inode cached root/file digest, inode hash table linkage, and optional bitmap for verified hash blocks.

State and persistence: Defines the in-memory `fsverity_info` cache shape. Persistent descriptor and Merkle tree data are referenced through public `linux/fsverity.h` structures and filesystem operations, not stored in the header.

Dependencies and integration points: Depends on `linux/fsverity.h`, rhashtable support, crypto SHA contexts, trace events, optional BPF syscall support, and optional builtin signature config.

Risks and test signals: Risks are mismatch between declared invariants and implementation assumptions, especially digest/block power-of-two requirements, maximum tree levels, and conditional stubs. Test with compile coverage for `CONFIG_BPF_SYSCALL` and `CONFIG_FS_VERITY_BUILTIN_SIGNATURES`, plus large-tree and sub-page block-size cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/fsverity_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/hash_algs.c -->
# sources/distributed-fs/ceph-client/fs/verity/hash_algs.c

Purpose: Defines fs-verity supported hash algorithms and provides hashing helpers for Merkle blocks, descriptors, salted initial states, and startup sanity checks.

Important APIs, types, and functions: Exports `fsverity_hash_algs`, `fsverity_get_hash_alg()`, `fsverity_prepare_hash_state()`, `fsverity_hash_block()`, `fsverity_hash_buffer()`, and `fsverity_check_hash_algs()`.

Control flow: Algorithm lookup validates the fs-verity algorithm number and logs unknown ids. Salt preparation pads salt to the hash compression block size, initializes SHA-256 or SHA-512 state, feeds the padded salt, and returns a duplicated initial context. Block hashing either hashes directly when unsalted or clones the precomputed state, updates with a full Merkle block, and finalizes. Buffer hashing dispatches to one-shot SHA helpers. Init-time checks assert nonzero algorithm ids, maximum digest sizes, power-of-two digest and block sizes, and mapping to `HASH_ALGO_*`.

State and persistence: Static algorithm table is immutable. Salted hash states are allocated per Merkle tree parameter set and freed by callers. No persistent storage is written.

Dependencies and integration points: Used by enable, open, measure, signature, and verify paths. Depends on SHA library helpers, `hash_digest_size`, and fs-verity public algorithm numbering.

Risks and test signals: Risks include algorithm-number ABI drift, salted hashing incompatibility, missing digest-size validation, and BUG paths for unsupported algorithms. Test SHA-256 and SHA-512 enable/verify, salted and unsalted files, invalid algorithm ids, and startup sanity on modified algorithm tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/hash_algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/init.c -->
# sources/distributed-fs/ceph-client/fs/verity/init.c

Purpose: Performs fs-verity subsystem initialization and provides rate-limited logging helpers.

Important APIs, types, and functions: Defines optional sysctl table for `/proc/sys/fs/verity/require_signatures`, `fsverity_init_sysctl()`, exported-style internal `fsverity_msg()`, and `late_initcall(fsverity_init)`.

Control flow: At late init, fs-verity checks hash algorithms, initializes the `fsverity_info` cache/hash table, allocates the verification workqueue, registers sysctls, initializes builtin signature support if configured, and registers BPF kfuncs if configured. Logging uses a static ratelimit state and prefixes messages with superblock id and inode number when available.

State and persistence: Creates global in-memory subsystem state: info cache, rhashtable, workqueue, optional sysctl, keyring, and BPF registration. The sysctl changes runtime policy for requiring builtin signatures but does not persist across boot by itself.

Dependencies and integration points: Depends on tracepoint creation, sysctl, ratelimit, hash/open/verify/signature/measure initialization paths, and kernel initcall ordering.

Risks and test signals: Risks are init ordering failures, panic paths for cache/workqueue/keyring allocation, missing sysctl when signatures are configured, and excessive or suppressed corruption logging. Test boot with fs-verity enabled, sysctl visibility, signature config on/off, BPF config on/off, and forced allocation failure where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/measure.c -->
# sources/distributed-fs/ceph-client/fs/verity/measure.c

Purpose: Implements APIs for retrieving the digest of a verity file through ioctl, internal kernel callers, and optional BPF LSM kfuncs.

Important APIs, types, and functions: Exports `fsverity_ioctl_measure()` and `fsverity_get_digest()`. Under `CONFIG_BPF_SYSCALL`, defines `bpf_get_fsverity_digest()`, BTF kfunc id sets, filter `bpf_get_fsverity_digest_filter()`, and `fsverity_init_bpf()`.

Control flow: The ioctl requires existing `fsverity_info`, reads the caller-provided digest buffer size, rejects undersized buffers with `-EOVERFLOW`, writes the algorithm and digest size, then copies the cached file digest. `fsverity_get_digest()` returns zero for non-verity files or copies raw digest plus fs-verity and/or generic hash algorithm ids. The BPF kfunc validates dynptr size, alignment, and LSM program type, then writes as much digest as fits and zero-fills extra space.

State and persistence: Reads only cached `fsverity_info->file_digest`. No filesystem metadata is modified.

Dependencies and integration points: Used by userspace `FS_IOC_MEASURE_VERITY`, IMA/LSM-style kernel consumers, and optional BPF LSM programs. Depends on `fsverity_get_info()`, user copy helpers, BPF dynptr internals, and BTF kfunc registration.

Risks and test signals: Risks include returning a digest without an algorithm id, buffer-size ABI mistakes, BPF dynptr alignment bugs, and stale zero result before a verity inode has been opened and info cached. Test ioctl on non-verity and verity files, undersized and oversized buffers, SHA-256/SHA-512 files, kernel `fsverity_get_digest()` callers, and BPF LSM kfunc access filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/measure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/open.c -->
# sources/distributed-fs/ceph-client/fs/verity/open.c

Purpose: Initializes and caches per-inode fs-verity metadata when verity files are opened, validates descriptors, computes file digests, and manages the global `fsverity_info` rhashtable.

Important APIs, types, and functions: Defines `fsverity_info_cachep`, `fsverity_info_hash`, `fsverity_init_merkle_tree_params()`, `compute_file_digest()`, `fsverity_create_info()`, `fsverity_set_info()`, `__fsverity_get_info()`, `validate_fsverity_descriptor()`, `fsverity_get_descriptor()`, `ensure_verity_info()`, `__fsverity_file_open()`, `fsverity_free_info()`, `fsverity_remove_info()`, `fsverity_cleanup_inode()`, and `fsverity_init_info_cache()`.

Control flow: Merkle parameter initialization validates hash id, optional salt, block-size limits, digest/block arity, tree level counts, and tree size. Descriptor loading asks the filesystem first for size and then contents, checks version, reserved fields, salt size, inode data size, and signature bounds. `fsverity_create_info()` builds parameters, copies root hash, computes the descriptor digest with signature excluded, verifies optional signature, and allocates a hash-block verification bitmap for sub-page tree blocks. Open rejects writable fds and ensures info is cached, tolerating races by freeing duplicate allocations when another thread inserts first.

State and persistence: Maintains a global rhashtable keyed by inode pointer and slab-allocated `fsverity_info` objects that live until inode cleanup. It reads persistent descriptors through filesystem operations but does not write them.

Dependencies and integration points: Depends on filesystem `get_verity_descriptor`, inode `S_VERITY` policy in public wrappers, rhashtable, slab usercopy cache, hash helpers, signature verification, and page-size/tree-size assumptions used by verify code.

Risks and test signals: Risks include descriptor size confusion, inode size mismatch, duplicate info races, bitmap sizing overflow, salt-state leaks, writable-open bypass, and stale rhashtable entries on inode eviction. Test concurrent opens, eviction cleanup, corrupted descriptors, signature-required files, block sizes smaller than page size, huge files near tree limits, and writable open attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/pagecache.c -->
# sources/distributed-fs/ceph-client/fs/verity/pagecache.c

Purpose: Provides generic filesystem helpers for reading and readahead of Merkle tree pages stored in an inode’s pagecache.

Important APIs, types, and functions: Exports `generic_read_merkle_tree_page()` and `generic_readahead_merkle_tree()`.

Control flow: The read helper calls `read_mapping_folio()` for the adjusted pagecache index and returns the corresponding page within the folio. The readahead helper asserts the mapping invalidate lock is held, checks whether the starting folio is missing or not uptodate, and triggers unbounded pagecache readahead for the requested Merkle tree range.

State and persistence: Reads and populates pagecache state for Merkle tree pages. Persistent Merkle tree placement is filesystem-specific; callers must translate fs-verity-relative indices to actual pagecache indices before using these helpers.

Dependencies and integration points: Used by filesystems that store Merkle tree data in their own pagecache address space. Depends on folio/pagecache APIs, readahead control, and filesystem locking around invalidation.

Risks and test signals: Risks include incorrect index adjustment by callers, readahead without invalidate lock, stale or non-uptodate hash pages, and folio/page reference mistakes. Test filesystems using the generic helpers with shifted Merkle-tree offsets, cache hits/misses, readahead under concurrent invalidation, and large tree ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/pagecache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/read_metadata.c -->
# sources/distributed-fs/ceph-client/fs/verity/read_metadata.c

Purpose: Implements `FS_IOC_READ_VERITY_METADATA`, allowing userspace to read a verity file’s Merkle tree, descriptor without builtin signature, or builtin signature.

Important APIs, types, and functions: Defines `fsverity_read_merkle_tree()`, `fsverity_read_buffer()`, `fsverity_read_descriptor()`, `fsverity_read_signature()`, and exported `fsverity_ioctl_read_metadata()`.

Control flow: The ioctl requires cached `fsverity_info`, copies and validates the read request, rejects overflowed offset+length, clamps length to `INT_MAX`, and dispatches by metadata type. Merkle tree reads clamp to tree size, optionally trigger filesystem readahead under shared invalidate lock, iterate pages via `read_merkle_tree_page`, map pages, and copy byte ranges to userspace while checking fatal signals. Descriptor reads reload and validate the descriptor, zero `sig_size`, and copies only the fixed descriptor portion. Signature reads reload the descriptor and returns `-ENODATA` when no builtin signature exists.

State and persistence: Read-only access to persistent verity metadata through filesystem operations and pagecache. No state is modified except normal cache/readahead effects.

Dependencies and integration points: Depends on `fsverity_get_info()`, `fsverity_get_descriptor()`, filesystem `read_merkle_tree_page` and optional `readahead_merkle_tree`, user copy helpers, highmem mapping, and backing-dev/pagecache synchronization.

Risks and test signals: Risks include leaking builtin signatures through descriptor reads, offset overflow, partial copy semantics, signal interruption, wrong tree-size clamping, and filesystem page read errors. Test all metadata types, offsets at and past EOF, short buffers, missing signatures, corrupted descriptors, readahead-enabled filesystems, and user fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/read_metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/signature.c -->
# sources/distributed-fs/ceph-client/fs/verity/signature.c

Purpose: Implements optional fs-verity builtin signature verification against the kernel `.fs-verity` keyring.

Important APIs, types, and functions: Defines global `fsverity_require_signatures`, static `fsverity_keyring`, `fsverity_verify_signature()`, and `fsverity_init_signature()`.

Control flow: If no signature is present, verification succeeds unless `require_signatures` is set, in which case the file is rejected. If a signature is present but the keyring is empty, it returns `-ENOKEY` without invoking the PKCS#7 parser. Otherwise it builds a `fsverity_formatted_digest` containing magic, algorithm id, digest size, and cached file digest, calls `verify_pkcs7_signature()` against the fs-verity keyring, logs specific failures, and exposes valid signatures to LSMs with `security_inode_setintegrity()`.

State and persistence: Maintains the `.fs-verity` keyring and runtime sysctl-backed `fsverity_require_signatures` policy. It does not persist signatures; signatures are stored in filesystem verity descriptors.

Dependencies and integration points: Depends on keyrings, PKCS#7/system data verification, credentials, LSM integrity hooks, hash algorithm ids, and `fsverity_info` file digests. Initialized from `init.c` when builtin signatures are configured.

Risks and test signals: Risks include trusting empty keyrings, malformed PKCS#7 attack surface, algorithm-id mismatch, LSM notification failures, and policy surprises when signatures are verified even if not required. Test unsigned files with policy off/on, signed files with empty keyring, wrong certificate, malformed signatures, valid signatures, keyring restriction, and LSM integrity hook behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/signature.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/verify.c -->
# sources/distributed-fs/ceph-client/fs/verity/verify.c

Purpose: Verifies file data against fs-verity Merkle trees during reads and provides readahead and async workqueue helpers for filesystem integrations.

Important APIs, types, and functions: Defines `struct fsverity_pending_block`, `struct fsverity_verification_context`, `fsverity_readahead()`, `is_hash_block_verified()`, `verify_data_block()`, `fsverity_verify_blocks()`, optional `fsverity_verify_bio()`, `fsverity_enqueue_verify_work()`, and `fsverity_init_workqueue()`.

Control flow: Readahead maps a data page range to needed hash-page ranges at each Merkle level and calls filesystem `readahead_merkle_tree`. Verification batches one or two data blocks, maps their folio data, hashes them, then `verify_data_block()` ascends from leaf hashes to the root until it finds an already verified hash block or reaches the root. It then descends, hashing each unverified hash block, comparing expected versus real hashes, marking hash blocks verified, and finally comparing the data block hash. EOF-spanning sub-page blocks past file size must be all zeroes. Bio verification iterates folios from completed read bios and sets `BLK_STS_IOERR` on failure.

State and persistence: Uses per-inode `fsverity_info` root hash, tree topology, optional salted hash state, and hash-block verification state. Verification marks hash pages `PG_checked` or sets bitmap bits for sub-page block sizes; no persistent metadata is changed.

Dependencies and integration points: Called by filesystem read_folio/readahead/bio completion paths. Depends on filesystem `read_merkle_tree_page` and optional readahead operation, page/folio mapping, block layer when enabled, SHA optimized two-block hashing, tracepoints, and high-priority per-CPU workqueue.

Risks and test signals: Risks include trusting evicted hash pages, bitmap and `PG_checked` memory-ordering bugs, kmap nesting limits, corrupted-tree diagnostics, EOF zero verification, block alignment assumptions, and async verification latency. Test valid and corrupted data blocks, corrupted hash blocks at every level, cache eviction and reread, sub-page Merkle blocks, EOF partial pages, bio and non-bio filesystems, concurrent reads of the same hash blocks, and workqueue initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/verify.c -->
