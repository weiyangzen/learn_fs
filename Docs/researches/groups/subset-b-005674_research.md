# subset-b-005674 Research

Grouped source research for VFS inode/ioctl/init infrastructure, HPFS mount handling, hugetlbfs, and iomap buffered block I/O. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/super.c -->
# sources/distributed-fs/ceph-client/fs/hpfs/super.c

## Purpose

`sources/distributed-fs/ceph-client/fs/hpfs/super.c` implements HPFS filesystem registration, mount-context parsing, superblock validation, remount handling, dirty/clean shutdown marking, filesystem error policy, statfs, FITRIM ioctl support, and HPFS inode-cache allocation. It is the superblock and lifecycle entry point for the OS/2 HPFS driver, bridging Linux VFS `fs_context` and `super_operations` to HPFS on-disk boot/super/spare blocks.

## Important APIs, Types, and Functions

The VFS-facing objects are `hpfs_fs_type`, `hpfs_fc_context_ops`, and `hpfs_sops`. Entry points include `hpfs_init_fs_context()`, `hpfs_get_tree()`, `hpfs_fill_super()`, `hpfs_reconfigure()`, `hpfs_put_super()`, `hpfs_statfs()`, `hpfs_ioctl()`, module init/exit functions, and inode slab callbacks `hpfs_alloc_inode()` and `hpfs_free_inode()`.

Mount parsing uses `struct hpfs_fc_context`, `hpfs_param_spec`, and enum tables for `case=`, `check=`, `errors=`, `eas=`, and `chkdsk=`. Persistent-dirty helpers are `mark_dirty()` and `unmark_dirty()`. Error handling is centralized in exported `hpfs_error()`, while `hpfs_stop_cycles()` provides a lightweight cycle detector for other HPFS tree-walking code.

## Control Flow

Mount setup starts with `hpfs_init_fs_context()`, which allocates private context and installs defaults or, on reconfigure, copies current superblock options. `hpfs_parse_param()` fills that context. `hpfs_get_tree()` calls `get_tree_bdev()`, which invokes `hpfs_fill_super()` for block-device mounts.

`hpfs_fill_super()` allocates `struct hpfs_sb_info`, initializes the HPFS mutex, forces 512-byte blocks, maps sectors 0, 16, and 17, validates HPFS and spare-block magics, rejects unsupported writable versions, installs VFS superblock methods, imports HPFS geometry and mount options into `sbi`, loads hotfix, bitmap-directory, and codepage metadata, checks dirty shutdown and spare-dnode conditions, marks writable mounts dirty, validates directory-band geometry when checking is enabled, and finally reads the root inode with `iget_locked()`, `hpfs_init_inode()`, and `hpfs_read_inode()`. It then creates the root dentry and patches root inode timestamps and EA metadata from the root directory entry.

Remount uses `hpfs_reconfigure()`: it syncs the filesystem, rejects `timeshift` changes, clears prior dirty marking, updates option fields, and marks the volume dirty again for read-write operation. Unmount calls `hpfs_put_super()`, which unmarks dirty under the HPFS lock and frees `sbi` through RCU.

`hpfs_ioctl()` only handles `FITRIM`; it checks `CAP_SYS_ADMIN`, copies `struct fstrim_range`, converts byte ranges to 512-byte HPFS sectors, delegates to `hpfs_trim_fs()`, and returns the trimmed length in bytes.

## State and Persistence Behavior

Runtime state lives in `struct hpfs_sb_info`: geometry, bitmap directory, codepage table, free-space caches, dnode-map location, mount option values, error mode, time shift, and a prior-error flag. Free-sector and free-dnode counts are cached lazily by `hpfs_statfs()` and `hpfs_get_free_dnodes()` using bitmap scans.

Persistent state mutations are narrow but important. `mark_dirty()` writes sector 17 spare-block fields `dirty=1` and `old_wrote=0`; `unmark_dirty()` syncs the block device and writes clean or dirty-for-chkdsk state based on `chkdsk` policy and whether `hpfs_error()` was called. Writable mount setup also marks the spare block dirty. These writes are buffer-head based and synchronously flushed.

Error policy can change runtime mount state: `errors=panic` panics after marking dirty, `errors=remount-ro` sets `SB_RDONLY`, and `errors=continue` leaves a writable corrupted filesystem running while recording `sb_was_error`.

## Dependencies and Integration Points

The file depends on HPFS helpers declared in `hpfs_fn.h` for sector mapping, bitmap prefetch, bitmap-directory/codepage loading, hotfix maps, inode initialization, root fnode lookup, directory entry mapping, filesystem checks, and trimming. VFS integration is through block-device mounts, `fs_context`, `super_operations`, dentry operations, inode cache slabs, `statfs`, and Linux user-copy/capability helpers.

On-disk integration centers on HPFS boot, super, and spare blocks and little-endian conversions. Test and runtime observability is mostly through `pr_err()`, `pr_info()`, mount errors, dirty flags visible to OS/2 chkdsk, and statfs output.

## Risks and Edge Cases

Mount-time validation is safety-critical because HPFS structures are consumed by later inode and directory walkers. Disabling checks (`check=none`) reduces corruption defenses. Dirty shutdown handling, spare-dnode usage, and version rejection are tied to whether the mount is writable and to `errors=` behavior.

The bailout path must release mapped buffer heads in the right order and free `sbi` exactly once. `hpfs_put_super()` uses RCU freeing for `sbi`, so readers must access it through normal superblock lifetime rules. `timeshift` is intentionally immutable across remount because timestamps are interpreted through that offset.

`FITRIM` range conversion rounds by shifting to 512-byte sectors; boundary behavior depends on `hpfs_trim_fs()` interpreting `[start,end)` consistently. Error handling can set `SB_RDONLY` directly, so any path that assumes normal remount sequencing should be careful.

## Test Signals

Useful tests include mounting valid and invalid HPFS images, bad magic/version images, dirty-spare-block images, spare-dnode-used images, and images with inconsistent directory-band geometry under each `check=` and `errors=` mode. Remount tests should verify option persistence, readonly/readwrite transitions, and rejection of changed `timeshift`.

Operational signals include spare-block dirty/old_wrote transitions across mount/unmount/error, `statfs` free counts matching HPFS bitmaps, root inode timestamp import, FITRIM permission and range behavior, inode slab init/teardown under module load/unload, and absence of leaked buffer heads on mount failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hugetlbfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/hugetlbfs/Makefile

## Purpose

`sources/distributed-fs/ceph-client/fs/hugetlbfs/Makefile` wires the hugetlbfs implementation into the kernel build. When `CONFIG_HUGETLBFS` is enabled, it builds the `hugetlbfs.o` composite object from `inode.o`.

## Important APIs, Types, and Functions

The relevant build variables are `obj-$(CONFIG_HUGETLBFS)` and `hugetlbfs-objs`. There are no C APIs here; the Makefile determines whether `fs/hugetlbfs/inode.c` participates in the build and which object name is registered with the kernel build system.

## Control Flow

Kbuild evaluates `obj-$(CONFIG_HUGETLBFS) += hugetlbfs.o`. If the config symbol is built-in or modular, Kbuild links `hugetlbfs.o`; the composite object is resolved through `hugetlbfs-objs := inode.o`. If the symbol is disabled, no hugetlbfs code from this directory is compiled.

## State and Persistence Behavior

The file has no runtime state or persistent state. Its only effect is build-time inclusion of the hugetlbfs source.

## Dependencies and Integration Points

It depends on the global Kbuild infrastructure and the `CONFIG_HUGETLBFS` Kconfig symbol. The composite object name must remain aligned with filesystem registration in `inode.c`; otherwise the implementation will not be linked.

## Risks and Edge Cases

The risk surface is small. Adding more source files later requires updating `hugetlbfs-objs`; moving `inode.c` or renaming the composite object without matching Kbuild changes would silently break build coverage for hugetlbfs.

## Test Signals

Build signals are sufficient: verify `CONFIG_HUGETLBFS=y` links hugetlbfs into the kernel, `CONFIG_HUGETLBFS=m` produces a module if supported by surrounding config, and `CONFIG_HUGETLBFS=n` excludes it. A symbol or link failure in hugetlbfs init paths usually points back to this object list or missing config dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hugetlbfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hugetlbfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/hugetlbfs/inode.c

## Purpose

`sources/distributed-fs/ceph-client/fs/hugetlbfs/inode.c` implements the hugetlbfs pseudo-filesystem: a VFS filesystem whose regular-file data is backed by hugetlb folios and hugetlb reservation accounting rather than normal page-cache writeback. It provides mount parsing, superblock construction, inode allocation with optional inode limits, file creation, mmap preparation, read support, fallocate and hole punching, truncate/eviction, internal mounts for SysV/shared hugepage files, and filesystem registration.

## Important APIs, Types, and Functions

Important private state includes `struct hugetlbfs_fs_context` for parsed mount options, `struct hugetlbfs_sb_info` from hugetlb headers for superblock limits and subpool state, and `struct hugetlbfs_inode_info` for per-inode reservation maps and seals. Mount options include `uid=`, `gid=`, `mode=`, `size=`, `min_size=`, `nr_inodes=`, and `pagesize=`.

Core VFS objects are `hugetlbfs_fs_type`, `hugetlbfs_ops`, `hugetlbfs_file_operations`, `hugetlbfs_dir_inode_operations`, `hugetlbfs_inode_operations`, and `hugetlbfs_aops`. Key functions include `hugetlbfs_init_fs_context()`, `hugetlbfs_parse_param()`, `hugetlbfs_validate()`, `hugetlbfs_fill_super()`, `hugetlbfs_get_tree()`, `hugetlbfs_get_inode()`, `hugetlbfs_read_iter()`, `hugetlbfs_file_mmap_prepare()`, `hugetlb_get_unmapped_area()`, `hugetlbfs_fallocate()`, `hugetlbfs_punch_hole()`, `hugetlb_vmtruncate()`, `remove_inode_hugepages()`, `hugetlbfs_evict_inode()`, `hugetlb_file_setup()`, `mount_one_hugetlbfs()`, and `init_hugetlbfs_fs()`.

## Control Flow

Mounting starts by allocating `struct hugetlbfs_fs_context` with defaults for current fsuid/fsgid, mode `0755`, unlimited size/inodes, default hstate, and no minimum pool size. Parse callbacks convert size strings or percentages to pending options and map `pagesize=` to an hstate. `hugetlbfs_get_tree()` validates min/max hugepage counts and calls `get_tree_nodev()`. `hugetlbfs_fill_super()` allocates `sbinfo`, initializes inode counters and optional `hugepage_subpool`, fills VFS superblock fields, sets `DCACHE_DONTCACHE`, creates a root directory inode, and installs it as the root dentry.

File and directory creation flow through `hugetlbfs_get_inode()`, which allocates a reserve map for regular files and symlinks, initializes owner/mode through idmapped mount helpers, assigns address-space operations, sets initial seals, and selects file, directory, symlink, or special inode operations. Directory operations are mostly simplefs operations with hugetlbfs-specific create, mkdir, mknod, symlink, tmpfile, and setattr hooks.

`hugetlbfs_file_mmap_prepare()` validates hugepage-aligned offsets and overflow, reserves pages over the requested hstate range, grows `i_size` for writable mappings, installs hugetlb VM operations, and arranges delayed VMA-lock allocation so rmap cannot observe the VMA before its hugetlb lock exists. `hugetlb_get_unmapped_area()` aligns non-fixed address hints and rejects unaligned length or fixed address.

Read support walks hugepage indexes from `ki_pos`, returns zeroes for holes, copies present huge folios to the iterator, and treats raw-hwpoison subpages as short readable ranges or `-EIO`. There is no normal buffered write path; `write_begin` rejects and `write_end` is a BUG fallback.

Truncate, hole punch, and eviction remove huge folios from page cache and reservations. `hugetlb_vmtruncate()` shrinks `i_size`, unmaps VMAs, and removes pages after the new EOF. `hugetlbfs_punch_hole()` zeroes partial hugepages at the edges, unmaps and removes fully covered hugepages, and checks write seals. `hugetlbfs_fallocate()` either delegates to punch-hole or preallocates huge folios one hstate index at a time through a pseudo VMA, reservation-aware allocation, zeroing, and page-cache insertion.

Boot-time initialization creates the inode slab, registers hugetlbfs, mounts an internal hugetlbfs instance for the default hstate, and best-effort mounts internal instances for other hstates. `hugetlb_file_setup()` uses those internal mounts to create pseudo regular files for shared hugetlb mappings after checking hstate availability and SHM_HUGETLB privilege.

## State and Persistence Behavior

hugetlbfs has no disk persistence. File contents and metadata exist in memory, backed by hugetlb folios and reservation/subpool accounting. Superblock state records hstate, uid/gid/mode, inode counters, and optional subpool with maximum/minimum hugepage limits. Inode state records reserve maps, file seals, `i_size`, ownership, mode, timestamps, and mapping state.

Persistent-looking operations are runtime accounting updates: reserving pages during mmap or `hugetlb_file_setup()`, consuming reservations during fallocate, removing page-cache folios, unreserving pages during truncate/hole punch/eviction, and adjusting subpool/free-inode counters. Eviction releases the reserve map for regular and symlink inodes and clears the inode.

The file also stores global state: `sysctl_hugetlb_shm_group`, the hugetlbfs inode kmem cache, and `hugetlbfs_vfsmount[]` for each hstate internal mount.

## Dependencies and Integration Points

This file is tightly integrated with the hugetlb MM subsystem: hstates, reservation maps, hugepage subpools, hugetlb fault mutexes, VMA locks, huge PTE walking, hugepage allocation, migration, and hugetlb tracepoints. It uses VFS fs-context, nodev mounts, idmapped mounts, simple directory operations, page symlink support, inode attributes, `statfs`, Linux security/capability helpers, `user_shm_lock()`, and internal long-term kernel mounts.

The mmap path integrates with `vm_area_desc`, `hugetlb_vm_ops`, rmap visibility, and per-VMA hugetlb locks. Internal shared memory users enter through exported `hugetlb_file_setup()`.

## Risks and Edge Cases

Reservation accounting is the highest-risk area. Truncation and hole punching must coordinate page-cache deletion, VMA unmapping, hugetlb fault mutexes, reserve-map updates, and subpool/global counts; the code explicitly handles races with faults by rechecking mapped folios and using hugetlb fault locks. OOM during unreserve can require reserve-count repair.

Alignment and overflow checks are critical because offsets are translated between base-page units, hugepage units, and byte offsets. `PGOFF_LOFFT_MAX`, hugepage-mask tests, and `len < vma_len` checks prevent signed `loff_t` overflow. Fallocate loops can be interrupted and must release fault mutexes and folio references on every exit.

Seals are enforced for shrink, grow, write, and future-write cases in setattr and punch-hole paths. The code deliberately sets high stack depth because hugetlbfs is unsuitable as a stacking filesystem. Internal hstate mounts are required for `hugetlb_file_setup()`; missing non-default hstates return `-ENOENT`.

## Test Signals

Coverage should include mounting with byte and percentage `size=`/`min_size=`, invalid `pagesize=`, min greater than max, inode-limit exhaustion, idmapped create ownership, root mode/uid/gid display in `/proc/mounts`, statfs subpool accounting, read holes returning zeroes, hwpoison read failures, aligned and unaligned mmap offsets, MAP_FIXED alignment rejection, writable mmap size growth, truncate alignment rejection, seals blocking grow/shrink/punch, fallocate preallocation and interrupt behavior, hole punching edge partial-zeroing, eviction unreserving all pages, and SysV SHM_HUGETLB privilege checks.

Useful runtime signals include hugetlbfs tracepoints for allocation, free, eviction, fallocate, and setattr, plus global/subpool hugepage counters before and after mmap, fallocate, truncate, and unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hugetlbfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/init.c -->
# sources/distributed-fs/ceph-client/fs/init.c

## Purpose

`sources/distributed-fs/ceph-client/fs/init.c` provides early-init, kernel-internal wrappers that mimic selected filesystem syscalls without using userspace pointers or already-open file descriptors. It is intended for `init/` and related boot code that needs to mount roots, create device nodes, change directories, set permissions, and duplicate files before normal userspace execution.

## Important APIs, Types, and Functions

The exported init helpers are `init_pivot_root()`, `init_mount()`, `init_umount()`, `init_chdir()`, `init_chroot()`, `init_chown()`, `init_chmod()`, `init_eaccess()`, `init_stat()`, `init_mknod()`, `init_link()`, `init_symlink()`, `init_unlink()`, `init_mkdir()`, `init_rmdir()`, `init_utimes()`, and `init_dup()`.

They use VFS helpers such as `kern_path()`, `path_mount()`, `path_umount()`, `path_pivot_root()`, `path_permission()`, `set_fs_pwd()`, `set_fs_root()`, `chown_common()`, `chmod_common()`, `vfs_getattr()`, `vfs_utimes()`, `get_unused_fd_flags()`, and `fd_install()`. Filename-taking operations use `CLASS(filename_kernel, ...)` wrappers to build kernel filename objects for lower-level `filename_*` helpers declared in `fs/internal.h`.

## Control Flow

Path-based operations first resolve a kernel string with `kern_path()` and appropriate lookup flags. `init_pivot_root()` resolves both new root and put-old directories and calls `path_pivot_root()`. `init_mount()` resolves the target and calls `path_mount()`. `init_umount()` resolves a mountpoint, optionally following symlinks unless `UMOUNT_NOFOLLOW` is set, and calls `path_umount()`.

Directory-context helpers resolve a directory and check execute/chdir permission before updating `current->fs`. `init_chroot()` additionally checks `CAP_SYS_CHROOT` in the current user namespace and calls `security_path_chroot()` before `set_fs_root()`.

Metadata changes resolve the target, acquire write access when needed, and call common VFS helpers. Object-creation and link/unlink operations wrap kernel string names in filename objects and delegate to the same `filename_*` implementations used by syscall paths. `init_dup()` obtains an unused fd and installs a reference to an existing file.

## State and Persistence Behavior

The helpers mutate normal VFS state on behalf of early kernel code: mount namespace state, the current task's root and cwd, inode ownership/mode/timestamps, directory entries, special files, hardlinks, symlinks, and fd tables. Persistence depends entirely on the backing filesystem and mount. The wrappers themselves hold no persistent state.

Resource cleanup is path-based: most functions `path_put()` resolved paths before returning, while scoped `CLASS(filename_kernel, ...)` objects manage filename lifetimes automatically.

## Dependencies and Integration Points

The file integrates early boot code with the normal VFS implementation while avoiding userspace address handling. It depends on mount/namei/open/stat/xattr internals exposed through `fs/internal.h`, LSM hooks for chroot, namespace capability checks, and the current task's `fs_struct` and file descriptor table.

Because many helpers are `__init`, they are intended to be discarded after boot; callers should not rely on them after init memory is freed.

## Risks and Edge Cases

These wrappers intentionally bypass syscall user-copy plumbing, so they must pass kernel filename wrappers to helpers that expect `struct filename` and must not pass raw kernel pointers into user-pointer syscall entry points. Lookup flags are security-sensitive: `AT_SYMLINK_NOFOLLOW` and `UMOUNT_NOFOLLOW` must be preserved exactly.

`init_chroot()` must keep capability and LSM checks aligned with normal chroot semantics. `init_chown()` needs `mnt_want_write()`/`mnt_drop_write()` pairing. `init_dup()` returns `0` after installing the fd rather than the fd number, matching the local init syscall contract but differing from `dup(2)` semantics; callers must understand that interface.

## Test Signals

Boot tests should verify initramfs/rootfs scripts using these helpers can mount, pivot root, chdir/chroot, create nodes/directories/links, set ownership/mode/timestamps, and unmount. Negative tests include missing paths, non-directories for chdir/chroot/pivot, permission failures, no `CAP_SYS_CHROOT`, readonly mounts for chown/chmod-like mutations, no free fds for `init_dup()`, and symlink-follow flag behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/inode.c -->
# sources/distributed-fs/ceph-client/fs/inode.c

## Purpose

`sources/distributed-fs/ceph-client/fs/inode.c` is the VFS inode cache and inode lifecycle implementation. It allocates and initializes inodes, maintains global inode hash and per-superblock inode/LRU lists, implements lookup and insertion APIs, handles final `iput()` and eviction, exports link-count and ownership helpers, supports timestamp updates including multigrain timestamps, provides write-path privilege and time updates, initializes inode caches/hash tables, and supplies diagnostic helpers.

## Important APIs, Types, and Functions

Core exported lifecycle APIs include `inode_init_always_gfp()`, `alloc_inode()`, `new_inode()`, `inode_init_once()`, `address_space_init_once()`, `__destroy_inode()`, `clear_inode()`, `evict_inodes()`, `prune_icache_sb()`, `ihold()`, `iput()`, `iput_not_last()`, `unlock_new_inode()`, and `discard_new_inode()`.

Lookup and hash APIs include `__insert_inode_hash()`, `__remove_inode_hash()`, `inode_insert5()`, `iget5_locked()`, `iget5_locked_rcu()`, `iget_locked()`, `ilookup5_nowait()`, `ilookup5()`, `ilookup()`, `find_inode_nowait()`, `find_inode_rcu()`, `find_inode_by_ino_rcu()`, `insert_inode_locked()`, `insert_inode_locked4()`, `iunique()`, and `get_next_ino()`.

Metadata helpers include `drop_nlink()`, `clear_nlink()`, `set_nlink()`, `inc_nlink()`, `init_special_inode()`, `inode_init_owner()`, `inode_owner_or_capable()`, `in_group_or_capable()`, `mode_strip_sgid()`, `inode_set_flags()`, `inode_nohighmem()`, `inode_needs_sync()`, `bmap()`, `inode_dio_wait()`, and `inode_dio_wait_interruptible()`.

Time and write-path helpers include `current_time()`, `timestamp_truncate()`, `inode_set_ctime_to_ts()`, `inode_set_ctime_current()`, `inode_set_ctime_deleg()`, `inode_update_time()`, `generic_update_time()`, `atime_needs_update()`, `touch_atime()`, `dentry_needs_remove_privs()`, `file_remove_privs()`, `file_update_time()`, `file_modified()`, and `kiocb_modified()`.

Global state includes `inode_hashtable`, `inode_hash_lock`, per-cpu `nr_inodes` and `nr_unused`, the inode slab cache, multigrain timestamp debug counters, and inode sysctl state.

## Control Flow

Inode allocation flows through filesystem-specific `s_op->alloc_inode()` or the generic slab, then `inode_init_always_gfp()` initializes the inode, address_space, locks, counters, uid/gid/mode defaults, xattr/mgtime opflags, security blob, and writeback-related fields. `new_inode()` additionally links the inode onto the superblock inode list.

Cache lookup uses a global hash derived from superblock and inode/hash value. `iget_locked()` and `iget5_locked()` look for a matching inode under RCU and spinlocks, wait for `I_NEW` to clear when necessary, retry if an inode was unhashed during the race, or allocate/insert a new `I_NEW` inode for the filesystem to fill. `insert_inode_locked()` handles callers that already own an initialized inode and returns `-EBUSY` if a live duplicate exists.

Reference release runs through `iput()`. If the count does not reach zero it returns quickly. On the final put, it syncs lazytime when needed, calls filesystem `drop_inode()` or the generic drop policy, either queues the inode on the superblock LRU for reuse or marks it `I_WILL_FREE`/`I_FREEING`, waits for writeback, calls filesystem `evict_inode()` or truncates pages and clears the inode, removes hash/list state, wakes waiters, and frees the inode through RCU and filesystem slab callbacks.

Shrinking and unmount flow through `prune_icache_sb()` and `evict_inodes()`. The LRU isolate path skips referenced or unreclaimable inodes, may invalidate page cache for shrinkable mappings, marks selected inodes `I_FREEING`, and disposes them outside the LRU lock. Unmount removes all zero-reference inodes after `SB_ACTIVE` is cleared.

Write-path metadata flow starts with `file_modified()` or `kiocb_modified()`, which remove suid/sgid/security privileges if needed and then update ctime/mtime/i_version through filesystem `update_time` or `generic_update_time()`. Atime flow is separate: `touch_atime()` checks noatime/nodiratime/relatime, readonly/write access, unmapped IDs, and then updates atime best-effort.

## State and Persistence Behavior

The file maintains in-memory VFS inode state and schedules persistence indirectly by dirtying inodes. It does not write filesystem-specific on-disk metadata itself except through generic dirtying, writeback waits, and filesystem callbacks.

Important state transitions are encoded in `i_state`: `I_NEW`, `I_CREATING`, dirty flags, `I_SYNC`, `I_REFERENCED`, `I_LRU_ISOLATING`, `I_WILL_FREE`, `I_FREEING`, and `I_CLEAR`. List membership spans the global hash, per-superblock inode list, per-superblock LRU, and writeback lists. Counters track total and unused inodes per CPU and removal counts per superblock when link count reaches zero.

Timestamps are stored in inode fields and truncated to superblock granularity. Multigrain timestamp mode uses `I_CTIME_QUERIED` in `i_ctime_nsec`, coarse/fine clock selection, compare-exchange updates, and debug counters to provide finer ctime when timestamp values have been observed.

## Dependencies and Integration Points

This file is central to VFS, MM, writeback, fsnotify, security, fsverity, POSIX ACLs, device nodes, block mapping, mount idmaps, cgroups writeback, debugfs, sysctl, and tracepoints. Filesystems depend on these exported helpers to allocate, publish, lookup, lock, evict, and dirty their inodes.

It also integrates with reclaim via `list_lru`, with direct I/O via `i_dio_count`, with writeback via inode writeback lists and `inode_wait_for_writeback()`, with LSM via `security_inode_alloc/free()` and privilege removal hooks, and with idmapped mounts for ownership and permission helpers.

## Risks and Edge Cases

Lock ordering is the main correctness risk. The file documents ordering among `s_inode_list_lock`, `i_lock`, inode LRU locks, writeback locks, `inode_hash_lock`, and `iunique_lock`. Lookup paths must not return inodes being freed, must wait without deadlocking when `I_FREEING` races are observed, and must not sleep in callbacks that run under `inode_hash_lock`.

Final `iput()` is sensitive because filesystem `drop_inode()`, lazytime sync, writeback wait, page-cache truncation, hash removal, wakeups, and RCU freeing all interleave with concurrent lookup and reclaim. Link-count helpers update `s_remove_count`; direct manipulation of `i_nlink` by filesystems can break unmount accounting.

Timestamp paths must handle NOWAIT semantics, lazytime, i_version increments, time granularity clamping, idmapped/mapped-ID checks, and multigrain races. Write-path privilege removal can block and therefore returns `-EAGAIN` for NOWAIT callers.

## Test Signals

Useful coverage includes iget/ilookup races with concurrent eviction, duplicate insertion returning `-EBUSY`, `I_NEW` wait/wakeup behavior, final `iput()` under dirty/lazytime inodes, superblock unmount eviction, LRU shrinker behavior with page-cache-backed inodes, RCU lookup helpers, inode hash sizing via `ihash_entries=`, link-count remove-count accounting, special inode initialization for char/block/FIFO/socket, idmapped ownership initialization, suid/sgid/capability stripping on write, NOWAIT timestamp update failures, multigrain timestamp monotonicity, and direct-I/O wait behavior.

Runtime signals include `/proc/sys/fs/inode-nr`, `/proc/sys/fs/inode-state`, debugfs `multigrain_timestamps`, VFS warnings from `dump_inode()`/`dump_mapping()`, writeback tracepoints, and lockdep reports for inode lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/internal.h -->
# sources/distributed-fs/ceph-client/fs/internal.h

## Purpose

`sources/distributed-fs/ceph-client/fs/internal.h` is the private cross-file header for VFS implementation code under `fs/`. It declares internal helpers that are shared among VFS source files but are not public kernel APIs, and it defines small internal structures and inline helpers for mount, file, inode, namespace, xattr, attr, and path handling.

## Important APIs, Types, and Functions

The header declares initialization hooks such as `bdev_cache_init()`, `chrdev_init()`, `filename_init()`, and `mnt_init()`. Namei and namespace internals include `filename_lookup()`, `filename_mkdirat()`, `filename_mknodat()`, `filename_symlinkat()`, `filename_linkat()`, `filename_unlinkat()`, `filename_rmdir()`, `filename_renameat2()`, `path_mount()`, `path_umount()`, `path_pivot_root()`, `lookup_mnt()`, `finish_automount()`, `may_mount()`, and remount helpers.

File and open internals include `alloc_empty_file*()`, `do_file_open()`, `do_file_open_root()`, `build_open_how()`, `build_open_flags()`, `file_close_fd_locked()`, `do_ftruncate()`, `chmod_common()`, `chown_common()`, `fput_close*()`, and inline helpers `file_put_write_access()` and `put_file_access()`.

Inode, dcache, pipe, namespace, stat, splice, xattr, ACL, attr, and anon-inode declarations cover `prune_icache_sb()`, `dentry_needs_remove_privs()`, `in_group_or_capable()`, `prune_dcache_sb()`, `shrink_dcache_for_umount()`, `pipefifo_fops`, `open_namespace_file()`, `do_statx*()`, `splice_file_to_pipe()`, `kernel_xattr_ctx`, xattr copy/set/get helpers, ACL helpers, `alloc_mnt_idmap()`, stashed dentry helpers, `path_mounted()`, file-owner release, statmount idmap reporting, and namespace root getters.

## Control Flow

This header has no runtime control flow by itself. It enables control flow between VFS implementation files by exposing internal functions that would otherwise require public declarations. Several inline helpers do encode behavior: `file_put_write_access()` releases inode and mount write references, including backing-file user mount references; `put_file_access()` releases read or writer accounting based on file mode; `sb_start_ro_state_change()` and `sb_end_ro_state_change()` provide memory-barrier ordering for superblock read-only transitions; `path_mounted()` checks whether a path is a mount root.

## State and Persistence Behavior

The header owns no storage. It describes and coordinates state owned by other VFS components: mount write counts, superblock readonly-transition flags, inode cache and dcache shrink state, file descriptor tables, xattr copy buffers, idmapped mount references, stashed dentries, and namespace roots.

The readonly-transition helpers are stateful in callers because they write `sb->s_readonly_remount` with memory barriers so mount readers observe either a pending transition or completed flag changes consistently.

## Dependencies and Integration Points

`internal.h` is a dense integration point across VFS compilation units. It depends on core kernel types such as `struct super_block`, `struct file`, `struct path`, `struct mount`, `struct fs_context`, `struct inode`, `struct dentry`, `struct seq_file`, `struct iov_iter`, `struct mnt_idmap`, and `struct ns_common`.

It is used by files such as `fs/init.c`, `fs/inode.c`, `fs/ioctl.c`, open/namei/namespace/stat/xattr/attr implementations, and filesystem helpers that need private VFS contracts. The block-device init declaration is compiled away to an inline no-op when `CONFIG_BLOCK` is disabled.

## Risks and Edge Cases

Because this is an internal header, changes have broad blast radius but limited external ABI review. Function signatures must stay synchronized with implementation files. Inline reference-release helpers are particularly sensitive: mismatched `put_write_access()` and mount write accounting can leak or prematurely drop write permissions, especially for backing files.

The readonly-transition barriers are subtle; weakening them can let `mnt_is_readonly()` observers see inconsistent superblock flag state. Xattr and ACL helpers carry user-pointer and kernel-buffer contracts that must remain clear to avoid user-copy bugs.

## Test Signals

Test signals are indirect. Full VFS build coverage across `CONFIG_BLOCK`, `CONFIG_FS_POSIX_ACL`, namespace, xattr, statmount, and backing-file configurations catches missing declarations. Runtime coverage should exercise mount/remount readonly transitions, file open/close accounting, early init wrappers, xattr get/set paths, ACL enabled and disabled builds, namespace file opens, dcache/inode shrinkers, and backing-file write-access release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ioctl.c -->
# sources/distributed-fs/ceph-client/fs/ioctl.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ioctl.c` implements the generic VFS `ioctl(2)` syscall dispatcher and common file ioctls that are shared across filesystems. It handles close-on-exec toggles, nonblocking and async flags, block mapping, fiemap, legacy preallocation ioctls, freeze/thaw, clone/dedupe, size queries, file attribute ioctls, filesystem UUID/sysfs path reporting, and compat ioctl translation.

## Important APIs, Types, and Functions

The syscall entry points are `SYSCALL_DEFINE3(ioctl)` and, under `CONFIG_COMPAT`, `COMPAT_SYSCALL_DEFINE3(ioctl)`. The generic fallback to filesystem-specific handlers is `vfs_ioctl()`. The core dispatcher is `do_vfs_ioctl()`.

Shared helper APIs include exported `fiemap_fill_next_extent()`, exported `fiemap_prep()`, and exported `compat_ptr_ioctl()`. Important local helpers are `ioctl_fibmap()`, `ioctl_fiemap()`, `ioctl_file_clone()`, `ioctl_file_clone_range()`, `ioctl_preallocate()`, `file_ioctl()`, `ioctl_fionbio()`, `ioctl_fioasync()`, `ioctl_fsfreeze()`, `ioctl_fsthaw()`, `ioctl_file_dedupe_range()`, `ioctl_getfsuuid()`, and `ioctl_get_fs_sysfs_path()`.

## Control Flow

Native `ioctl(2)` obtains the fd through the scoped fd helper, rejects bad fds, runs `security_file_ioctl()`, calls `do_vfs_ioctl()`, and if the command is not one of the generic VFS commands, falls back to `vfs_ioctl()` which calls `file_operations->unlocked_ioctl()` and translates `-ENOIOCTLCMD` to `-ENOTTY`.

`do_vfs_ioctl()` switches on command numbers. Simple commands update close-on-exec or file flags. `FIOQSIZE`, `FIONREAD`, and `FIGETBSZ` return sizes for supported object types. Freeze/thaw check `CAP_SYS_ADMIN` in the superblock user namespace and delegate to superblock freeze/thaw operations. Clone and dedupe copy user argument structures and call VFS range helpers. Attribute ioctls delegate to fileattr helpers. Regular-file-only legacy preallocation commands flow through `file_ioctl()`.

FIEMAP copies the user header, bounds extent count against `FIEMAP_MAX_EXTENTS`, initializes `struct fiemap_extent_info`, calls the inode's `->fiemap`, and copies back flags and mapped extent count. Filesystem `->fiemap` implementations call `fiemap_prep()` and `fiemap_fill_next_extent()` to validate flags, optionally sync dirty pages, and copy extent records to the user array.

Compat ioctl handling runs `security_file_ioctl_compat()`, special-cases integer `FICLONE`, x86_64 legacy preallocation structure alignment, and 32-bit flag command numbers, then reuses `do_vfs_ioctl()` with `compat_ptr()` for compatible pointer commands or falls back to filesystem `compat_ioctl`.

## State and Persistence Behavior

Most operations mutate file descriptor or filesystem state indirectly. `FIOCLEX`/`FIONCLEX` update fd table close-on-exec state. `FIONBIO` changes `file->f_flags` under `f_lock`; `FIOASYNC` delegates to `fasync()` and may alter async notification state. Preallocation, punch-hole, zero-range, clone, and dedupe can change file extents through VFS filesystem methods. Freeze/thaw changes superblock freeze state. Fileattr ioctls can update inode flags or project IDs through helpers in other files.

FIEMAP and FIBMAP report mapping state without changing layout, except `FIEMAP_FLAG_SYNC` can write and wait dirty pages. UUID and sysfs-path ioctls expose superblock fields only when populated.

## Dependencies and Integration Points

The file integrates syscall/fd handling, LSM ioctl hooks, file operations, inode operations, VFS clone/dedupe/fallocate, superblock freeze/thaw, buffer-head `bmap`, writeback sync, fscrypt/fileattr helpers, user-copy helpers, compat ABI, and architecture ioctl definitions.

Filesystem integration occurs through `file_operations->unlocked_ioctl`, `file_operations->compat_ioctl`, `inode_operations->fiemap`, superblock operations, and the common fileattr helpers included from `<linux/fileattr.h>`.

## Risks and Edge Cases

User ABI compatibility is the primary risk. Commands that pass integers must not be fed through `compat_ptr()`, and x86_64 legacy preallocation structures require special alignment handling. New generic ioctls must preserve compat semantics and go through LSM review because security modules may care about command behavior.

FIEMAP must avoid extent-count overflow on 32-bit systems and must propagate unsupported flags back through `fi_flags` with `-EBADR`. FIBMAP is privileged and warns if a block number would truncate into an `int`. Freeze/thaw permission checks depend on the superblock user namespace.

Size-reporting commands deliberately reject anonymous regular files in some cases. `ioctl_file_dedupe_range()` limits the copied request to one page. Clone must report an error if a length-limited clone completes only partially.

## Test Signals

Tests should cover native and compat ioctls for `FIONBIO`, `FIOASYNC`, `FIONREAD`, `FIOQSIZE`, `FIGETBSZ`, `FIBMAP` permission failure and success, FIEMAP count-only and bounded arrays, unsupported FIEMAP flags, freeze/thaw permission and unsupported filesystems, clone and clone-range partial behavior, dedupe range copyback, legacy preallocation whence handling, x86_64 compat preallocation structures, fileattr get/set, UUID/sysfs path absent and present cases, and fallback to filesystem-specific ioctl returning `-ENOTTY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/Makefile -->
# sources/distributed-fs/ceph-client/fs/iomap/Makefile

## Purpose

`sources/distributed-fs/ceph-client/fs/iomap/Makefile` defines the build composition of the generic iomap library. It builds the `iomap.o` composite object when `CONFIG_FS_IOMAP` is enabled and conditionally includes block and swap support pieces.

## Important APIs, Types, and Functions

The build variables are `ccflags-y`, `obj-$(CONFIG_FS_IOMAP)`, `iomap-y`, `iomap-$(CONFIG_BLOCK)`, and `iomap-$(CONFIG_SWAP)`. Core objects are `trace.o`, `iter.o`, and `buffered-io.o`; block-enabled objects are `direct-io.o`, `ioend.o`, `fiemap.o`, `seek.o`, and `bio.o`; swap support adds `swapfile.o`.

## Control Flow

Kbuild adds `-I $(src)` so trace event headers in the iomap directory can be included. If `CONFIG_FS_IOMAP` is enabled, Kbuild links `iomap.o`. The base object list always includes tracing, iteration, and buffered I/O. Extra objects are included only when their configuration symbols are enabled.

## State and Persistence Behavior

The file has no runtime state. Its build-time state determines which iomap capabilities are present in the resulting kernel.

## Dependencies and Integration Points

It integrates the iomap library with kernel configuration. Filesystems that use iomap depend on this object composition for exported buffered write/read helpers, iterator support, tracepoints, direct I/O, fiemap/seek, bio read support, and swapfile helpers.

## Risks and Edge Cases

Misplacing an object in the wrong conditional can create link failures or missing exported symbols. `buffered-io.o` is part of the base iomap library, while `bio.o` is gated by `CONFIG_BLOCK`; callers must only use block-backed bio read ops when block support exists. Trace include paths must remain correct for generated trace headers.

## Test Signals

Build matrices should cover `CONFIG_FS_IOMAP=y/m/n`, `CONFIG_BLOCK=y/n` where applicable, and `CONFIG_SWAP=y/n`. Link failures in iomap exports or missing trace definitions are the main regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/bio.c -->
# sources/distributed-fs/ceph-client/fs/iomap/bio.c

## Purpose

`sources/distributed-fs/ceph-client/fs/iomap/bio.c` implements the block-backed read backend for iomap buffered I/O. It batches folio read ranges into bios, submits them, completes folio read state on bio completion, handles integrity payload allocation/verification plumbing, and provides a synchronous single-folio-range read helper for write-begin read-around.

## Important APIs, Types, and Functions

Exported symbols are `iomap_bio_read_folio_range()`, `iomap_bio_read_ops`, and `iomap_bio_read_folio_range_sync()`. Internal helpers include `__iomap_read_end_io()`, `iomap_read_end_io()`, `iomap_fail_buffered_read()`, `iomap_fail_reads()`, `iomap_bio_submit_read()`, `iomap_read_bio_set()`, and `iomap_read_alloc_bio()`.

Important state includes the global `failed_read_list`, `failed_read_lock`, and `failed_read_work`, plus per-read `struct iomap_read_folio_ctx` fields `read_ctx`, `read_ctx_file_offset`, `cur_folio`, `ops`, and optional `rac`.

## Control Flow

As buffered iomap reads encounter mapped extents, `iomap_bio_read_folio_range()` tries to append the current folio range to the existing bio when sectors are contiguous, the iomap maximum bio size has room, and `bio_add_folio()` succeeds. Otherwise it submits the existing bio through `ctx->ops->submit_read()` and allocates a new bio sized for the remaining iomap range, with a single-page fallback allocation to avoid partial-page read handling. It sets readahead flags when applicable, initializes sector and end_io, and adds the current folio range.

Submission is through `iomap_bio_submit_read()`, which allocates integrity metadata when `IOMAP_F_INTEGRITY` is set and calls `submit_bio()`. Completion enters `iomap_read_end_io()`. Successful bios call `__iomap_read_end_io()` immediately, which walks all folio segments and calls `iomap_finish_folio_read()` with success, frees integrity metadata, and drops the bio. Failed bios are queued to `failed_read_list` and processed by `iomap_fail_reads()` workqueue context to avoid nested inode-lock acquisition in filesystem error reporting.

`iomap_bio_read_folio_range_sync()` builds an on-stack one-vector bio, submits it synchronously with `submit_bio_wait()`, optionally verifies integrity data, frees integrity metadata, and returns the block-layer error.

## State and Persistence Behavior

The file does not persist filesystem metadata. It drives reads from block devices into page-cache folios and updates folio read/uptodate/error state through `iomap_finish_folio_read()`. Integrity metadata is attached per bio and freed on completion. Failed read bios temporarily live on a global bio list until the workqueue finishes them.

## Dependencies and Integration Points

It depends on the iomap iterator contract, `struct iomap_read_ops`, block-layer bio allocation/submission, `fs_bio_set` or filesystem-provided biosets, bio integrity helpers, page-cache folios, and the buffered-io completion function from `buffered-io.c`. Filesystems using iomap can install `iomap_bio_read_ops` as their read ops for block-backed buffered reads.

## Risks and Edge Cases

The error path intentionally defers completion to process context; changing that can reintroduce nested `i_lock` or filesystem-error-reporting deadlocks. Bio allocation has a nofail folio-add path after allocation and a single-page fallback, but callers still depend on valid `ctx->ops->submit_read()` and coherent iomap sector ranges.

Integrity payload allocation must match freeing and synchronous verification must only run when the submit succeeded. Readahead paths use reduced GFP flags and mark bios `REQ_RAHEAD`; allocation failure handling must avoid leaving the current folio locked forever.

## Test Signals

Useful tests include sequential buffered reads merging into larger bios, non-contiguous extents forcing submission, iomap max-bio-size boundaries, readahead bio flags, allocation fallback to one vector under fault injection, block read errors completing folios through workqueue context, integrity-enabled reads allocating/freeing payloads, synchronous read-around success and integrity verification failure, and no folio read completion leaks under short or failed bios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/bio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/buffered-io.c -->
# sources/distributed-fs/ceph-client/fs/iomap/buffered-io.c

## Purpose

`sources/distributed-fs/ceph-client/fs/iomap/buffered-io.c` implements the generic iomap buffered page-cache path: folio read and readahead, per-block uptodate/dirty tracking for large folios, buffered writes, inline-data handling, delalloc reservation cleanup after short writes, unshare, zero/truncate-page helpers, page-mkwrite, and writeback over iomap mappings. It is a central library used by filesystems such as XFS and others that describe file layout through iomap iterators.

## Important APIs, Types, and Functions

The local `struct iomap_folio_state` tracks per-folio block uptodate bits, dirty bits, pending read bytes, and pending writeback bytes. Exported read helpers include `iomap_finish_folio_read()`, `iomap_read_folio()`, `iomap_readahead()`, and `iomap_is_partially_uptodate()`. Folio lifecycle helpers include `iomap_get_folio()`, `iomap_release_folio()`, `iomap_invalidate_folio()`, and `iomap_dirty_folio()`.

Exported write and maintenance helpers include `iomap_file_buffered_write()`, `iomap_write_delalloc_release()`, `iomap_file_unshare()`, `iomap_fill_dirty_folios()`, `iomap_zero_range()`, `iomap_truncate_page()`, `iomap_page_mkwrite()`, `iomap_finish_folio_write()`, `iomap_writeback_folio()`, and `iomap_writepages()`.

Important internal flows are `ifs_alloc()/ifs_free()`, `iomap_adjust_read_range()`, `iomap_read_inline_data()`, `iomap_read_folio_iter()`, `iomap_write_begin()`, `__iomap_write_begin()`, `iomap_write_end()`, `iomap_write_iter()`, `iomap_zero_iter()`, and the writeback range helpers.

## Control Flow

Read flow starts in `iomap_read_folio()` or `iomap_readahead()`, which initialize an `iomap_iter` and loop through filesystem-provided mappings. `iomap_read_folio_iter()` handles inline data directly, allocates per-block folio state when needed, trims already-uptodate ranges, zeroes holes/new/post-EOF ranges, and delegates mapped ranges to `ctx->ops->read_folio_range()`. Completion returns through `iomap_finish_folio_read()`, which updates per-block uptodate bits, reports errors, decrements pending bytes, and ends the folio read when all submitted ranges complete.

Buffered write flow starts in `iomap_file_buffered_write()`, which sets `IOMAP_WRITE` plus NOWAIT/DONTCACHE flags and iterates mappings. `iomap_write_iter()` rate-limits dirty pages, faults source iov pages before locking the destination folio, prepares a folio with `iomap_write_begin()`, copies data atomically, marks written ranges uptodate and dirty through `iomap_write_end()`, updates in-memory `i_size` when extending, and advances the iterator. Short writes can shrink the folio size target and retry; failed writes truncate newly allocated pagecache beyond EOF.

`iomap_write_begin()` obtains or batches a folio, validates stale mappings through optional filesystem callbacks, handles inline or buffer-head mappings, or calls `__iomap_write_begin()` to read/zero needed blocks before partial writes. `IOMAP_UNSHARE` forces existing data to be read rather than overwritten.

Delalloc release scans page cache under `invalidate_lock`, finds cached dirty data ranges, and punches only clean/non-dirty portions of a delayed-allocation extent through a filesystem callback so dirty cached data keeps its reservation. Zeroing uses `iomap_zero_range()` and can skip holes/unwritten extents unless dirty pagecache over unwritten mappings requires a flush and stale retry. `iomap_page_mkwrite()` handles mmap write faults by preparing the folio over the current mapping and marking it dirty.

Writeback flow starts in `iomap_writepages()` and processes dirty folios with `iomap_writeback_folio()`. It handles EOF, initializes pending write byte accounting, starts writeback before submission, walks per-block dirty ranges, calls filesystem `writeback_range()`, clears dirty bits, records mapping errors, and then submits pending IO through filesystem `writeback_submit()` if necessary. Completion calls `iomap_finish_folio_write()` to decrement pending byte accounting and end writeback.

## State and Persistence Behavior

The file persists no metadata by itself, but it is responsible for the page-cache state that filesystems eventually write to disk. `iomap_folio_state` stores transient per-block uptodate and dirty state for folios that contain multiple filesystem blocks. Folio flags, mapping errors, dirty/writeback state, and inode `i_size` are updated directly.

Persistence occurs through filesystem callbacks: `iomap_ops` supplies extents, `iomap_write_ops` can customize folio read/get/put/validity, delalloc punch callbacks remove reservations, and writeback callbacks submit disk I/O. Inline data writes copy back into `iomap->inline_data` and mark the inode dirty.

## Dependencies and Integration Points

The file depends on the iomap iterator framework, page cache/folio APIs, writeback control, buffer-head compatibility for `IOMAP_F_BUFFER_HEAD`, block-backed synchronous reads from `bio.c`, filesystem error reporting, swap/migrate-aware folio handling, readahead, mmap fault handling, dirty throttling, and tracepoints from `trace.h`.

Filesystem integration is callback-heavy: callers provide `iomap_ops`, optional `iomap_write_ops`, read ops, writeback ops, and delalloc punch functions. Correctness depends on filesystems returning stable iomaps or implementing `iomap_valid()` and on holding locks documented by the delalloc release path.

## Risks and Edge Cases

Large folios with smaller filesystem blocks are the main subtlety. Per-block uptodate and dirty bitmaps must stay synchronized with folio flags, read completion, invalidation, release, and writeback. Incorrect pending byte accounting can leave folios locked or under writeback forever.

Stale iomaps are a corruption risk: concurrent extent conversion or reclaim can make cached mappings invalid before write-begin, so filesystems that need validation must provide `iomap_valid()`. Short writes, poisoned user pages, post-EOF dirty mmap data, and delalloc reservations all require precise rollback or punch behavior to avoid stale data exposure or leaked reservations.

EOF handling is repeated in read, write, zero, page-mkwrite, and writeback paths. Off-by-one errors around block boundaries, folio boundaries, and `[start,end)` delalloc intervals would affect data integrity. Writeback from reclaim context is rejected because iomap writeback can recurse into filesystem allocation paths.

## Test Signals

Coverage should include full and partial folio reads, mixed uptodate/non-uptodate blocks, inline-data reads/writes, holes/new extents zeroing, reads crossing EOF, read errors and fserror reporting, buffered writes extending `i_size`, NOWAIT failures, DONTCACHE folio selection, short-copy retries, stale iomap retry, buffer-head compatibility, delalloc release with dirty and clean sub-folio blocks, zero range over holes/unwritten/mapped extents, truncate-page partial block zeroing, mmap page faults, writeback of dirty sub-folio ranges, EOF-straddling writeback, mapping error propagation, and reclaim-context writeback rejection.

Tracepoints such as `trace_iomap_readpage`, `trace_iomap_readahead`, `trace_iomap_zero_iter`, `trace_iomap_writeback_folio`, release/invalidate traces, and filesystem writeback callbacks provide useful runtime diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/buffered-io.c -->
