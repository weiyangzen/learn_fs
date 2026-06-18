# subset-b-005645 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exec.c -->
# sources/distributed-fs/ceph-client/fs/exec.c

## Purpose
`exec.c` is the Linux execve implementation. It owns opening an executable for execution, building a temporary `linux_binprm`, counting and copying argv/envp into a new stack, selecting a registered binary-format loader, committing credentials, replacing the task's `mm_struct`, collapsing a multithreaded task into one thread, installing the new executable identity, and exposing `execve`, `execveat`, compat exec syscalls, and `kernel_execve`. It is both VFS-facing and scheduler/security-facing: successful binfmt handlers call back into `begin_new_exec()`, after which failures are fatal to the current task.

## Important APIs, types, and functions
The binary-format registry is `formats` protected by `binfmt_lock`, with exported `__register_binfmt()`, `unregister_binfmt()`, `set_binfmt()`, and internal `put_binfmt()`. `path_noexec()` enforces `MNT_NOEXEC` and `SB_I_NOEXEC`.

Argument setup is handled by `bprm_mm_init()`, `count()`, `count_strings_kernel()`, `bprm_stack_limits()`, `copy_strings()`, `copy_string_kernel()`, `copy_strings_kernel()`, `setup_arg_pages()` on MMU builds, and `transfer_args_to_stack()` on NOMMU builds. `struct user_arg_ptr` abstracts native and compat user pointers.

Executable opening and read helpers include `do_open_execat()`, exported `open_exec()`, optional `read_code()`, and matching `do_close_execat()`. `alloc_bprm()`, `free_bprm()`, and the cleanup class around `struct linux_binprm` own lifetime.

The irreversible exec transition is split across `bprm_execve()`, `exec_binprm()`, `search_binary_handler()`, and exported `begin_new_exec()`, `setup_new_exec()`, and `finalize_exec()`. Security and credential helpers include `prepare_bprm_creds()`, `check_unsafe_exec()`, `bprm_fill_uid()`, `bprm_creds_from_file()`, `would_dump()`, and `set_dumpable()`.

Thread/task replacement helpers are `exec_mmap()`, `de_thread()`, `unshare_sighand()`, and `__set_task_comm()`. User entry points are `SYSCALL_DEFINE3(execve)`, `SYSCALL_DEFINE5(execveat)`, compat syscall wrappers, and `kernel_execve()`.

## Control flow
User syscalls enter `do_execveat_common()`. It rechecks deferred `RLIMIT_NPROC` failure, opens the target with `do_open_execat()`, allocates a new `linux_binprm` and temporary `mm`, counts argv/envp, computes stack limits that include pointer-array space, copies the executable path, environment strings, and arguments backward into the new stack, and inserts an empty `argv[0]` if userspace passed no arguments.

`bprm_execve()` then locks and prepares credentials, records unsafe ptrace/no-new-privs/shared-fs state, sets `current->in_execve`, lets LSMs fill invariant credential state via `security_bprm_creds_for_exec()`, and either returns for `AT_EXECVE_CHECK` or calls `exec_binprm()`. `exec_binprm()` repeatedly calls `search_binary_handler()` to read the initial buffer, run `security_bprm_check()`, and invoke registered `fmt->load_binary()` methods. Interpreter rewrites replace `bprm->file` with `bprm->interpreter`, retain an execfd executable when needed, and are bounded by a small recursion depth.

Binfmt success calls `begin_new_exec()`. That function computes final file-derived credentials, marks `point_of_no_return`, kills sibling threads with `de_thread()`, cancels io_uring, unshares the files table, installs `mm->exe_file`, computes nondumpability, swaps the new `mm` into the task through `exec_mmap()`, resets namespaces/timers/sighand/thread state, applies `CLOEXEC`, adjusts secureexec stack limits, sets dumpability, updates `comm`, flushes signal handlers, commits credentials under LSM hooks, and optionally passes the opened executable as an fd to an interpreter. Afterward, binfmt code calls `setup_new_exec()` and `finalize_exec()` around arch-specific loader setup and `start_thread()`.

On failure before the point of no return, cleanup unwinds the binprm, credentials, executable write denial, temporary `mm`, pages, and interpreter strings. On failure after the point of no return, `bprm_execve()` forces a fatal signal if one is not already pending.

## State and persistence behavior
Most state is transient in the current task and its new `linux_binprm`: copied argv/env pages, temporary stack VMA, new `mm`, executable file, interpreter file, final credentials, flags such as `secureexec`, `interp_flags`, `per_clear`, `point_of_no_return`, and the `execfd` handoff. Persistent user-visible state changes include the task's `mm`, `comm`, credentials, dumpability, signal disposition, fd table after close-on-exec, namespace execution hooks, process event notifications, rseq/user-events state, and `/proc` executable identity.

The global `suid_dumpable` sysctl is persistent kernel configuration under `fs.suid_dumpable`. `formats` is global runtime state owned by binfmt modules. The code updates accounting and notification surfaces through audit, ptrace, proc connector, sched tracepoints, perf events, taskstats, NUMA cleanup, and coredump safety validation.

## Dependencies and integration points
This file integrates VFS pathname opening, mount noexec policy, mmap and stack VMA setup, GUP, signal/thread-group management, pid transfer, file-descriptor tables, LSM hooks, credentials/user namespaces/idmapped mounts, binfmt modules, scheduler and cgroup threadgroup transitions, io_uring cancellation, perf, audit, ptrace, proc connector, rseq, user events, sysctl, coredump, and architecture `start_thread` preparation.

## Risks and test signals
Key risks are point-of-no-return error paths, multithreaded exec races, credential and dumpability mistakes around setuid/setgid/no-new-privs/ptrace/shared-fs states, stale executable fd/path handling for interpreters, stack-limit overflows, user pointer faults while copying arguments, module lifetime races while traversing binfmt handlers, `CLOEXEC` ordering versus dumpability, and NOMMU/MMU divergence.

Useful tests include `execve`/`execveat` with `AT_EMPTY_PATH`, `AT_SYMLINK_NOFOLLOW`, `AT_EXECVE_CHECK`, inaccessible `/dev/fd` interpreter paths, null argv, huge argv/envp near `ARG_MAX`, fatal signals during copy, setuid/setgid under idmapped mounts and user namespaces, ptrace/no-new-privs/LSM combinations, multithreaded exec from non-leader threads, close-on-exec races, binfmt interpreter chains, compat exec syscalls, noexec mounts, unreadable executable coredump policy, and fault injection after `begin_new_exec()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/Kconfig -->
# sources/distributed-fs/ceph-client/fs/exfat/Kconfig

## Purpose
`Kconfig` exposes the exFAT filesystem driver to the kernel configuration system. It declares the build-time switch for native exFAT support and a separate default charset option used when mounts do not specify `iocharset=`.

## Important APIs, types, and functions
`config EXFAT_FS` is a tristate option named "exFAT filesystem support". It selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`, which are required by the implementation files in this directory. `config EXFAT_DEFAULT_IOCHARSET` is a string option defaulting to `"utf8"` and depending on `EXFAT_FS`.

## Control flow
This file has no runtime flow. During kernel configuration, enabling `EXFAT_FS=y` links the driver built-in and `EXFAT_FS=m` builds `exfat.ko`. The default iocharset string becomes `CONFIG_EXFAT_DEFAULT_IOCHARSET`, which `super.c` uses for mount option defaults.

## State and persistence behavior
The selected tristate persists in the kernel build configuration. The default charset persists as a compiled-in string but can be overridden per mount through the exFAT mount options. The selected helper dependencies determine whether the driver can use buffer-head block I/O, NLS conversion tables, and legacy direct I/O helpers.

## Dependencies and integration points
The option is consumed by the exFAT `Makefile` and by code guarded through normal `CONFIG_EXFAT_FS` build selection. Its `select` lines tie the driver to core block-buffer cache, NLS, and direct-I/O infrastructure.

## Risks and test signals
Risks are configuration-level: missing selected dependencies would break compilation, and a poor default charset changes filename conversion behavior for users who do not pass `iocharset`. Test signals include all three build modes (`n`, `m`, `y`), mount behavior with default and overridden iocharset, and build coverage when NLS or buffer-head options are otherwise disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/Makefile -->
# sources/distributed-fs/ceph-client/fs/exfat/Makefile

## Purpose
The exFAT `Makefile` maps `CONFIG_EXFAT_FS` to the `exfat.o` composite object and lists the implementation translation units that form the filesystem driver.

## Important APIs, types, and functions
The only build targets are `obj-$(CONFIG_EXFAT_FS) += exfat.o` and `exfat-y := inode.o namei.o dir.o super.o fatent.o cache.o nls.o misc.o file.o balloc.o`. This expresses the driver layering: superblock/mount, inode/address-space, namespace operations, directory entries, FAT and bitmap allocation, cluster cache, NLS conversion, miscellaneous checksums/time/errors, and file operations.

## Control flow
There is no runtime control flow. Kbuild compiles the listed objects and links them into `exfat.o`; that composite is linked built-in or as `exfat.ko` depending on `EXFAT_FS`.

## State and persistence behavior
The file persists the compile-time module composition. Adding, removing, or reordering objects affects symbol availability and module init/exit linkage, but does not store filesystem runtime state.

## Dependencies and integration points
The Makefile integrates with the kernel build system and the `Kconfig` option in the same directory. It expects `super.o` to provide module registration and uses the other objects for the file and inode operation tables exported through headers.

## Risks and test signals
Risks include omitting a source object that defines referenced symbols, adding duplicate definitions, or failing modular build linkage. Test signals are `CONFIG_EXFAT_FS=m` and `=y` builds, `modpost` symbol checks, and boot/module-load smoke tests that mount an exFAT image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/balloc.c -->
# sources/distributed-fs/ceph-client/fs/exfat/balloc.c

## Purpose
`balloc.c` implements allocation bitmap management for exFAT. It locates and loads the on-disk allocation bitmap from the root directory, keeps bitmap sectors pinned in `sbi->vol_amap`, sets/tests/clears cluster bits, counts used clusters, finds the next free cluster, and implements `FITRIM` support by discarding contiguous free cluster ranges.

## Important APIs, types, and functions
`exfat_load_bitmap()` scans root directory entries for the primary `TYPE_BITMAP` entry and calls `exfat_allocate_bitmap()`. `exfat_allocate_bitmap()` validates bitmap size, allocates the buffer-head array, reads bitmap sectors with readahead, and checks that the bitmap's own clusters are marked allocated via `exfat_test_bitmap_range()`. `exfat_free_bitmap()` releases bitmap buffers.

`exfat_set_bitmap()`, `exfat_clear_bitmap()`, and `exfat_test_bitmap()` mutate or query a single cluster bit. `exfat_find_free_bitmap()` scans little-endian machine-word chunks from a hint cluster and wraps to the beginning. `exfat_count_used_clusters()` counts set bits across the bitmap. `exfat_trim_fs()` walks free-cluster runs under `bitmap_lock` and calls `sb_issue_discard()`.

## Control flow
During mount, `exfat_load_bitmap()` starts at `sbi->root_dir` as an `ALLOC_FAT_CHAIN`, reads dentries cluster by cluster, and stops at a bitmap entry with flags zero. Bitmap allocation computes the expected byte length from `EXFAT_DATA_CLUSTER_COUNT()`, tolerates only oversized on-disk bitmaps, reads each sector into `sbi->vol_amap`, and verifies the bitmap file's clusters are allocated.

Allocation paths in `fatent.c` call `exfat_find_free_bitmap()` to choose clusters and `exfat_set_bitmap()` to mark them. Freeing calls `exfat_clear_bitmap()` and expects an already-set bit; clearing an unset bit is treated as I/O/corruption. `FITRIM` translates byte ranges to cluster ranges, finds successive free clusters, coalesces adjacent free clusters, discards ranges meeting `minlen`, honors fatal signals, and returns trimmed byte count in `range->len`.

## State and persistence behavior
Persistent state is the on-disk allocation bitmap file, represented in memory as buffer heads in `sbi->vol_amap`. Updates mark bitmap buffers dirty and optionally synchronously write them through `exfat_update_bh()`. Runtime fields affected include `sbi->map_clu`, `sbi->map_sectors`, `sbi->vol_amap`, and, indirectly through callers, `sbi->used_clusters` and `sbi->clu_srch_ptr`. `bitmap_lock` serializes allocation/free/trim scans that depend on bitmap consistency.

## Dependencies and integration points
This file depends on directory entry reading (`exfat_get_dentry()`), FAT-chain traversal (`exfat_get_next_cluster()`), readahead (`exfat_blk_readahead()`), buffer-head update helpers, cluster/bitmap macros in `exfat_fs.h`, raw dentry definitions, and block discard APIs. It is used by mount, cluster allocation/free, statfs used-cluster accounting, and file ioctl trim.

## Risks and test signals
Risks include endian/word-size mistakes in bitmap word scanning, trusting a corrupt bitmap size, races if callers mutate bitmap without `bitmap_lock`, incorrect wraparound in `exfat_find_free_bitmap()`, mismatches between bitmap bits and FAT chains, and discard over ranges that are not really free. Useful tests include mount images with valid, oversized, undersized, missing, and self-unmarked bitmaps; allocation/free stress around sector and word boundaries; 32-bit and 64-bit builds; full-volume allocation; trim with different `start/len/minlen`; signal interruption; and fsck-style corrupt bitmap/FAT mismatch images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/balloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/cache.c -->
# sources/distributed-fs/ceph-client/fs/exfat/cache.c

## Purpose
`cache.c` provides a small per-inode LRU cache for logical-file-cluster to physical-disk-cluster runs. exFAT can represent a file as either a contiguous no-FAT chain or an explicit FAT chain; this cache accelerates repeated FAT-chain walks for non-contiguous files.

## Important APIs, types, and functions
`struct exfat_cache` stores one run: file-cluster start, disk-cluster start, and number of contiguous clusters. `struct exfat_cache_id` carries a candidate run and cache generation id while walking. `exfat_cache_init()` and `exfat_cache_shutdown()` manage the `exfat_cachep` slab. `exfat_cache_inval_inode()` drops all cached runs and increments `ei->cache_valid_id`.

Internal helpers include `exfat_cache_lookup()`, `exfat_cache_merge()`, `exfat_cache_add()`, `exfat_cache_update_lru()`, `cache_init()`, and `cache_contiguous()`. The exported mapping entry point is `exfat_get_cluster()`.

## Control flow
`exfat_get_cluster()` starts at `ei->start_clu`, handles empty and EOF chains, and returns immediately for the first cluster. It seeds a candidate cache entry, asks `exfat_cache_lookup()` for the best cached run covering or preceding the requested file cluster, and stops the target range at the next known cache boundary. If the cache covers the requested range, it returns the physical cluster and contiguous count.

On a cache miss or partial hit, `exfat_get_cluster()` reads FAT entries with `exfat_ent_get()` until the requested logical cluster is reached, resetting the candidate when the next physical cluster is not contiguous. It then scans forward while FAT entries remain physically contiguous to report the largest mappable extent. Discovered runs are inserted or merged under `cache_lru_lock`; stale candidate ids are ignored after invalidation.

## State and persistence behavior
The cache is purely in-memory and per inode. `struct exfat_inode_info` owns `cache_lru`, `nr_caches`, `cache_lru_lock`, and `cache_valid_id`. Persistent FAT entries are not changed here; this file only reads them. Invalidations occur on truncate and other chain-structure changes to prevent stale physical mappings from being reused.

## Dependencies and integration points
The cache depends on `exfat_ent_get()` for FAT reads, `exfat_inode_info` fields from `exfat_fs.h`, and slab/list/spinlock primitives. It is used by `exfat_map_cluster()` in `inode.c` for buffered I/O, direct I/O, bmap, and readahead.

## Risks and test signals
Risks include stale cache use after allocation/free/truncate, off-by-one errors in `nr_contig` semantics, LRU races during allocation failure and invalidation, and incorrect mapping if a corrupted FAT chain loops or points outside the volume. Tests should cover repeated random reads on fragmented files, truncate followed by read/write, extension that converts no-FAT to FAT chain, direct I/O and bmap after cache hits, concurrent invalidation under lockdep/KCSAN, and fault injection for slab allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/dir.c -->
# sources/distributed-fs/ceph-client/fs/exfat/dir.c

## Purpose
`dir.c` implements exFAT directory entry parsing, iteration, entry-set caching, filename dentry assembly, directory checksum updates, empty-slot validation, lookup scanning, subdirectory counting, new directory allocation, and volume label read/write. exFAT represents one file with a primary file dentry, a stream-extension dentry, one or more filename dentries, and optional secondary dentries; this file owns that multi-entry contract.

## Important APIs, types, and functions
Directory iteration uses `exfat_readdir()` and `exfat_iterate()` exported through `exfat_dir_operations`. Entry type decoding and construction use `exfat_get_entry_type()`, `exfat_set_entry_type()`, `exfat_init_dir_entry()`, `exfat_init_stream_entry()`, `exfat_init_name_entry()`, `exfat_init_ext_entry()`, and `exfat_calc_num_entries()`.

Entry-set cache APIs are `exfat_get_dentry()`, `exfat_get_dentry_cached()`, `exfat_get_dentry_set()`, `exfat_get_empty_dentry_set()`, and `exfat_put_dentry_set()`. `exfat_update_dir_chksum()` computes the primary-file checksum while skipping the checksum field. `exfat_remove_entries()` marks entry sets deleted and frees benign secondary allocated clusters.

Search and metadata helpers include `exfat_find_dir_entry()`, `exfat_count_dir_entries()`, `exfat_alloc_new_dir()`, `exfat_read_volume_label()`, and `exfat_write_volume_label()`.

## Control flow
`exfat_iterate()` emits dot entries, rounds VFS position to dentry size, allocates a temporary name buffer, and repeatedly calls `exfat_readdir()` under `s_lock`. `exfat_readdir()` uses directory hints, walks clusters, skips non-file entries, reads the full name from extension entries, converts UTF-16 to the mounted NLS/UTF-8 encoding, updates the directory bitmap hint, and advances `ctx->pos` past the whole entry set.

`exfat_get_dentry()` maps a logical directory entry index to sector/offset using `exfat_find_location()`, checks chain and bitmap validity, optionally triggers readahead, and returns a direct pointer into a buffer head. Entry-set fetches read enough adjacent sectors to cover all requested dentries; validation enforces file -> stream -> name -> optional benign-secondary ordering. Empty entry-set validation accepts deleted after unused for compatibility but reports used-after-unused corruption.

`exfat_find_dir_entry()` is the main case-insensitive scanner. It uses `hint_stat` to avoid restarting from zero, tracks a file/stream/name/secondary state machine, matches stream name hash and length before comparing filename dentries with `exfat_uniname_ncmp()`, records first-empty-entry hints, rewinds once to cover entries before the hint, and detects excessive cluster traversal. Volume label helpers scan root entries for `TYPE_VOLUME`, reuse the first empty slot if needed, and update a single dentry.

## State and persistence behavior
Persistent state is the directory entry stream itself: file, stream, name, volume label, bitmap, upcase, and secondary dentries. Modifications are made through buffer-head-backed entry sets; `es->modified` controls whether `exfat_update_bhs()` writes dirty buffers. Directory checksums are persisted in the file dentry. Runtime state includes directory hints (`hint_bmap`, `hint_stat`, `hint_femp`) in `exfat_inode_info`, temporary `exfat_entry_set_cache` buffer arrays, and name buffers allocated from the name cache.

## Dependencies and integration points
This file depends on FAT/cluster walking, bitmap testing, NLS conversion, checksum/time helpers, buffer-head I/O, VFS directory iteration, file ioctls/fsync from `file.c`, and inode building/lookup from `inode.c`/`namei.c`. It is central to mount-time bitmap/upcase discovery, path lookup, create/mkdir/rename/unlink, readdir, stat link counts, and filesystem label ioctls.

## Risks and test signals
Risks include entry-set validation accepting corrupt layouts, checksum drift after partial updates, stale hints after directory mutation, off-by-one positions across cluster boundaries, direct buffer-head pointer lifetime misuse, benign secondary cluster leaks, looped directory FAT chains, and compatibility behavior around unused/deleted dentries. Tests should cover long 255-character names, names spanning sector and cluster boundaries, directory growth, deletion/reuse hints, corrupted stream/name ordering, volume label create/clear/update, readdir while mutating, empty directories with zero-size and allocated clusters, and fsck images with loops or bitmap mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/exfat_fs.h -->
# sources/distributed-fs/ceph-client/fs/exfat/exfat_fs.h

## Purpose
`exfat_fs.h` is the private in-kernel contract for the exFAT driver. It defines driver-wide constants, conversion macros, in-memory superblock and inode structures, directory/name helper structures, attribute/mode conversion helpers, cluster/FAT/bitmap geometry helpers, operation-table declarations, and prototypes for all exFAT implementation files.

## Important APIs, types, and functions
Important types include `enum exfat_error_mode`, `struct exfat_dentry_namebuf`, `struct exfat_uni_name`, `struct exfat_chain`, `struct exfat_hint_femp`, `struct exfat_hint`, `struct exfat_entry_set_cache`, `struct exfat_dir_entry`, `struct exfat_mount_options`, `struct exfat_sb_info`, and `struct exfat_inode_info`.

Important helpers include `EXFAT_SB()`, `EXFAT_I()`, `exfat_forced_shutdown()`, `exfat_mode_can_hold_ro()`, `exfat_make_mode()`, `exfat_make_attr()`, `exfat_save_attr()`, `exfat_is_last_sector_in_cluster()`, `exfat_cluster_to_sector()`, `exfat_sector_to_cluster()`, `is_valid_cluster()`, `exfat_ondisk_size()`, `exfat_cluster_walk()`, and `exfat_chain_advance()`.

Macros define entry-set indices, dentry type classes, max name sizes, cluster/block/dentry conversions, FAT entry offsets, allocation bitmap offsets, directory cache sizing, and the `EXFAT_FLAGS_SHUTDOWN` runtime flag. Prototypes expose superblock, FAT, bitmap, file, namei, cache, dir, inode, NLS, and misc APIs.

## Control flow
The header has no independent runtime flow, but it defines common call contracts. Code generally converts VFS objects to exFAT objects with `EXFAT_SB()`/`EXFAT_I()`, uses geometry macros to translate file offsets to clusters/sectors/dentries, walks chains through `exfat_cluster_walk()`/`exfat_chain_advance()`, and uses prototypes grouped by source file to coordinate operations.

## State and persistence behavior
`struct exfat_sb_info` is the central mounted-volume state: sector/cluster geometry, FAT and data starts, root cluster, volume flags, boot-sector buffer, allocation bitmap buffers, upcase table, allocation search pointer, used-cluster count, shutdown flags, global `s_lock`, `bitmap_lock`, mount options, NLS table, ratelimit state, and inode hash table.

`struct exfat_inode_info` extends VFS inodes with on-disk directory location, type/attr/start cluster/flags, lookup and bmap hints, cluster cache LRU state, directory-entry position hash, valid size, truncate lock, and creation time. Persistent values are mirrored from directory entries and stream extensions; hints, caches, locks, hash nodes, and shutdown flags are runtime-only.

## Dependencies and integration points
The header pulls in Linux VFS, NLS, block device, ratelimit, backing-device, and UAPI exFAT definitions, plus raw on-disk definitions through implementation files. Every exFAT source file depends on this header for shared structures and prototypes. It is the integration point between VFS operation tables, address-space operations, mount option parsing, FAT allocation, bitmap allocation, directory entry handling, and filename conversion.

## Risks and test signals
Risks include macro arithmetic overflow or off-by-one conversion errors, lock contract drift, misuse of persisted versus runtime inode fields, inconsistent `ALLOC_NO_FAT_CHAIN` versus `ALLOC_FAT_CHAIN` semantics, and ABI-visible changes to ioctl or mount option behavior via UAPI. Tests include compile coverage of all objects, 32-bit/64-bit arithmetic, maximum cluster and directory sizes, no-FAT and FAT-chain files, read-only/shutdown paths, mode/attribute conversions under different masks, and lockdep around `s_lock`, `bitmap_lock`, cache LRU, and truncate lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/exfat_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/exfat_raw.h -->
# sources/distributed-fs/ceph-client/fs/exfat/exfat_raw.h

## Purpose
`exfat_raw.h` defines exFAT on-disk constants and packed raw structures. It describes boot-sector layout, directory entry types, FAT special cluster values, allocation flags, file attributes, checksum modes, timestamp limits, and the union representation of every 32-byte exFAT dentry variant used by the driver.

## Important APIs, types, and functions
Key constants include boot signatures, `"EXFAT   "` filesystem name, volume flags (`VOLUME_DIRTY`, `MEDIA_FAILURE`), cluster sentinels (`EXFAT_EOF_CLUSTER`, `EXFAT_BAD_CLUSTER`, `EXFAT_FREE_CLUSTER`), first/reserved cluster constants, allocation flags (`ALLOC_POSSIBLE`, `ALLOC_FAT_CHAIN`, `ALLOC_NO_FAT_CHAIN`), dentry size and maximum directory entries, raw dentry type bytes, checksum modes, file attributes, sector/cluster limits, and timestamp bounds.

`struct boot_sector` is the packed main/backup boot sector format. `struct exfat_dentry` is a packed 32-byte dentry with union arms for file, stream, name, bitmap, upcase, volume label, vendor extension, vendor allocation, and generic secondary entries. `EXFAT_TZ_VALID` marks valid timezone offset fields.

## Control flow
There is no executable control flow. Runtime code reads these structures from buffer heads and converts little-endian fields with the kernel endian helpers. Entry classification in `dir.c`, boot validation in `super.c`, allocation in `fatent.c`/`balloc.c`, NLS upcase loading, and timestamp conversion in `misc.c` all depend on this exact raw layout.

## State and persistence behavior
Everything in this header describes persistent on-disk state. The packed layout must match the exFAT specification byte-for-byte. The driver persists file size and valid size in stream entries, timestamps and attributes in file entries, UTF-16 name fragments in name entries, allocation bitmap/upcase metadata in root-directory system entries, and volume flags in the boot sector.

## Dependencies and integration points
The header depends only on Linux integer types. It is included by all implementation files that parse or write disk data and by `exfat_fs.h` users indirectly through shared type references. It bridges block-buffer contents to higher-level exFAT in-memory structures.

## Risks and test signals
Risks are layout and interpretation bugs: missing `__packed`, incorrect little-endian conversion, raw type classification drift, timestamp range mishandling, treating reserved cluster values as valid, and incorrectly handling benign versus critical secondary entries. Tests should mount known-good images, fuzz boot sectors and dentries, verify structure sizes/offsets at build time, exercise vendor/benign secondary entries, validate timezone/timestamp bounds, and run cross-endian or sparse/static-analysis checks for endian annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/exfat_raw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/fatent.c -->
# sources/distributed-fs/ceph-client/fs/exfat/fatent.c

## Purpose
`fatent.c` implements FAT entry I/O, FAT mirroring, FAT-chain construction, cluster allocation/freeing, cluster-chain counting, cluster zeroing, and block readahead helpers. Together with `balloc.c`, it maintains exFAT's persistent allocation state: bitmap bits identify allocated clusters, and FAT entries link clusters when a file is not represented as a contiguous no-FAT chain.

## Important APIs, types, and functions
FAT entry primitives are `exfat_ent_get()`, `exfat_ent_set()`, internal `__exfat_ent_get()`, `__exfat_ent_set()`, `exfat_end_bh()`, and `exfat_mirror_bh()`. Readahead and chain helpers include `exfat_blk_readahead()`, `exfat_chain_cont_cluster()`, `exfat_find_last_cluster()`, and `exfat_count_num_clusters()`.

Cluster lifecycle APIs are `exfat_alloc_cluster()`, `exfat_free_cluster()`, internal `__exfat_free_cluster()`, `exfat_zeroed_cluster()`, and `exfat_discard_cluster()`. They call bitmap helpers and, when needed, FAT setters.

## Control flow
`exfat_ent_get()` validates the requested cluster, reads or reuses the proper FAT sector buffer, remaps reserved values above bad-cluster to EOF, rejects free/bad/out-of-range content, and leaves the buffer cached for the caller to release. `exfat_ent_set()` writes one FAT entry and mirrors the containing sector to FAT2 when present.

`exfat_alloc_cluster()` runs under `bitmap_lock`. It verifies free-space accounting, chooses a hint cluster from the caller or `sbi->clu_srch_ptr`, finds free bitmap bits, sets bitmap bits, initializes FAT entries when the chain uses FAT, links from the prior cluster, and increments `p_chain->size`. If contiguous allocation breaks while the caller wanted `ALLOC_NO_FAT_CHAIN`, it materializes the previous contiguous run with `exfat_chain_cont_cluster()` and switches to `ALLOC_FAT_CHAIN`. On failure it frees the partially allocated chain.

`__exfat_free_cluster()` clears bitmap bits for either a no-FAT contiguous range or a FAT-linked chain, optionally issues discard for contiguous physical runs, detects possible chain loops by bounding traversal, and decrements `used_clusters`. Truncate and rmdir paths call it through `exfat_free_cluster()`. `exfat_zeroed_cluster()` obtains each buffer in a cluster, zeroes it, marks it dirty, and synchronizes a blockdev range for synchronous directories.

## State and persistence behavior
Persistent state modified here includes FAT1/FAT2 sectors and allocation bitmap bits; discard informs lower storage but does not change exFAT metadata. Runtime state updated includes `sbi->used_clusters`, `sbi->clu_srch_ptr`, chain descriptors passed by callers, and the `discard` mount option when the device reports unsupported discard. FAT writes are buffer-head dirty writes, optionally synchronous through `exfat_update_bh()`.

## Dependencies and integration points
This file depends on bitmap operations, buffer-head block I/O, block discard, cluster geometry macros, mount options, and sync helpers. It is called by inode block mapping, file expansion/truncate, directory growth, mkdir/rmdir, rename replacement cleanup, and directory allocation.

## Risks and test signals
Risks include bitmap/FAT ordering inconsistency, failure rollback leaks, FAT2 mirroring errors, looped chain traversal, incorrect conversion from contiguous to FAT chains, stale `used_clusters`, discard of allocated clusters, and synchronous write failures. Tests should cover fragmented and contiguous allocation, ENOSPC rollback, FAT2 images, discard-supported and unsupported devices, cluster zeroing for directories, corrupt FAT loops, truncate after allocation failure, full-volume wraparound allocation, and power-fail ordering with fsck validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/fatent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/file.c -->
# sources/distributed-fs/ceph-client/fs/exfat/file.c

## Purpose
`file.c` implements VFS file operations and inode attribute operations for regular exFAT files. It handles fallocate-style preallocation, truncate/extend semantics, chmod/chown/time validation, FAT-compatible attribute ioctls, volume label and shutdown ioctls, trim ioctl forwarding, fsync, valid-data-length extension, write/read/mmap/splice wrappers, and the exported `exfat_file_operations` and `exfat_file_inode_operations`.

## Important APIs, types, and functions
Growth and truncate helpers are `exfat_cont_expand()`, `exfat_fallocate()`, `__exfat_truncate()`, and `exfat_truncate()`. Attribute paths are `exfat_getattr()`, `exfat_setattr()`, `exfat_sanitize_mode()`, and `exfat_allow_set_time()`.

Ioctl helpers include `exfat_ioctl_get_attributes()`, `exfat_ioctl_set_attributes()`, `exfat_ioctl_fitrim()`, `exfat_ioctl_shutdown()`, `exfat_ioctl_get_volume_label()`, `exfat_ioctl_set_volume_label()`, `exfat_ioctl()`, and `exfat_compat_ioctl()`. I/O hooks include `exfat_file_fsync()`, `exfat_extend_valid_size()`, `exfat_file_write_iter()`, `exfat_file_read_iter()`, `exfat_page_mkwrite()`, `exfat_file_mmap_prepare()`, and `exfat_splice_read()`.

## Control flow
`exfat_cont_expand()` grows a file by allocating enough clusters for the requested size, appending them to an existing chain, converting to FAT-chain mode if needed, updating `i_size` and `i_blocks`, but deliberately not increasing `valid_size` for unwritten preallocated ranges. `exfat_fallocate()` exposes this only for `FALLOC_FL_ALLOCATE_RANGE` on regular files.

`__exfat_truncate()` marks the volume dirty, computes new versus physical cluster counts, advances to the first cluster to free, shrinks `valid_size`, sets archive attribute, writes the directory entry before cutting the FAT chain, invalidates the cluster cache and hints, then frees removed clusters. This ordering reduces the chance that a crash leaves freed clusters still referenced by the directory entry.

`exfat_setattr()` handles extension before generic checks when `ATTR_SIZE` grows, permits configured owner/group time updates, rejects unsupported uid/gid/mode changes, sanitizes Unix mode into exFAT's limited attribute model, zeroes the tail block on shrink, serializes truncate through `truncate_lock`, and calls `exfat_truncate()`. Write paths zero gaps up to `valid_size` before writing beyond it, then call generic buffered write. Mmap write faults extend `valid_size` before `filemap_page_mkwrite()`.

## State and persistence behavior
Persistent metadata changed here includes directory entry file attributes, stream size, valid size, timestamps, FAT chains, bitmap bits, volume label entries, volume dirty/shutdown flags, and block discard state. Runtime state includes `ei->valid_size`, `ei->start_clu`, `ei->flags`, `ei->attr`, inode size, block count, page cache, and forced shutdown flag. `exfat_file_fsync()` flushes page metadata through `simple_fsync_noflush()`, synchronizes the block device, and issues a device flush.

## Dependencies and integration points
This file depends on FAT and bitmap allocation, inode writeback, directory entry sets, NLS conversion, volume-label helpers, shutdown support in `super.c`, VFS setattr/write/read/mmap/ioctl APIs, blockdev discard/flush, security inode setattr hooks, and legacy FAT ioctl numbers from `msdos_fs.h`.

## Risks and test signals
Risks include valid-size exposure of stale data, crash ordering during truncate/free, file extension without zeroing gaps, direct-I/O alignment differences, chmod/attribute mismatches, ioctl capability/security gaps, forced-shutdown bypass, and concurrent write/truncate races. Tests should include fsx, xfstests generic write/truncate/fallocate/mmap/direct-I/O cases, sparse writes beyond valid size, attr ioctls on files and root directory, volume-label ioctls with lossy names, FITRIM permission and range checks, shutdown ioctl behavior, fsync power-fail testing, and mode mask mount-option combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/inode.c -->
# sources/distributed-fs/ceph-client/fs/exfat/inode.c

## Purpose
`inode.c` implements exFAT inode writeback, logical-to-physical block mapping, buffered/direct address-space operations, inode hash lookup by on-disk directory position, inode construction from directory entries, and inode eviction. It is the bridge between VFS page-cache I/O and exFAT cluster allocation semantics.

## Important APIs, types, and functions
Metadata writeback APIs are `__exfat_write_inode()`, `exfat_write_inode()`, and `exfat_sync_inode()`. Mapping helpers are `exfat_map_cluster()`, `exfat_get_block()`, and `exfat_block_truncate_page()`. Address-space callbacks include `exfat_read_folio()`, `exfat_readahead()`, `exfat_writepages()`, `exfat_write_begin()`, `exfat_write_end()`, `exfat_direct_IO()`, and `exfat_aop_bmap()`.

Inode cache helpers are `exfat_hash_inode()`, `exfat_unhash_inode()`, `exfat_iget()`, `exfat_fill_inode()`, `exfat_build_inode()`, and `exfat_evict_inode()`. `exfat_aops` binds exFAT block mapping to the VFS page cache.

## Control flow
`__exfat_write_inode()` skips root and deleted inodes, marks the volume dirty, fetches the inode's on-disk entry set, writes attributes and create/modify/access times, serializes `i_size` and `valid_size`, writes stream flags/start cluster or zero-size values, refreshes the entry checksum, and writes the dentry buffers. `exfat_write_inode()` wraps it in `s_lock`.

`exfat_get_block()` serializes through `s_lock`, rejects unmapped reads beyond EOF, asks `exfat_map_cluster()` for the cluster backing the requested block, maps contiguous sectors into `bh_result`, and enforces valid-data-length behavior. Reads beyond valid size are left unmapped or partially read and zero-filled; creates mark new buffers and extend `ei->valid_size`. `exfat_map_cluster()` handles no-FAT chains directly, consults `exfat_get_cluster()` for FAT chains, allocates missing clusters when `create` is true, appends them to the existing chain, converts to FAT-chain mode when allocation is no longer contiguous, and updates bmap hints.

Buffered and direct I/O use the common mapper. `exfat_write_begin()` allocates blocks through `block_write_begin()`, `exfat_write_end()` updates `valid_size` and archive attribute, and `exfat_direct_IO()` uses locking direct I/O plus explicit valid-size updates/zeroing around partial written blocks. Readahead avoids multi-page readahead across a valid-size boundary. Bmap takes `truncate_lock` to avoid races with truncate.

## State and persistence behavior
Persistent state includes directory entry timestamps/attrs/checksums, stream size/valid size/start cluster/flags, FAT links, and allocation bitmap changes triggered by mapping. Runtime inode state includes page cache, `i_blocks`, `i_size`, `ei->valid_size`, `ei->start_clu`, `ei->flags`, bmap hints, inode hash table membership keyed by `i_pos`, `i_generation`, and VFS operation pointers. Eviction truncates unlinked files under `s_lock`, clears page cache, invalidates cluster caches, and removes inode hash entries.

## Dependencies and integration points
This file depends on `file.c` truncate helpers, `fatent.c` allocation and FAT I/O, `cache.c` cluster cache, directory entry-set APIs, time/attribute helpers, VFS address-space and buffer-head helpers, direct-I/O infrastructure selected by Kconfig, and superblock inode allocation in `super.c`. `namei.c` calls `exfat_build_inode()` after lookups and updates inode hashes after rename.

## Risks and test signals
Risks include stale data beyond valid size, block mapping races with truncate, invalid cache hints after chain mutation, incorrect `i_blocks`, writeback of deleted entries, direct-I/O zeroing mistakes, and inode aliasing if `i_pos` hashing is wrong. Tests should cover buffered/direct/mmap writes across valid-size boundaries, bmap during truncate, read beyond valid size, eviction of unlinked open files, rename followed by lookup using old/new positions, root inode special cases, fragmented files with cache hits, and fault injection in directory entry writeback and cluster allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/misc.c -->
# sources/distributed-fs/ceph-client/fs/exfat/misc.c

## Purpose
`misc.c` contains shared exFAT utility routines for filesystem error policy, timestamp conversion, atime truncation, 16-bit and 32-bit checksums, buffer-head update/writeback, and `struct exfat_chain` assignment/copy.

## Important APIs, types, and functions
`__exfat_fs_error()` reports filesystem corruption and enforces the mount `errors=` policy. Time helpers are `exfat_get_entry_time()`, `exfat_set_entry_time()`, `exfat_truncate_atime()`, and `exfat_truncate_inode_atime()`. Checksum helpers are `exfat_calc_chksum16()` and `exfat_calc_chksum32()`. Buffer helpers are `exfat_update_bh()` and `exfat_update_bhs()`. Chain helpers are `exfat_chain_set()` and `exfat_chain_dup()`.

## Control flow
`__exfat_fs_error()` conditionally prints a ratelimited or normal error, then either panics, remounts read-only, or continues according to `sbi->options.errors`. Timestamp reading converts DOS-style date/time fields to Unix time, applies centisecond precision where present, and adjusts either the stored valid exFAT timezone offset or the configured/system timezone. Timestamp writing stores local UTC-equivalent fields and marks the timezone offset as valid zero.

Checksum helpers rotate the accumulator and add each byte, skipping checksum fields for directory-entry and boot-sector checksum modes. Buffer update helpers mark buffers uptodate and dirty, optionally synchronously writing and waiting for all buffers. Chain helpers are thin assignments used throughout allocation and directory walking.

## State and persistence behavior
Error handling can persistently flip the mounted superblock read-only via `SB_RDONLY`. Time conversion reads and writes persistent file dentry fields. Checksum results are persisted by callers in directory entries, boot-region validation, and upcase-table validation. Buffer helpers control when metadata buffers are dirtied and synchronized to disk.

## Dependencies and integration points
This file depends on VFS superblock flags, mount options, Linux time conversion, buffer-head APIs, and raw exFAT checksum/timestamp constants. It is used by almost every exFAT implementation file: directory checksums, inode timestamp writeback, boot/upcase verification, FAT/bitmap/entry-set updates, truncate, create, rename, and corruption handling.

## Risks and test signals
Risks include incorrect timezone interpretation, timestamp truncation mismatch with Windows behavior, checksum skip-offset mistakes, lost synchronous write errors, and over-aggressive read-only remounting. Tests should include timestamp round trips with `time_offset` and `sys_tz`, atime two-second truncation, create/modify centisecond preservation, checksum verification for directory and boot entries, synchronous directory updates, and `errors=continue|panic|remount-ro` behavior under injected corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/namei.c -->
# sources/distributed-fs/ceph-client/fs/exfat/namei.c

## Purpose
`namei.c` implements exFAT VFS namespace operations: dentry hashing/comparison/revalidation, empty directory slot search and directory expansion, path/name conversion for lookup and creation, create, lookup, unlink, mkdir, rmdir, rename, and the directory inode operation table. It connects case-insensitive exFAT naming rules to the Linux dcache and directory-entry machinery in `dir.c`.

## Important APIs, types, and functions
Dentry operations are `exfat_d_revalidate()`, `exfat_d_hash()`, `exfat_d_cmp()`, `exfat_utf8_d_hash()`, `exfat_utf8_d_cmp()`, `exfat_dentry_ops`, and `exfat_utf8_dentry_ops`. Slot and path helpers include `exfat_search_empty_slot()`, `exfat_find_empty_entry()`, `exfat_check_max_dentries()`, `__exfat_resolve_path()`, `exfat_resolve_path()`, `exfat_resolve_path_for_lookup()`, and `exfat_make_i_pos()`.

VFS inode operation implementations are `exfat_create()`, `exfat_lookup()`, `exfat_unlink()`, `exfat_mkdir()`, `exfat_rmdir()`, `exfat_rename()`, plus internal `exfat_add_entry()`, `exfat_find()`, `exfat_check_dir_empty()`, `exfat_rename_file()`, `exfat_move_file()`, and `__exfat_rename()`.

## Control flow
Dentry hashing/comparison strips trailing dots unless `keep_last_dots` is enabled and folds case through `exfat_toupper()`. UTF-8 mounts use UTF-8 decoding directly; NLS mounts use the selected `nls_io` table. Negative dentries store the parent directory version and are invalidated on parent version changes or creation/rename-target lookups.

Create/mkdir call `exfat_add_entry()` under `s_lock`: resolve the VFS name to UTF-16, compute entry count, find or allocate an empty entry set, allocate and zero a first cluster for non-zero-size directories, initialize the file/stream/name dentries, write them synchronously when needed, fill `exfat_dir_entry`, build an inode, set creation timestamps, and instantiate the dentry. `exfat_find_empty_entry()` first consumes `hint_femp`, validates actual empty sets, and grows the directory one cluster at a time when no slot exists.

Lookup resolves the search name in lookup-compatible lossy mode, refreshes directory hints when the parent `i_version` changes, scans with `exfat_find_dir_entry()`, reads file and stream entries into `exfat_dir_entry`, clamps invalid size/valid-size/start-cluster states, counts subdirectories for link count, builds or reuses an inode keyed by on-disk position, and handles dcache aliases.

Unlink/rmdir mark entry sets deleted and clear/unhash inodes; rmdir first verifies no file/dir entries remain and leaves cluster freeing to inode eviction/truncate. Rename resolves the target name, optionally verifies target directory emptiness, either rewrites in place, allocates a larger entry set, or moves to a new parent, then deletes a replaced target's entries and frees replaced directory clusters. It updates inode hashes and link counts after moving directory-entry positions.

## State and persistence behavior
Persistent state includes directory entry sets, directory cluster allocation, directory sizes/valid sizes, FAT/bitmap changes for directory growth and replaced-directory cleanup, and deleted-entry markers. Runtime state includes dentry hashes and negative-dentry version tokens, directory hints, inode hash positions, link counts, inode versions, timestamps, and `DIR_DELETED` markers to suppress later writeback of removed entries.

## Dependencies and integration points
This file depends on `dir.c` entry-set operations and directory scanners, `nls.c` conversion and upcase behavior, `fatent.c` cluster allocation/free/zeroing, inode build/hash/write helpers, VFS dcache/namei APIs, idmapped mount signatures for inode operations, and forced-shutdown state from the superblock.

## Risks and test signals
Risks include case-insensitive dcache alias bugs, trailing-dot compatibility mismatches, stale negative dentries, directory growth without inode writeback, rename partial updates, replacement directory cluster leaks, link-count errors, target/source `DIR_DELETED` races, and lossy-name creation. Tests should cover case-only names, UTF-8 and NLS mounts, trailing-dot options, long names requiring many dentries, directory expansion to max dentry count, create/unlink/mkdir/rmdir/rename under `dirsync`, rename over files and empty directories, hard alias/dcache reuse scenarios, and corrupt target/source dentries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/nls.c -->
# sources/distributed-fs/ceph-client/fs/exfat/nls.c

## Purpose
`nls.c` implements exFAT filename case folding, Unicode/NLS/UTF-8 conversion, name validation and hash calculation, and upcase table loading. exFAT stores filenames as UTF-16 and performs case-insensitive matching through an upcase table; this file owns both the default table and on-disk table verification/loading.

## Important APIs, types, and functions
The large `uni_def_upcase` table is the compressed recommended upcase table. `bad_uni_chars` lists forbidden ASCII characters. Conversion helpers include `exfat_convert_char_to_ucs2()`, `exfat_convert_ucs2_to_char()`, `exfat_utf16_to_utf8()`, `exfat_utf8_to_utf16()`, `__exfat_utf16_to_nls()`, and `exfat_nls_to_ucs2()`.

Public APIs are `exfat_toupper()`, `exfat_uniname_ncmp()`, `exfat_utf16_to_nls()`, `exfat_nls_to_utf16()`, `exfat_create_upcase_table()`, and `exfat_free_upcase_table()`. Upcase loading internals are `exfat_load_upcase_table()` and `exfat_load_default_upcase_table()`.

## Control flow
Lookup and create paths convert VFS byte names into `struct exfat_uni_name`. UTF-8 mounts use kernel UTF-8 helpers; NLS mounts convert via `nls_io`. Invalid conversion falls back to `_` and sets `NLS_NAME_LOSSY` for NLS mode; creation rejects lossy names while lookup can tolerate them for compatibility. Both conversion paths reject control characters and the forbidden ASCII punctuation set. The uppercased UTF-16 name is checksummed with `exfat_calc_chksum16()` for the stream extension name hash.

Read paths convert UTF-16 names back to either UTF-8 or the configured NLS encoding. NLS output replaces unsupported surrogate-pair code points with `_` because the kernel NLS framework cannot represent code points above U+FFFF. Case-insensitive comparisons call `exfat_toupper()` per UTF-16 unit.

At mount, `exfat_create_upcase_table()` scans root directory entries for `TYPE_UPCASE`. If found, it reads the upcase table clusters, expands compressed identity/skip markers into a 65536-entry table, computes the 32-bit checksum, and accepts it only if index coverage and checksum match. Non-I/O validation failure falls back to the built-in default table; missing table also falls back. `exfat_free_upcase_table()` releases `sbi->vol_utbl`.

## State and persistence behavior
Persistent state read here is the upcase table dentry and table file. Runtime state is `sbi->vol_utbl`, a 65536-entry array where zero means identity mapping. Filename hashes are persisted into stream dentries by callers. No on-disk state is directly modified in this file.

## Dependencies and integration points
This file depends on root-directory scanning, dentry type decoding, FAT chain traversal, checksum helpers, NLS and UTF-8 kernel APIs, and mount option `utf8`. It is used by dcache hashing/comparison, lookup, create, rename, readdir, and volume-label ioctls.

## Risks and test signals
Risks include lossy conversion policy mismatches, surrogate-pair handling differences between UTF-8 and NLS mounts, upcase-table checksum/expansion bugs, forbidden-character compatibility gaps, name-hash collisions or drift, and fallback to default table hiding a corrupt table. Tests should cover non-ASCII case-insensitive lookups, invalid byte sequences, names with forbidden characters, surrogate pairs, max-length names, UTF-8 versus iocharset mounts, corrupt upcase table checksum, missing upcase table fallback, and volume labels with lossy conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/nls.c -->
