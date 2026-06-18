# Group Research: group_1094_linux_stable_sources_os_linux_linux_stable_fs_userfaultfd_c_sources_f6fee40f2fd3

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/userfaultfd.c -->
# File Research: sources/os/linux/linux-stable/fs/userfaultfd.c

Implements Linux `userfaultfd`, the userspace page-fault handling facility exposed by the `userfaultfd(2)` syscall and `/dev/userfaultfd` misc device. It owns `struct userfaultfd_ctx` lifetime, fault and event wait queues, fault message generation, registration/unregistration, ioctl dispatch, wakeups, and integration hooks for fork, mremap, unmap, remove, write-protect, minor-fault, poison, copy, zero-page, continue, and page move operations.

Key flows:
- `handle_userfault()` is called from MM fault paths. It validates retry capability, constructs a `UFFD_EVENT_PAGEFAULT` message, queues the fault on `fault_pending_wqh`, releases the fault lock, wakes readers, sleeps, and relies on userspace ioctls or wakeups to resolve the fault.
- `userfaultfd_ctx_read()` moves page faults from the pending queue to the in-progress queue, returns `uffd_msg` records, and handles asynchronous events such as fork/remap/remove/unmap.
- `userfaultfd_register()` and `userfaultfd_unregister()` validate ranges, VMA compatibility, ownership by one context, hugepage alignment, write permissions, and supported modes before updating VMA userfault flags.
- `userfaultfd_copy()`, `userfaultfd_zeropage()`, `userfaultfd_continue()`, `userfaultfd_poison()`, `userfaultfd_writeprotect()`, and `userfaultfd_move()` translate UFFD ioctls into MM helper calls, store partial-completion counts back to userspace, and wake fault waiters unless `DONTWAKE` modes are used.

Concurrency is central. The file uses ctx refcounts, `mmap_changing`, `released`, `map_changing_lock`, waitqueue locks, `refile_seq`, explicit memory barriers, and careful list handling to avoid missed wakeups, use-after-free, and mmap-lock livelocks. Security policy gates kernel-fault-capable userfaultfds behind `CAP_SYS_PTRACE` or `vm.unprivileged_userfaultfd`; `UFFD_USER_MODE_ONLY` is always allowed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/userfaultfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/utimes.c -->
# File Research: sources/os/linux/linux-stable/fs/utimes.c

Implements VFS timestamp update syscalls and compatibility entry points: `utimensat`, older `utime`/`utimes`/`futimesat` where enabled, and 32-bit time variants. The central helper is `vfs_utimes()`, which validates nanosecond fields, handles `UTIME_NOW` and `UTIME_OMIT`, builds `struct iattr`, obtains mount write access, calls `notify_change()`, and retries delegated inodes through `break_deleg_wait()`.

Path and fd dispatch are split between `do_utimes_path()` and `do_utimes_fd()`. Path handling supports `AT_SYMLINK_NOFOLLOW` and `AT_EMPTY_PATH`, uses `filename_lookup()`, and retries stale lookups with `LOOKUP_REVAL`. File descriptor handling rejects flags and applies `vfs_utimes()` to the file path.

Compatibility code rejects invalid microsecond values before converting them to nanoseconds, avoiding truncated invalid values passing later validation. The main correctness concerns are preserving POSIX permission behavior through `notify_change()`, doing nothing when both times are `UTIME_OMIT`, and routing legacy ABI variants through one VFS timestamp update path.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/utimes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/vboxsf/Kconfig

Defines `CONFIG_VBOXSF_FS`, the VirtualBox guest shared-folder filesystem driver. It is tristate, depends on ARM64 or X86 plus `VBOXGUEST`, and selects NLS support for optional filename charset conversion.

The help text positions the driver as the Linux guest-side implementation for folders exported by VirtualBox hosts. It can be built-in or modular. The dependency on `VBOXGUEST` reflects that filesystem operations are mediated through the VirtualBox guest device and HGCM shared-folder service.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/vboxsf/Makefile

Builds the `vboxsf` module when `CONFIG_VBOXSF_FS` is enabled. The composite object consists of `dir.o`, `file.o`, `utils.o`, `vboxsf_wrappers.o`, and `super.o`.

This mirrors the driver split: directory and dentry operations, regular-file and mmap behavior, inode/path/NLS helpers, typed HGCM host-call wrappers, and mount/superblock/module setup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/vboxsf/dir.c

Implements vboxsf directory file operations, dentry validation, and directory inode operations. Directory open creates a host directory handle with `vboxsf_create_at_dentry()`, reads all directory entries from the host into `vboxsf_dir_info`, closes the host handle, and stores buffered entries in `file->private_data`.

`vboxsf_dir_iterate()` emits buffered entries using `dir_emit()`, synthesizing inode numbers from directory position and mapping VirtualBox mode bits to Linux `d_type`. It supports optional NLS conversion through `vboxsf_nlscpy()` and skips entries whose names fail conversion.

Lookup and dentry revalidation call host stat helpers and create/reinitialize Linux inodes via `vboxsf_new_inode()` and `vboxsf_init_inode()`. Create, mkdir, atomic open, unlink/rmdir, rename, and symlink translate VFS operations into host protocol calls, then mark parent inodes for restat when host metadata may have changed.

Important behavior: the driver rejects RCU lookup revalidation, does not support rename flags, bounds-checks variable-sized host directory records, and maps unsupported host symlink creation reported as read-only to `-EPERM`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/file.c -->
# File Research: sources/os/linux/linux-stable/fs/vboxsf/file.c

Implements vboxsf regular-file operations, address-space operations, mmap hooks, symlink readlink support, and host handle lifetime. `struct vboxsf_handle` wraps a host shared-folder handle, root id, access flags, refcount, and per-inode list linkage.

Open maps Linux open flags to VirtualBox create/access flags, calls `vboxsf_create_at_dentry()`, and tracks the returned handle in `file->private_data`. Release writes back dirty pagecache with `filemap_write_and_wait()` before closing the host handle so host-side readers can see guest writes.

Reads and writes use generic VFS helpers backed by `vboxsf_reg_aops`. `vboxsf_read_folio()` reads one page from the host and zero-fills the tail. `vboxsf_writepages()` finds an open write-capable handle and writes dirty folios back. `vboxsf_write_end()` writes only copied bytes and extends inode size if needed. mmap uses `filemap_fault` and flushes dirty pages when the VMA closes.

The file documents the driver’s caching model: host-side changes can occur without notification, so the guest only guarantees seeing host changes made before guest open/revalidation. Symlinks are read through `vboxsf_readlink()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/shfl_hostintf.h -->
# File Research: sources/os/linux/linux-stable/fs/vboxsf/shfl_hostintf.h

Defines the VirtualBox Shared Folders host-interface ABI used by the vboxsf driver. It contains function numbers, root and object handle constants, mode bits, packed wire structs, parameter counts, and helper constants for map/unmap folder, create/open, close, read, write, list, get/set information, remove, rename, readlink, symlink, UTF-8 selection, and symlink mode selection.

Important structures include:
- `shfl_string`, a variable-length UTF-8/UTF-16 path string with explicit byte size and length.
- `shfl_fsobjattr` and `shfl_fsobjinfo`, which carry host object attributes, sizes, timestamps, mode, and optional Unix/EA metadata.
- `shfl_createparms`, the bidirectional create/open request containing returned handle, result code, flags, and object info.
- HGCM parameter structs such as `shfl_create`, `shfl_read`, `shfl_write`, `shfl_list`, `shfl_information`, `shfl_remove`, `shfl_rename`, and `shfl_symlink`.

The file is ABI-sensitive: many structs are packed, size assertions are used, and values mirror VirtualBox host service expectations. Executable driver code depends on these definitions for pointer direction, parameter count, result interpretation, and buffer sizing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/shfl_hostintf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/super.c -->
# File Research: sources/os/linux/linux-stable/fs/vboxsf/super.c

Implements vboxsf filesystem registration, mount parsing, superblock creation, inode cache allocation, backing-device setup, and module lifetime. Mount options include `nls`, `uid`, `gid`, `ttl`, `dmode`, `fmode`, `dmask`, and `fmask`; `nls` cannot be changed during reconfigure.

`vboxsf_fill_super()` allocates `vboxsf_sbi`, loads optional NLS, allocates a BDI id, disables readahead/io pages, maps the requested shared-folder source through the host service, stats the root path, creates inode 0 as the root, and installs vboxsf super/dentry operations. Cleanup unwinds folder mapping, BDI id, NLS, IDR, and private state.

`vboxsf_setup()` serializes one-time module setup: inode cache creation, VirtualBox guest-device connection, UTF-8 mode selection, and optional host symlink visibility. `vboxsf_parse_monolithic()` rejects old binary mount data. Reconfigure applies changed options to the root inode. Module init registers the `vboxsf` filesystem; exit unregisters it, disconnects, flushes RCU inode frees, and destroys the inode cache.

The superblock uses anonymous backing storage via `kill_anon_super`, and `statfs` retrieves volume information from the host with `vboxsf_fsinfo()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/utils.c -->
# File Research: sources/os/linux/linux-stable/fs/vboxsf/utils.c

Provides vboxsf utility code for inode allocation/init, stat/revalidation, getattr/setattr, path conversion, NLS conversion, and directory buffer management.

`vboxsf_new_inode()` allocates Linux inodes and assigns synthetic inode numbers through an IDR, incrementing generation on wrap. `vboxsf_init_inode()` converts host `shfl_fsobjinfo` into Linux inode type, mode, ownership, size, blocks, timestamps, operations, and address-space ops, applying mount masks and forced modes.

Revalidation is host-stat based. `vboxsf_inode_revalidate()` honors the dentry TTL unless `force_restat` is set, restats the host object, reinitializes inode metadata, and invalidates the pagecache if mtime advanced. `vboxsf_getattr()` supports statx sync flags. `vboxsf_setattr()` opens the object for attribute writes, separately updates mode/times and size through `vboxsf_fsinfo()`, then restats.

Path conversion builds `shfl_string` paths from dentries, converting from configured NLS to UTF-8 when needed. Directory helpers allocate 16 KiB buffers, collect all host directory entries with `vboxsf_dirinfo()`, and treat host filename translation failure (`-EILSEQ`) as nonfatal.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/vboxsf_wrappers.c -->
# File Research: sources/os/linux/linux-stable/fs/vboxsf/vboxsf_wrappers.c

Wraps VirtualBox HGCM shared-folder service calls behind Linux-style helpers returning negative errno values. `vboxsf_connect()` locates the guest device and connects to the `"VBoxSharedFolders"` service, storing a global client id. `vboxsf_disconnect()` closes it. `vboxsf_call()` centralizes guest-device lookup, HGCM invocation, VirtualBox status capture, and status-to-errno conversion.

The remaining functions build typed HGCM parameter structs defined in `shfl_hostintf.h`: map/unmap folder, create/open, close, remove, rename, read, write, directory listing, file/volume information, readlink, symlink, UTF-8 mode, and symlink mode. Read/write/list/fsinfo update in/out byte-count fields after calls.

Important integration details: host create/open can return success while `create_parms->handle` remains nil and the result code explains why, so callers inspect both errno and returned fields. Directory listing maps the host “no more files” condition to positive `1`, which the utility layer treats as end-of-directory.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/vboxsf_wrappers.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/vfsmod.h -->
# File Research: sources/os/linux/linux-stable/fs/vboxsf/vfsmod.h

Private vboxsf module header. It includes the host ABI header and declares shared constants, private structs, operation tables, and cross-file helper prototypes.

Key private state:
- `vboxsf_options`: mount options for TTL, uid/gid, forced modes, and masks.
- `vboxsf_fs_context`: fs_context private parser state.
- `vboxsf_sbi`: per-superblock data including options, root host info, inode IDR, NLS table, root handle, and BDI id.
- `vboxsf_inode`: per-inode state with `force_restat`, open handle list, mutex, and embedded VFS inode.
- Directory buffer containers used to store host listing results.

The header defines `VBOXSF_SBI()` and `VBOXSF_I()` accessors and exposes the internal division between directory, file, utility, and host-wrapper modules.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/vboxsf/vfsmod.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/verity/Kconfig

Defines fs-verity configuration. `CONFIG_FS_VERITY` enables read-only file-based authenticity protection using a Merkle-tree mechanism analogous to dm-verity but per file. It depends on page size no larger than 64 KiB and selects SHA-256/SHA-512 library support and hash metadata.

The help text identifies supported filesystems as ext4, f2fs, and btrfs, and describes transparent read-time verification plus access to the root/file digest for auditing or authenticity workflows.

`CONFIG_FS_VERITY_BUILTIN_SIGNATURES` optionally adds in-kernel verification of builtin signatures and selects `SYSTEM_DATA_VERIFICATION`. The help warns that builtin signatures are not always the preferred trust model compared with userspace verification or IMA appraisal.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/verity/Makefile

Builds the fs-verity core from `enable.o`, `hash_algs.o`, `init.o`, `measure.o`, `open.o`, `pagecache.o`, `read_metadata.o`, and `verify.o` when `CONFIG_FS_VERITY` is enabled. `signature.o` is included only when builtin signature support is configured.

This mirrors the subsystem split: enabling and Merkle tree construction, hash algorithm support, initialization/logging, digest measurement, open-time descriptor loading, generic Merkle pagecache helpers, metadata read ioctl support, read-time verification, and optional PKCS#7 signature validation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/enable.c -->
# File Research: sources/os/linux/linux-stable/fs/verity/enable.c

Implements `FS_IOC_ENABLE_VERITY`. It validates the userspace enable argument, requires a writable-permitted regular file opened for read, rejects append-only/directories/non-regular files, obtains mount write access, and uses `deny_write_access()` to stabilize file contents while building the Merkle tree.

`build_merkle_tree()` hashes file data blocks, accumulates digest blocks per tree level, writes complete Merkle tree blocks through the filesystem’s `write_merkle_tree_block()` operation, handles zero-length files specially with an all-zero root hash, and aborts on fatal signals.

`enable_verity()` builds a descriptor with algorithm, block size, salt, optional builtin signature, file size, and root hash. It calls filesystem `begin_enable_verity()`, builds the tree outside the inode lock, creates and caches `fsverity_info`, inserts it before finalization, then calls `end_enable_verity()` to persist metadata and set `S_VERITY`. On failure it rolls back through `end_enable_verity(filp, NULL, ...)`.

The code deliberately does not drop pagecache after enable, documenting the performance/race tradeoff.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/enable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/fsverity_private.h -->
# File Research: sources/os/linux/linux-stable/fs/verity/fsverity_private.h

Private fs-verity subsystem header. It defines implementation limits and core private types: `FS_VERITY_MAX_LEVELS`, `fsverity_hash_alg`, `union fsverity_hash_ctx`, `merkle_tree_params`, and `fsverity_info`.

`merkle_tree_params` captures hash algorithm, salted initial hash state, digest/block sizes, arity, tree depth, total tree size/pages, and per-level block offsets. `fsverity_info` is the cached per-inode verification state stored in a global rhashtable and includes root hash, file digest, inode pointer, and optional hash-block verified bitmap.

The header declares internal helpers for hashing, initialization, descriptor loading, info-cache management, signature verification, BPF registration, verification workqueue setup, and tracepoint inclusion. It also provides logging wrappers `fsverity_warn()` and `fsverity_err()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/fsverity_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/hash_algs.c -->
# File Research: sources/os/linux/linux-stable/fs/verity/hash_algs.c

Defines fs-verity supported hash algorithms and hashing helpers. The table currently supports SHA-256 and SHA-512, mapping fs-verity UAPI algorithm numbers to crypto/hash algorithm ids, digest sizes, and compression block sizes.

`fsverity_get_hash_alg()` validates an algorithm number and logs unknown values. `fsverity_prepare_hash_state()` precomputes salted initial hash state by zero-padding the salt to the hash compression block size, allowing salted block hashing to run as efficiently as unsalted hashing. `fsverity_hash_block()` hashes one Merkle block using either the precomputed salted state or direct buffer hashing. `fsverity_hash_buffer()` hashes arbitrary descriptor/buffer data.

`fsverity_check_hash_algs()` sanity-checks the table at init: algorithm 0 must remain unused, digest sizes must fit fs-verity limits, digest and block sizes must be powers of two, and `HASH_ALGO_*` metadata must match.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/hash_algs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/init.c -->
# File Research: sources/os/linux/linux-stable/fs/verity/init.c

Initializes fs-verity global state and logging. `fsverity_msg()` is a rate-limited printk helper that includes filesystem id and inode number when available. The init path runs as a `late_initcall`, checking hash algorithm metadata, initializing the `fsverity_info` cache/rhashtable, creating the read verification workqueue, registering sysctl controls, initializing optional signature support, and registering optional BPF kfuncs.

When builtin signatures are configured, the sysctl table exposes `/proc/sys/fs/verity/require_signatures`, constrained to 0/1. Without sysctl support, initialization stubs out sysctl registration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/measure.c -->
# File Research: sources/os/linux/linux-stable/fs/verity/measure.c

Implements digest measurement APIs for fs-verity files. `fsverity_ioctl_measure()` serves `FS_IOC_MEASURE_VERITY`: it requires cached verity info, checks that the user buffer’s digest capacity is large enough, returns algorithm and digest size, then copies the enforced file digest to userspace.

`fsverity_get_digest()` is an exported in-kernel helper that copies the raw digest and optionally returns both fs-verity and generic `HASH_ALGO_*` algorithm identifiers. The comments emphasize that callers must use an algorithm id because raw digest bytes alone are not meaningful.

When BPF syscall support is enabled, the file registers the LSM-only kfunc `bpf_get_fsverity_digest()`, which writes a `struct fsverity_digest` plus digest bytes into a BPF dynptr and zero-fills extra output space. A filter rejects non-LSM program types to avoid recursion.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/measure.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/open.c -->
# File Research: sources/os/linux/linux-stable/fs/verity/open.c

Handles open-time loading and caching of fs-verity metadata. It maintains a global rhashtable keyed by inode pointer and a slab cache for `fsverity_info`.

`fsverity_init_merkle_tree_params()` validates algorithm and log block size, prepares salted hash state, computes hashes per block, number of tree levels, per-level starting blocks, tree size, and tree pages. It enforces block size constraints: power-of-two, 1 KiB minimum, no larger than page size or filesystem block size, and not too small for the digest.

`fsverity_create_info()` builds cached verification state from a descriptor, computes the file digest over the descriptor with signature omitted, verifies optional builtin signature, and allocates a verified-hash-block bitmap when Merkle block size differs from page size. `fsverity_get_descriptor()` asks the filesystem for descriptor size/content and validates version, reserved fields, salt size, data size, and signature bounds.

`__fsverity_file_open()` rejects write opens and ensures verity info is cached. `fsverity_cleanup_inode()` removes cached state at inode cleanup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/open.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/pagecache.c -->
# File Research: sources/os/linux/linux-stable/fs/verity/pagecache.c

Provides generic helpers for filesystems that store Merkle tree blocks in the inode pagecache. `generic_read_merkle_tree_page()` reads a folio at a filesystem-adjusted page index and returns the page corresponding to that index. `generic_readahead_merkle_tree()` starts readahead for Merkle tree pages if the target page is absent or not uptodate.

Both helpers require the filesystem to translate fs-verity’s Merkle-tree-relative index to the actual pagecache index where metadata is stored. Readahead asserts the mapping invalidate lock is held, matching the locking expectations used by fs-verity metadata reads.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/pagecache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/read_metadata.c -->
# File Research: sources/os/linux/linux-stable/fs/verity/read_metadata.c

Implements `FS_IOC_READ_VERITY_METADATA`. It supports reading three byte-stream metadata types from a verity file: Merkle tree, descriptor, and builtin signature.

`fsverity_read_merkle_tree()` bounds the requested range to the tree size, optionally triggers filesystem Merkle-tree readahead, then reads each Merkle tree page with `read_merkle_tree_page()`, maps it, and copies requested bytes to userspace. It handles signals and returns partial progress when available.

`fsverity_read_descriptor()` loads the descriptor, clears `sig_size`, and exposes only the fixed descriptor without the builtin signature. `fsverity_read_signature()` exposes just the builtin signature and returns `-ENODATA` if none exists. The ioctl validates reserved fields and offset overflow, clamps length to `INT_MAX`, and dispatches by metadata type.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/read_metadata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/signature.c -->
# File Research: sources/os/linux/linux-stable/fs/verity/signature.c

Implements optional fs-verity builtin signature verification. It maintains the root-owned `.fs-verity` keyring and the sysctl-backed `fsverity_require_signatures` flag.

`fsverity_verify_signature()` accepts unsigned files unless signatures are required. For signed files, it rejects verification if the keyring is empty to avoid exposing PKCS#7 parsing attack surface unnecessarily. It formats the fs-verity file digest with `"FSVerity"` magic, algorithm id, digest size, and digest bytes, then verifies the PKCS#7 signature against the keyring.

On success it calls `security_inode_setintegrity()` with `LSM_INT_FSVERITY_BUILTINSIG_VALID` so LSMs can consume the validated signature. `fsverity_init_signature()` allocates the keyring at boot and panics if allocation fails.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/signature.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/verify.c -->
# File Research: sources/os/linux/linux-stable/fs/verity/verify.c

Implements fs-verity read-time data verification. `fsverity_readahead()` walks Merkle tree levels for an upcoming data page range and asks the filesystem to readahead needed hash pages.

The core verifier is `verify_data_block()`. It hashes a data block, ascends the Merkle tree loading hash pages until it finds an already verified hash block or reaches the root, then descends and verifies each hash block against the expected digest before checking the data block digest. Verified hash blocks are cached using `PG_checked` when block size equals page size, or an in-memory bitmap plus `PG_checked` page freshness tracking when they differ. It also verifies fully past-EOF blocks are zeroed.

`fsverity_verify_blocks()` verifies aligned data in a locked, not-yet-uptodate folio. `fsverity_verify_bio()` does the same for completed read bios and marks `bi_status` on failure. The verification context can batch two SHA-256 blocks when optimized 2x hashing is available. The file also creates a high-priority per-CPU workqueue used by asynchronous verification work.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/verity/verify.c -->