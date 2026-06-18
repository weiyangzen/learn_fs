# Research: subset-b-006005

This grouped report covers the requested init and io_uring source files. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/initramfs.c -->
# sources/distributed-fs/ceph-client/init/initramfs.c

## Purpose
`initramfs.c` implements early rootfs population. It extracts built-in and external initramfs/initrd images into rootfs, manages optional initrd retention/freeing, exposes retained initrd data through sysfs, and exports `wait_for_initramfs()` so later boot code can synchronize with asynchronous extraction.

## Important APIs, Types, And Functions
- `unpack_to_rootfs(char *buf, unsigned long len)` is the central parser/decompressor. It accepts raw `newc` cpio streams or compressed streams detected by `decompress_method()`, writes files into rootfs, and returns `NULL` on success or a static error string.
- `reserve_initrd_mem()` validates and reserves physical initrd memory with memblock, converts it to virtual `initrd_start/initrd_end`, and disables invalid or overlapping initrd regions.
- `populate_rootfs()` is registered with `rootfs_initcall()` and schedules `do_populate_rootfs()` on an exclusive async domain unless `initramfs_async=false`.
- `wait_for_initramfs()` synchronizes against the async cookie and is exported with GPL visibility.
- `find_link()/free_hash()` track cpio hardlinks by `(major, minor, ino, file type)`.
- `do_name()`, `do_copy()`, `do_symlink()`, `do_header()`, and `flush_buffer()` are the finite-state-machine actions used while unpacking.

## Control Flow
The cpio extractor operates as a finite-state machine over `Start`, `Collect`, `GotHeader`, `SkipIt`, `GotName`, `CopyFile`, `GotSymlink`, and `Reset`. `write_buffer()` repeatedly invokes the current action until progress stops. `flush_buffer()` feeds decompressed bytes into the same state machine and validates archive boundaries.

`unpack_to_rootfs()` initializes transient buffers, then loops over the input. If the current location looks like an aligned `newc` header it parses directly; if it sees zero padding it skips it; otherwise it attempts decompression and feeds output through `flush_buffer()`. Directory mtimes and hardlink hash cleanup are finalized after the stream.

Rootfs population first unpacks the built-in archive, panicking on failure. If an external initrd exists and `CONFIG_INITRAMFS_FORCE` is not set, it tries to unpack it as initramfs. When that fails and block RAM support exists, `populate_initrd_image()` writes `/initrd.image`; otherwise it logs failure. The routine then calls `security_initramfs_populated()`, frees or retains initrd memory, resets global initrd pointers, and flushes delayed `fput()` work.

## State And Persistence
Most parser state is `__initdata`: current header fields, checksum state, byte offsets, parser buffers, hardlink table, pending directory mtimes, `message`, and async cookie. Persistent effects are filesystem objects created in rootfs, optional `/sys/firmware/initrd` binary attribute when `retain_initrd`/`keepinitrd` is used, and cleared `initrd_start/initrd_end` after extraction. If `CONFIG_INITRAMFS_PRESERVE_MTIME` is enabled, file and directory mtimes are restored from archive metadata; otherwise normal creation times apply.

## Dependencies And Integration Points
The file depends on VFS/init syscall wrappers (`init_mkdir`, `init_mknod`, `init_link`, `init_symlink`, `init_utimes`, `kernel_write`), decompressor infrastructure, memblock, initrd globals, kexec crash reservation, sysfs firmware kobject, security hooks, async init domains, and boot parameters (`retain_initrd`, `keepinitrd`, `initramfs_async=`). `kernel_init_freeable()` in `init/main.c` calls `wait_for_initramfs()` before opening `/dev/console` or running init.

## Risks And Edge Cases
Archive parsing is sensitive to padding, `PATH_MAX`, missing NUL terminators, checksum mismatches, and malformed compression boundaries. Hardlink metadata can leak if not freed after archives without a trailer; this file explicitly frees it after unpacking. `mtime` is parsed into `time64_t` from old cpio fields with a noted y2106 limit. Bad writes can leave partially created files. Retaining initrd exposes raw boot image bytes through sysfs and requires the reserved memory to remain valid.

## Test Signals
`initramfs_test.c` directly targets `unpack_to_rootfs()` for regular files, directories, data integrity, checksum handling, hardlinks without trailers, many entries, padded filenames, path-length boundaries, and missing filename NUL termination. Boot integration is also exercised indirectly by initcall ordering and by systems booting with/without external initrd.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/initramfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/initramfs_internal.h -->
# sources/distributed-fs/ceph-client/init/initramfs_internal.h

## Purpose
This small internal header exposes the initramfs extractor to nearby init code and tests without making it a broad public kernel API.

## Important APIs, Types, And Functions
- `char *unpack_to_rootfs(char *buf, unsigned long len);` declares the extractor implemented by `initramfs.c`.
- `CPIO_HDRLEN` defines the fixed 110-byte `newc` cpio header length used by the extractor and its KUnit tests.

## Control Flow
There is no runtime logic. Including files compile against the extractor contract and agree on header sizing.

## State And Persistence
No state is stored here. The persistence behavior belongs to `initramfs.c`, which creates rootfs entries.

## Dependencies And Integration Points
`initramfs_test.c` includes this header to build synthetic cpio records with the same header length as production code. `initramfs.c` includes it for its exported internal prototype.

## Risks And Edge Cases
Changing `CPIO_HDRLEN` would desynchronize archive packing/parsing assumptions. Exposing `unpack_to_rootfs()` here is intentionally narrow; making it more public would invite use outside early init constraints.

## Test Signals
The header is covered when `initramfs_test.c` compiles and when synthetic cpio streams align with production parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/initramfs_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/initramfs_test.c -->
# sources/distributed-fs/ceph-client/init/initramfs_test.c

## Purpose
This KUnit suite validates the initramfs `newc` cpio extractor. It builds in-memory cpio streams, calls `unpack_to_rootfs()`, and verifies resulting filesystem objects or expected parse failures.

## Important APIs, Types, And Functions
- `struct initramfs_test_cpio` models the 13 `newc` header fields plus filename and data pointers.
- `fill_cpio()` serializes one or more test records into a properly padded cpio stream.
- Test cases include `initramfs_test_extract`, `initramfs_test_fname_overrun`, `initramfs_test_data`, `initramfs_test_csum`, `initramfs_test_hardlink`, `initramfs_test_many`, `initramfs_test_fname_pad`, and `initramfs_test_fname_path_max`.
- `kunit_test_init_section_suites()` registers the suite for init-section execution while keeping case metadata in `__refdata`.

## Control Flow
Each case allocates a source buffer, fills records, calls `unpack_to_rootfs()`, then checks results with init-time VFS helpers such as `init_stat`, `filp_open`, `kernel_read`, `init_unlink`, and `init_rmdir`. Cleanup removes created test files/directories.

## State And Persistence
Tests intentionally mutate rootfs by creating files, directories, and hardlinks, then remove them. Some negative tests verify that malformed records do not create visible files. The checksum failure test documents that a bad checksum can leave the file whose payload was already written while aborting later entries.

## Dependencies And Integration Points
The suite depends on KUnit, `initramfs_internal.h`, init syscall wrappers, VFS file operations, and timekeeping. It is part of early init test execution, not normal userspace-driven testing.

## Risks And Edge Cases
The suite covers historical bug-prone areas: filenames lacking NUL terminators, archive padding that permits data alignment, `PATH_MAX` acceptance/skipping, missing trailer cleanup for hardlink hash state, and checksum validation. It relies on writable rootfs state and must carefully unlink artifacts to avoid contaminating later tests.

## Test Signals
Passing this suite indicates the extractor handles normal file/dir extraction, metadata ownership/mode/mtime expectations, file contents, checksums, hardlinks, scalability across many records, padded filename fields, and path-length rejection. Failures provide direct evidence of parser or VFS integration regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/initramfs_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/main.c -->
# sources/distributed-fs/ceph-client/init/main.c

## Purpose
`init/main.c` is the kernel boot orchestration file. It implements `start_kernel()`, command-line and bootconfig parsing, initcall execution, transition from early boot to normal scheduling, rootfs readiness, init memory freeing, and final execution of PID 1.

## Important APIs, Types, And Functions
- `start_kernel()` is the main entry after architecture setup and runs the global initialization sequence.
- `rest_init()` creates the initial userspace-thread wrapper (`kernel_init`) and `kthreadd`, then enters CPU idle.
- `kernel_init()` waits for `kthreadd`, runs `kernel_init_freeable()`, frees init memory, marks kernel text/data read-only, finalizes PTI, and executes init.
- `kernel_init_freeable()` enables normal GFP masks, initializes SMP/workqueues/async/initcalls/KUnit, waits for initramfs, opens console, prepares the root namespace if needed, and loads integrity keys.
- `parse_early_param()`, `unknown_bootoption()`, `setup_boot_config()`, and `setup_command_line()` build the kernel and init argument vectors.
- `do_one_initcall()`, `do_initcall_level()`, and `do_initcalls()` invoke built-in initcall levels with tracing, blacklist handling, and sanity checks.

## Control Flow
Boot begins with interrupts disabled, early CPU and memory structures initialized, bootconfig and command lines prepared, early parameters parsed, and unknown arguments routed to init or environment arrays. `start_kernel()` then initializes allocators, tracing, scheduler, RCU, IRQ/timer/timekeeping/randomness, console, lockdep, namespaces, VFS, cgroups, networking namespaces, and other core subsystems before calling `rest_init()`.

`rest_init()` starts `kernel_init` as PID 1, pins it to the boot CPU until scheduler SMP setup, starts `kthreadd`, changes `system_state` to scheduling, and enters idle. `kernel_init()` performs late boot work, frees init-only memory, switches to `SYSTEM_RUNNING`, and tries init candidates in order: `rdinit`/`/init`, explicit `init=`, `CONFIG_DEFAULT_INIT`, `/sbin/init`, `/etc/init`, `/bin/init`, `/bin/sh`.

## State And Persistence
Global boot state includes `system_state`, `early_boot_irqs_disabled`, command-line buffers, init argv/envp arrays, `execute_command`, `ramdisk_execute_command`, bootconfig data, static key initialization, `reset_devices`, `loops_per_jiffy`, and `rodata_enabled`. It persists `/proc/cmdline` data in `saved_command_line`, exports `system_state`, `reset_devices`, and `static_key_initialized`, and frees init sections after async init work completes.

## Dependencies And Integration Points
This file integrates nearly every core subsystem: architecture setup, memblock, scheduler, workqueues, RCU/SRCU, IRQ/timers/timekeeping, VFS, namespace, cgroup, security, random, ACPI, SMP, KUnit, initramfs, module/initcall infrastructure, tracing, proc/sysfs, and exec. It calls `wait_for_initramfs()` from `initramfs.c` before console/root namespace use.

## Risks And Edge Cases
Ordering is the primary risk. Interrupt state, allocator availability, static keys, security initialization, bootconfig removal from initrd, early parameter parsing, initcall side effects, and async init completion all have strict sequencing. Argument arrays can overflow and panic later. `do_one_initcall()` repairs preemption/IRQ imbalances but reports them. Incorrect initramfs waiting can break `/dev/console` or early userspace discovery.

## Test Signals
Signals include successful system boot, initcall debug traces, KUnit execution from `kunit_run_all_tests()`, bootconfig parse logs, unknown boot option notices, and failure modes such as explicit panic on missing working init. Kernel selftests and platform boot matrices are the real coverage for this file because its behavior spans subsystem ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/noinitramfs.c -->
# sources/distributed-fs/ceph-client/init/noinitramfs.c

## Purpose
`noinitramfs.c` creates a minimal default rootfs for builds or boots without initramfs extraction. It ensures `/dev/console` and `/root` exist early enough for the rest of init to proceed.

## Important APIs, Types, And Functions
- `default_rootfs()` enables usermode helpers, creates `/dev`, creates `/dev/console` as character device major 5 minor 1 with owner read/write permissions, and creates `/root`.
- `rootfs_initcall(default_rootfs)` schedules it in the rootfs initcall stage.

## Control Flow
The initcall performs three filesystem operations in order. Any failure jumps to a warning path and returns the negative error.

## State And Persistence
Persistent effects are rootfs directories and the console device node. No private state is retained.

## Dependencies And Integration Points
It depends on init syscall wrappers, `new_encode_dev(MKDEV(5,1))`, rootfs initcall ordering, and `usermodehelper_enable()`. `kernel_init_freeable()` later opens `/dev/console`, so this fallback complements the initramfs path.

## Risks And Edge Cases
If rootfs is not writable or device creation fails, later console setup may warn or fail. The function is intentionally minimal and does not populate a complete userspace.

## Test Signals
Boots without an initramfs should show a usable `/dev/console` and `/root`. The warning `Failed to create a rootfs` is the direct failure signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/noinitramfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/version-timestamp.c -->
# sources/distributed-fs/ceph-client/init/version-timestamp.c

## Purpose
This file defines build-timestamp-sensitive kernel identity data: the initial UTS namespace and the printable Linux banner. It is included by `version.c` and can be regenerated late in the build.

## Important APIs, Types, And Functions
- `struct uts_namespace init_uts_ns` initializes namespace common data, sysname, nodename, release, version, machine, domainname, and `init_user_ns`.
- `const char linux_banner[]` formats `UTS_RELEASE`, compile user/host/compiler, and `UTS_VERSION`.

## Control Flow
There is no executable control flow. Initialization happens through static data.

## State And Persistence
The UTS namespace data persists for the life of the kernel and backs system identity visible through utsname/proc paths. `linux_banner` is printed during early boot by `start_kernel()`.

## Dependencies And Integration Points
It depends on generated headers `compile.h` and `utsrelease.h`, UTS constants, namespace helpers, and `init_user_ns`. `version.c` uses weak definitions first, then includes this file for the final strong definitions.

## Risks And Edge Cases
The comment warns fixed strings should not be touched because build tooling may depend on exact banner formatting. Incorrect generated values affect uname/proc identity and reproducibility metadata.

## Test Signals
Boot logs showing the expected Linux banner and `uname` reporting expected release/version data are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/version-timestamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/version.c -->
# sources/distributed-fs/ceph-client/init/version.c

## Purpose
`version.c` provides kernel build identity strings, build notes, and early hostname override support. It wraps final timestamp-sensitive data from `version-timestamp.c`.

## Important APIs, Types, And Functions
- `early_hostname()` handles the `hostname=` early parameter by copying into `init_uts_ns.name.nodename` with truncation warning.
- `linux_proc_banner` defines `/proc/version`-style formatting.
- `BUILD_SALT` and `BUILD_LTO_INFO` emit build metadata notes.
- Weak `init_uts_ns` and `linux_banner` definitions allow a late build step to replace them; including `version-timestamp.c` supplies strong final definitions.
- `EXPORT_SYMBOL_GPL(init_uts_ns)` exposes the initial UTS namespace to GPL code.

## Control Flow
The only executable path is early parameter parsing for hostname. Static data provides banners and namespace defaults.

## State And Persistence
`init_uts_ns` persists globally. `hostname=` can mutate the initial nodename during early boot before normal userspace hostname tools run.

## Dependencies And Integration Points
It depends on generated compile metadata, printk, UTS namespace structures, proc namespace support, early parameter infrastructure, and build-salt/LTO note macros. `start_kernel()` prints `linux_banner`.

## Risks And Edge Cases
Overlong `hostname=` values are truncated with warning. Build system expectations around weak/strong symbol replacement and banner string layout are fragile.

## Test Signals
Booting with `hostname=` should update the initial nodename. `/proc/version`, boot banner output, and exported `init_uts_ns` consumers should reflect generated compile metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/init/version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/Kconfig -->
# sources/distributed-fs/ceph-client/io_uring/Kconfig

## Purpose
This Kconfig fragment enables optional io_uring features based on dependency availability.

## Important APIs, Types, And Functions
- `IO_URING_ZCRX` defaults on when `IO_URING`, `PAGE_POOL`, `INET`, and `NET_RX_BUSY_POLL` are present.
- `IO_URING_BPF` defaults on when `BPF` and `NET` are present.
- `IO_URING_BPF_OPS` defaults on when `IO_URING`, `BPF_SYSCALL`, `BPF_JIT`, and `DEBUG_INFO_BTF` are present.

## Control Flow
There is no runtime flow. These symbols drive compilation in the Makefile and conditional code paths.

## State And Persistence
Configuration state persists in the kernel build and determines which object files and APIs exist.

## Dependencies And Integration Points
The symbols map to `zcrx.o`, `bpf_filter.o`, and `bpf-ops.o` in the io_uring Makefile. Headers provide stubs when optional features are disabled.

## Risks And Edge Cases
Because all three are `def_bool y`, enabling dependencies implicitly enables the feature. Incorrect dependencies could expose compile failures or runtime APIs in unsupported environments.

## Test Signals
Build matrix coverage with and without BPF, BTF/JIT, networking, busy-poll, and page-pool support validates these dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/Makefile -->
# sources/distributed-fs/ceph-client/io_uring/Makefile

## Purpose
The Makefile defines the io_uring object composition for core support and optional feature objects.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_IO_URING)` builds the core aggregate with files such as `io_uring.o`, `opdef.o`, `rsrc.o`, `filetable.o`, `rw.o`, `poll.o`, `eventfd.o`, `fs.o`, `cancel.o`, `register.o`, `alloc_cache.o`, and `loop.o`.
- Optional objects include `io-wq.o`, `futex.o`, `epoll.o`, `napi.o`, `net.o`, `cmd_net.o`, `fdinfo.o`, `mock_file.o`, `bpf_filter.o`, and `bpf-ops.o`.
- `CONFIG_GCOV_PROFILE_URING` can enable GCOV profiling for this directory.

## Control Flow
Build-time only. Object inclusion follows Kconfig symbols.

## State And Persistence
The resulting kernel image/module includes only selected object files. No runtime state lives here.

## Dependencies And Integration Points
This file binds Kconfig to implementation. Many files in this research set rely on being compiled only when their subsystem dependencies exist, while headers provide stubs for callers in disabled configurations.

## Risks And Edge Cases
Duplicated or missing objects can create link failures or silently omit operations. The core list includes many operation adapters; additions to `opdef` often need corresponding Makefile updates.

## Test Signals
Successful allmodconfig/allyesconfig/minimal builds and io_uring operation tests across feature combinations validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/advise.c -->
# sources/distributed-fs/ceph-client/io_uring/advise.c

## Purpose
`advise.c` implements io_uring operations for `madvise` and `fadvise`, translating SQE fields into VM and VFS advisory calls.

## Important APIs, Types, And Functions
- `struct io_madvise` stores address, length, and advice.
- `struct io_fadvise` stores file, offset, length, and advice.
- `io_madvise_prep()` validates unused SQE fields, reads `addr`, `off`/`len`, and `fadvise_advice`, and forces async execution.
- `io_madvise()` calls `do_madvise(current->mm, ...)`.
- `io_fadvise_prep()` parses offset/length/advice and forces async for advice values that may block.
- `io_fadvise()` calls `vfs_fadvise(req->file, ...)`.

## Control Flow
Preparation copies SQE values into per-request command storage. Execution warns if a force-async operation somehow arrives in nonblocking issue mode, invokes the backing syscall helper, sets failure state for negative `fadvise` results, and completes through `IOU_COMPLETE`.

## State And Persistence
No persistent io_uring state is kept. Effects are advisory VM or file-cache state managed by MM/VFS.

## Dependencies And Integration Points
The file depends on io_uring request helpers, SQE layout, `CONFIG_ADVISE_SYSCALLS`, `CONFIG_MMU`, `do_madvise`, and `vfs_fadvise`. `advise.h` exposes operation hooks to the opcode table.

## Risks And Edge Cases
Unsupported MM/advice configurations return `-EOPNOTSUPP`. Length can be sourced from either `off`/`addr` or fallback `len`, so SQE field interpretation must match userspace ABI. Blocking advice must not execute from a nonblocking path.

## Test Signals
io_uring tests for `IORING_OP_MADVISE`/`FADVISE` should cover invalid reserved fields, unsupported configs, async forcing, and result parity with direct syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/advise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/advise.h -->
# sources/distributed-fs/ceph-client/io_uring/advise.h

## Purpose
This header declares io_uring madvise/fadvise prep and issue handlers for use by the operation definition table.

## Important APIs, Types, And Functions
- `io_madvise_prep()` and `io_madvise()`.
- `io_fadvise_prep()` and `io_fadvise()`.

## Control Flow
No local control flow. The declarations connect `opdef` dispatch to `advise.c`.

## State And Persistence
No state is defined here.

## Dependencies And Integration Points
It depends on forward-visible `struct io_kiocb` and `struct io_uring_sqe` declarations from including context. It is part of the io_uring opcode integration surface.

## Risks And Edge Cases
Prototype drift with `advise.c` or `opdef` would cause build failures or operation dispatch mismatch.

## Test Signals
Build coverage and successful dispatch of advise operations validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/advise.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/alloc_cache.c -->
# sources/distributed-fs/ceph-client/io_uring/alloc_cache.c

## Purpose
`alloc_cache.c` provides a small reusable object cache for io_uring subsystems that frequently allocate per-request auxiliary objects, notably futex wait data.

## Important APIs, Types, And Functions
- `io_alloc_cache_init()` allocates the pointer array, initializes counts and element sizing, and returns `false` on success.
- `io_alloc_cache_free()` drains cached entries through a caller-provided free function and frees the pointer array.
- `io_cache_alloc_new()` allocates a new element with `kmalloc()` and clears configured initial bytes.

## Control Flow
Initialization allocates an array of object pointers. Allocation paths in the header try cached entries first, then call `io_cache_alloc_new()`. Freeing drains all cached objects and clears `entries`.

## State And Persistence
State is stored in `struct io_alloc_cache`: `entries`, `nr_cached`, `max_cached`, `elem_size`, and `init_clear`. Cached objects persist until reused or the owning ring frees the cache.

## Dependencies And Integration Points
It depends on `kvmalloc_array`, `kvfree`, and the inline helpers in `alloc_cache.h`. `futex.c` uses it for `struct io_futex_data`.

## Risks And Edge Cases
The initializer’s false-on-success convention is easy to misuse. Cache sizing must match actual object size and any required zeroed prefix. Draining uses a supplied free function; passing the wrong function would corrupt memory ownership.

## Test Signals
Futex wait stress tests, KASAN, and allocation-failure injection can validate cache reuse, cleanup, and error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/alloc_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/alloc_cache.h -->
# sources/distributed-fs/ceph-client/io_uring/alloc_cache.h

## Purpose
The header defines inline fast paths for the io_uring allocation cache and the hard cap on cached entries.

## Important APIs, Types, And Functions
- `IO_ALLOC_CACHE_MAX` caps generic caches at 128 entries.
- `io_alloc_cache_put()` poisons and stores an object when capacity exists.
- `io_alloc_cache_get()` pops an object, unpoisons it for KASAN, and clears the configured prefix under KASAN.
- `io_cache_alloc()` and `io_cache_free()` are the high-level allocate/free helpers.

## Control Flow
`io_cache_alloc()` returns a cached object if available, otherwise allocates a new one. `io_cache_free()` tries to cache the object, falling back to `kvfree()`.

## State And Persistence
The object stack is LIFO through `entries[nr_cached]`. Cached objects remain owned by the cache until reused or drained.

## Dependencies And Integration Points
It depends on `struct io_alloc_cache` from `io_uring_types.h`, KASAN mempool hooks, and `alloc_cache.c` for slow paths. Subsystems using it must initialize and free caches at ring lifetime boundaries.

## Risks And Edge Cases
KASAN poisoning failure forces direct free. Inline cache operations are not internally locked, so callers must use them under their own serialization if shared. `init_clear` must be enough to prevent stale fields from leaking between requests.

## Test Signals
KASAN-enabled io_uring stress, futex wait cancellation, and ring teardown tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/alloc_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/bpf-ops.c -->
# sources/distributed-fs/ceph-client/io_uring/bpf-ops.c

## Purpose
`bpf-ops.c` registers BPF struct-ops support for io_uring loop customization and exposes BPF kfuncs that can submit SQEs or access mapped io_uring regions under verifier constraints.

## Important APIs, Types, And Functions
- `bpf_io_uring_submit_sqes()` kfunc calls `io_submit_sqes(ctx, nr)`.
- `bpf_io_uring_get_region()` kfunc returns validated pointers to parameter, CQ, or SQ mapped regions and asserts `ctx->uring_lock`.
- `struct io_uring_bpf_ops` instances are installed through BPF struct_ops registration.
- `io_install_bpf()` validates ring setup flags and installs `ctx->bpf_ops` and `ctx->loop_step`.
- `io_unregister_bpf_ops()` safely ejects installed ops during ring teardown.
- `io_uring_bpf_init()` registers the struct_ops type at initcall time.

## Control Flow
BPF subsystem initialization finds the BTF type for `iou_loop_params`, registers kfunc IDs, and registers struct_ops. Registration from userspace resolves a ring fd, takes a global control mutex and the ring lock, then installs ops if the ring is defer-taskrun and not SQPOLL/IOPOLL. Unregistration or ring teardown clears the ops with the same lock ordering.

## State And Persistence
Global state includes `io_bpf_ctrl_mutex` and cached `loop_params_type`. Per-ring state is `ctx->bpf_ops` and `ctx->loop_step`; the BPF ops object stores `ring_fd` and `priv`.

## Dependencies And Integration Points
The file depends on BPF verifier, BTF, struct_ops, io_uring registration/memmap/loop internals, and `DEBUG_INFO_BTF`/JIT/syscall Kconfig dependencies. It integrates with ring lifetime cleanup through `io_unregister_bpf_ops()`.

## Risks And Edge Cases
Lock ordering between the global BPF mutex and `uring_lock` is critical. Region pointer exposure must remain bounded by `io_region_size()`. Verifier access only permits reads from expected context arguments and selected scalar fields. Rings using SQPOLL or IOPOLL are explicitly unsupported.

## Test Signals
BPF struct_ops registration tests should cover valid/invalid ring fds, unsupported ring flags, kfunc verifier access, region size rejection, and ring teardown while a BPF link exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/bpf-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/bpf-ops.h -->
# sources/distributed-fs/ceph-client/io_uring/bpf-ops.h

## Purpose
This header defines the BPF struct-ops interface shape and mapped region identifiers for io_uring BPF operations.

## Important APIs, Types, And Functions
- Region enum values `IOU_REGION_MEM`, `IOU_REGION_CQ`, and `IOU_REGION_SQ`.
- `struct io_uring_bpf_ops` with `loop_step`, `ring_fd`, and private `priv`.
- `io_unregister_bpf_ops()` declaration or no-op stub when the feature is disabled.

## Control Flow
No runtime logic except the disabled-feature stub.

## State And Persistence
The struct stores per-registered-link state. `priv` points back to the owning ring while installed.

## Dependencies And Integration Points
It depends on `io_uring_types.h` and is used by ring teardown and BPF registration code.

## Risks And Edge Cases
ABI-sensitive struct layout must match BTF expectations. The no-op stub must remain safe for builds without `CONFIG_IO_URING_BPF_OPS`.

## Test Signals
Builds with and without BPF ops enabled validate stubs/prototypes; BPF struct_ops tests validate layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/bpf-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/bpf_filter.c -->
# sources/distributed-fs/ceph-client/io_uring/bpf_filter.c

## Purpose
`bpf_filter.c` implements classic BPF-based filtering for io_uring request submission. Filters are registered per opcode and can allow or deny requests based on a restricted context populated from the request.

## Important APIs, Types, And Functions
- `struct io_bpf_filter` links a refcounted `bpf_prog` list per opcode.
- `__io_uring_run_bpf_filters()` runs all filters for `req->opcode`; any zero result denies with `-EACCES`.
- `io_register_bpf_filter()` imports user registration data, creates a BPF program, copy-on-writes cloned filter sets if needed, and installs the filter.
- `io_put_bpf_filters()` and `io_free_bpf_filters()` manage RCU/refcounted cleanup.
- `io_bpf_filter_clone()` shares filters into cloned restrictions with COW.
- `io_uring_check_cbpf_filter()` validates and rewrites a safe cBPF instruction subset.

## Control Flow
Registration validates command type, flags, opcode, reserved fields, filter length, and expected per-opcode PDU size. It then creates a BPF program from user instructions, allocates or COWs the filter table, prepends the new filter for the opcode, and optionally marks all unregistered opcodes with `dummy_filter` to deny the rest. Runtime filtering does a fast RCU pointer check, populates `io_uring_bpf_ctx`, then runs each filter pinned on CPU until all allow or one denies.

## State And Persistence
Filter state is stored in `struct io_restriction` through `bpf_filters` and `bpf_filters_cow`. The filter table is an RCU array indexed by opcode; individual filter lists are refcounted and immutable except for prepending. `dummy_filter` is a static sentinel for deny-all slots.

## Dependencies And Integration Points
The file depends on io_uring opcode definitions (`io_issue_defs`), operation-specific filter population callbacks, classic BPF creation/validation, RCU, spinlocks, and restriction registration paths. The header provides disabled stubs when `CONFIG_IO_URING_BPF` is off.

## Risks And Edge Cases
Verifier safety is central: only aligned loads from the bounded io_uring context and selected ALU/jump operations are allowed. COW and refcount handling must avoid use-after-free while cloned restrictions are modified. `DENY_REST` changes default behavior for all unspecified opcodes, which can surprise callers if combined with later filter additions.

## Test Signals
Tests should cover allowed/denied opcodes, stacked filters, invalid cBPF instructions, strict and non-strict PDU size handling, cloned restrictions with COW, `DENY_REST`, and RCU teardown under concurrent submissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/bpf_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/bpf_filter.h -->
# sources/distributed-fs/ceph-client/io_uring/bpf_filter.h

## Purpose
The header exposes BPF filter registration, execution, cloning, and cleanup to io_uring restriction and submission paths, with stubs for disabled builds.

## Important APIs, Types, And Functions
- `io_uring_run_bpf_filters()` inline wrapper returns success when no filter table exists.
- `__io_uring_run_bpf_filters()`, `io_register_bpf_filter()`, `io_put_bpf_filters()`, and `io_bpf_filter_clone()` are available under `CONFIG_IO_URING_BPF`.
- Disabled builds reject registration with `-EINVAL` and make execution/cleanup no-ops.

## Control Flow
The enabled wrapper checks whether `filters` is non-NULL before calling the full runner. Disabled stubs avoid conditional compilation at call sites.

## State And Persistence
No state is defined here. It references RCU filter arrays owned by restriction state.

## Dependencies And Integration Points
It includes the UAPI BPF filter definition and is used by request initialization/filtering and restriction registration code.

## Risks And Edge Cases
Callers must pass opcode-validated requests because the implementation indexes by `req->opcode`. Stub behavior must preserve semantics for kernels without BPF filter support.

## Test Signals
Builds with `CONFIG_IO_URING_BPF` off validate stubs; enabled runtime filter tests validate wrapper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/bpf_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/cancel.c -->
# sources/distributed-fs/ceph-client/io_uring/cancel.c

## Purpose
`cancel.c` implements io_uring cancellation by userdata, file, opcode, sequence, task, ring, and exit state. It coordinates cancellation across io-wq, poll, waitid, futex, timeout, deferred, uring_cmd, iopoll, and task-work paths.

## Important APIs, Types, And Functions
- `io_async_cancel_prep()` parses `IORING_OP_ASYNC_CANCEL` SQEs.
- `io_async_cancel()` issues async cancellation and completes the cancel request.
- `io_sync_cancel()` implements registered synchronous cancel with optional timeout.
- `io_cancel_req_match()` centralizes match criteria.
- `io_try_cancel()` attempts io-wq, poll, waitid, futex, and timeout cancellation.
- `io_cancel_remove()` and `io_cancel_remove_all()` remove requests from subsystem hlist queues using subsystem-specific callbacks.
- `io_uring_try_cancel_requests()` and `io_uring_cancel_generic()` drive broad cancellation during ring teardown, task exit, or exec.

## Control Flow
Async cancel prep validates reserved fields and mutually exclusive flags, then records userdata, fd, or opcode. Execution builds `io_cancel_data`, optionally resolves a normal or fixed file, and calls `__io_async_cancel()`. That routine first tries the current task context, then scans all task contexts attached to the ring under `ctx->tctx_lock` for io-wq work.

Synchronous cancel copies `io_uring_sync_cancel_reg`, validates pads/flags, resolves file references, tries cancellation, and if work is already running waits on `ctx->cq_wait` while repeatedly retrying until completion, timeout, signal/task-work error, or no matching request remains.

Exit/teardown cancellation sets `in_cancel`, starts io-wq exit, drops task context refs, iterates rings or SQPOLL contexts, drains local work, cancels deferred/poll/waitid/futex/uring_cmd/timeouts, and waits until inflight counters reach zero before cleaning or freeing task context.

## State And Persistence
Cancellation uses `ctx->cancel_seq` to avoid repeatedly matching the same request during `ALL` scans, request `cancel_seq_set/work.cancel_seq`, per-task inflight counters, `tctx->in_cancel`, wait queues, subsystem request lists, and `ctx->uring_lock`/`completion_lock`/`timeout_lock`. It changes request flags to canceled, posts failed completions, or signals running workers.

## Dependencies And Integration Points
The file depends on io-wq, task context tracking, fixed-file lookup, poll, waitid, futex, timeout, SQPOLL, uring_cmd, wait/local task work, and ring locking. It is a shared utility used by operation cancel, ring release, task exit, and exec cleanup.

## Risks And Edge Cases
Concurrency and ownership dominate risk. Running io-wq work may only be signaled and returns `-EALREADY`. Fixed files must be revalidated when locks are dropped. Linked timeouts require `timeout_lock` for safe matching. Broad cancellation must not deadlock with deferred task-run or SQPOLL ownership. Sequence matching must prevent infinite counting during cancel-all loops.

## Test Signals
io_uring cancellation tests should cover cancel by userdata, fd, fixed fd, opcode, any/all, running vs pending work, poll/timeouts/futex/waitid/uring_cmd requests, sync cancel timeout, task exit, exec, SQPOLL, and deferred task-run rings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/cancel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/cancel.h -->
# sources/distributed-fs/ceph-client/io_uring/cancel.h

## Purpose
The header defines shared cancellation data and APIs used across io_uring subsystems.

## Important APIs, Types, And Functions
- `struct io_cancel_data` carries context, userdata, file, opcode, flags, and sequence.
- Declarations cover async/sync cancel, try-cancel, match helpers, list removal, ring/request teardown, and generic task cancellation.
- `io_cancel_match_sequence()` marks requests with a sequence to avoid reprocessing in `ALL` cancellation scans.

## Control Flow
The inline sequence helper returns true if the request already saw the current cancel sequence, otherwise records it and returns false.

## State And Persistence
It references per-request `cancel_seq_set` and `work.cancel_seq`, and per-cancel `seq` from `ctx->cancel_seq`.

## Dependencies And Integration Points
It includes `io_uring_types.h` and is consumed by poll, waitid, futex, uring_cmd, io-wq cancellation, and ring teardown code.

## Risks And Edge Cases
The sequence helper mutates request state during matching; callers must only use it in contexts where request lifetime is protected. Prototype drift would affect many cancellation-capable subsystems.

## Test Signals
Cancel-all tests that would otherwise double count or loop over the same request validate sequence matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/cancel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/cmd_net.c -->
# sources/distributed-fs/ceph-client/io_uring/cmd_net.c

## Purpose
`cmd_net.c` implements socket-specific io_uring command operations: socket queue ioctls, getsockopt/setsockopt, TX timestamp multishot CQEs, and getsockname/peername support.

## Important APIs, Types, And Functions
- `io_uring_cmd_sock()` dispatches `cmd->cmd_op` to socket command handlers and is exported GPL.
- `io_uring_cmd_get_sock_ioctl()` calls protocol `ioctl` for `SIOCINQ`/`SIOCOUTQ`.
- `io_uring_cmd_getsockopt()` and `io_uring_cmd_setsockopt()` bridge SQE opt fields into socket option helpers.
- `io_uring_cmd_timestamp()` polls the socket error queue and posts CQE32 timestamp records.
- `io_uring_cmd_getsockname()` validates SQE fields and calls `do_getsockname()` for local or peer addresses.

## Control Flow
The dispatcher uses the socket from `cmd->file->private_data`. Timestamp handling requires CQE32, arms multishot poll for `EPOLLERR`, drains timestamp-only skbs from `sk_error_queue`, posts one CQE pair per timestamp, and requeues unposted skbs.

## State And Persistence
No persistent module state is stored. Operations can consume entries from a socket error queue, return socket option values to user memory, and post multishot CQEs.

## Dependencies And Integration Points
The file depends on net socket internals, errqueue timestamp helpers, io_uring command infrastructure, multishot CQE32 posting, socket UAPI command opcodes, and compat handling via issue flags.

## Risks And Edge Cases
TX timestamp requires CQE32 and rejects payload skbs. Error-queue locking and requeueing must preserve skbs when CQE posting stops. Only `SOL_SOCKET` getsockopt is supported here; unsupported protocol/levels return `-EOPNOTSUPP`. SQE padding validation prevents ABI ambiguity.

## Test Signals
Socket io_uring command tests should cover queue depth ioctls, getsockopt/setsockopt parity, timestamp multishot delivery with CQE32, requeue behavior on partial posting, getsockname/peername, compat mode, and invalid SQE fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/cmd_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/epoll.c -->
# sources/distributed-fs/ceph-client/io_uring/epoll.c

## Purpose
`epoll.c` provides io_uring operations for `epoll_ctl` and `epoll_wait`-style event delivery.

## Important APIs, Types, And Functions
- `struct io_epoll` stores epoll fd, operation, target fd, and optional event.
- `struct io_epoll_wait` stores max events and userspace event array.
- `io_epoll_ctl_prep()` parses the SQE and copies an event from userspace when the operation needs one.
- `io_epoll_ctl()` calls `do_epoll_ctl()`.
- `io_epoll_wait_prep()` parses wait output buffer and count.
- `io_epoll_wait()` calls `epoll_sendevents()` on `req->file`.

## Control Flow
Prep rejects unsupported SQE fields. `epoll_ctl` can be issued nonblocking; if `do_epoll_ctl()` returns `-EAGAIN` under nonblocking issue flags, the request is retried later. `epoll_wait` returns `-EAGAIN` when no events are sent so io_uring can arm/retry instead of completing with zero.

## State And Persistence
Persistent effects occur in the target epoll instance through `do_epoll_ctl()`. Wait operations copy events to userspace and otherwise keep no local state.

## Dependencies And Integration Points
The file depends on eventpoll internals, uaccess, io_uring request helpers, and `CONFIG_EPOLL` object inclusion. `epoll.h` exposes handlers to `opdef`.

## Risks And Edge Cases
Userspace event copy can fault. Nonblocking `epoll_ctl` needs careful `-EAGAIN` propagation. `epoll_wait` must use the request file as the epoll file and returns retry semantics for empty results.

## Test Signals
Tests should cover add/mod/del control operations, invalid event pointers, nonblocking retry paths, wait returning events, and empty wait producing retry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/epoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/epoll.h -->
# sources/distributed-fs/ceph-client/io_uring/epoll.h

## Purpose
This header declares io_uring epoll operation handlers when epoll support is compiled in.

## Important APIs, Types, And Functions
- `io_epoll_ctl_prep()` and `io_epoll_ctl()`.
- `io_epoll_wait_prep()` and `io_epoll_wait()`.

## Control Flow
No runtime flow is defined. Declarations are guarded by `CONFIG_EPOLL`.

## State And Persistence
No state is defined here.

## Dependencies And Integration Points
It connects epoll operation implementations to the io_uring opcode table in builds with epoll support.

## Risks And Edge Cases
Callers must not reference these prototypes without matching config guards in builds where `CONFIG_EPOLL` is off.

## Test Signals
Compile coverage with `CONFIG_EPOLL=y/n` and runtime epoll operation tests validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/epoll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/eventfd.c -->
# sources/distributed-fs/ceph-client/io_uring/eventfd.c

## Purpose
`eventfd.c` manages io_uring completion eventfd registration, signaling, and unregistering.

## Important APIs, Types, And Functions
- `struct io_ev_fd` stores the eventfd context, async-only mode, last CQ tail, refcount, pending signal bit, and RCU head.
- `io_eventfd_register()` installs an eventfd for a ring.
- `io_eventfd_unregister()` removes it.
- `io_eventfd_signal()` signals the eventfd when completions are posted and notification policy allows it.
- `__io_eventfd_signal()` either signals immediately or defers through RCU when signaling is not currently allowed.

## Control Flow
Registration requires `ctx->uring_lock`, rejects duplicate eventfd registration, copies the fd from userspace, gets an `eventfd_ctx`, snapshots current CQ tail under `completion_lock`, sets ring flags, and publishes via RCU. Signaling checks ring availability, disabled CQ flag, async-only policy, and refcount. For CQE events, it suppresses duplicate notifications when `cached_cq_tail` has not advanced.

## State And Persistence
Per-ring state is `ctx->io_ev_fd` and `IO_RING_F_HAS_EVFD`. `last_cq_tail` tracks notification coalescing. RCU/refcounted `io_ev_fd` persists until all signal paths drop references after unregister.

## Dependencies And Integration Points
The file depends on eventfd, eventpoll wake mask `EPOLL_URING_WAKE`, io-wq worker detection for async mode, RCU, completion lock, and ring CQ flags. It is called by completion posting paths.

## Risks And Edge Cases
RCU/refcount correctness is critical around unregister racing with signal. Deferred signaling uses an atomic pending bit to avoid queuing multiple RCU callbacks. Duplicate notification suppression depends on `cached_cq_tail` under `completion_lock`.

## Test Signals
Tests should cover register/unregister, duplicate register `-EBUSY`, disabled CQ eventfd flag, async-only behavior from worker vs submitter, CQ tail coalescing, and unregister while completions race.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/eventfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/eventfd.h -->
# sources/distributed-fs/ceph-client/io_uring/eventfd.h

## Purpose
This header declares io_uring eventfd registration and signaling functions.

## Important APIs, Types, And Functions
- Forward declaration of `struct io_ring_ctx`.
- `io_eventfd_register()`, `io_eventfd_unregister()`, and `io_eventfd_signal()`.

## Control Flow
No local control flow.

## State And Persistence
No state is defined here; functions operate on per-ring eventfd state.

## Dependencies And Integration Points
Used by io_uring registration and completion paths to avoid exposing the implementation details of `struct io_ev_fd`.

## Risks And Edge Cases
Signaling callers must pass whether a CQE event actually occurred so duplicate suppression semantics remain correct.

## Test Signals
Build and eventfd registration/completion tests validate prototype integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/eventfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/fdinfo.c -->
# sources/distributed-fs/ceph-client/io_uring/fdinfo.c

## Purpose
`fdinfo.c` emits diagnostic `/proc/<pid>/fdinfo` output for io_uring file descriptors, including ring indices, queued SQEs/CQEs, SQPOLL metrics, registered files/buffers, poll/cancel state, overflow CQEs, and optional NAPI data.

## Important APIs, Types, And Functions
- `io_uring_show_fdinfo()` is the exported entry called by procfs fdinfo handling.
- `__io_uring_show_fdinfo()` performs the actual `seq_file` emission.
- `napi_show_fdinfo()` and `common_tracking_show_fdinfo()` print busy-poll tracking details when enabled.

## Control Flow
The public function tries `ctx->uring_lock` to avoid ABBA deadlocks with seq locks. The internal printer snapshots SQ/CQ head/tail values, iterates pending SQEs with nospec opcode bounds, iterates CQEs including CQE32 handling, reports SQPOLL thread metrics if applicable, lists registered files and buffers, traverses cancel-table poll lists, prints overflow CQEs under `completion_lock`, and appends NAPI info.

## State And Persistence
No state is mutated except local snapshots. Output reflects possibly racing ring state; the code explicitly tolerates imprecision for debugging.

## Dependencies And Integration Points
It depends on procfs/seq_file, io_uring rings, filetable helpers, SQPOLL metrics, cancel hash table, resource tables, opcode definitions, completion lock, and optional NAPI fields.

## Risks And Edge Cases
The code avoids blocking fdinfo reads behind ring locks by using `mutex_trylock()`, meaning output may be absent under contention. Active rings can race with printed SQ/CQ state. SQE128 and CQE32 handling must avoid wrap/corruption while printing.

## Test Signals
Manual/proc tests should verify fdinfo output for normal rings, SQPOLL, registered files/buffers, CQ overflow, poll lists, SQE128/CQE32, NAPI modes, and lock contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/fdinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/fdinfo.h -->
# sources/distributed-fs/ceph-client/io_uring/fdinfo.h

## Purpose
This header declares the procfs fdinfo printer for io_uring files.

## Important APIs, Types, And Functions
- `io_uring_show_fdinfo(struct seq_file *m, struct file *f)`.

## Control Flow
No local control flow.

## State And Persistence
No state is defined here.

## Dependencies And Integration Points
The declaration is used by io_uring file operations/proc integration when `CONFIG_PROC_FS` includes `fdinfo.o`.

## Risks And Edge Cases
Prototype drift would break fdinfo integration. The implementation relies on callers passing an io_uring file with `private_data` set to `struct io_ring_ctx`.

## Test Signals
Build coverage with procfs and readable `/proc/<pid>/fdinfo/<fd>` output validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/fdinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/filetable.c -->
# sources/distributed-fs/ceph-client/io_uring/filetable.c

## Purpose
`filetable.c` manages fixed-file table allocation, installation, removal, and automatic slot allocation for io_uring registered files.

## Important APIs, Types, And Functions
- `io_alloc_file_tables()` allocates resource node storage and the allocation bitmap.
- `io_free_file_tables()` frees resource data and bitmap.
- `__io_fixed_fd_install()` installs a file at a requested 1-based slot or automatically allocated slot.
- `io_fixed_fd_install()` wraps installation with submit locking and drops the file on error.
- `io_fixed_fd_remove()` clears an existing fixed-file slot.
- `io_register_file_alloc_range()` sets the auto-allocation range from userspace.

## Control Flow
Auto allocation uses `io_file_bitmap_get()` to scan from `alloc_hint` within `[file_alloc_start, file_alloc_end)`, wrapping once. Installation rejects io_uring files, missing tables, and out-of-range slots, allocates a resource node, resets any existing node at the slot, sets the bitmap, and stores encoded file pointer/flags. Removal validates the slot, resets the node, and clears the bitmap.

## State And Persistence
Per-ring state lives in `ctx->file_table.data.nodes`, `ctx->file_table.bitmap`, `alloc_hint`, and allocation range fields. Each node stores an encoded file pointer plus NOWAIT/regular-file flags.

## Dependencies And Integration Points
It depends on resource table helpers (`io_rsrc_data_alloc/free`, `io_rsrc_node_alloc/lookup/reset`), filetable inline encoding from `filetable.h`, submit locking, and UAPI `io_uring_file_index_range`.

## Risks And Edge Cases
Slot numbering differs between explicit userspace slots and zero-based internals; `IORING_FILE_INDEX_ALLOC` returns a zero-based allocated slot. Installing io_uring files is rejected to avoid recursion. Bitmap and node updates require `uring_lock` protection. Range overflow is checked with `check_add_overflow()`.

## Test Signals
Registered-file tests should cover explicit slots, auto allocation and wrap, allocation range validation, removal, io_uring file rejection, fixed file replacement, and error cleanup/fput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/filetable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/filetable.h -->
# sources/distributed-fs/ceph-client/io_uring/filetable.h

## Purpose
The header declares fixed-file table operations and defines inline helpers for bitmap and encoded file-slot state.

## Important APIs, Types, And Functions
- Public operations: allocate/free tables, install/remove fixed fd, and register allocation range.
- `io_file_bitmap_set()` and `io_file_bitmap_clear()` update bitmap and allocation hint with sanity warnings.
- `FFS_NOWAIT`, `FFS_ISREG`, and `FFS_MASK` encode request flags into low bits of `node->file_ptr`.
- `io_slot_flags()`, `io_slot_file()`, and `io_fixed_file_set()` decode/encode file pointers and flags.
- `io_file_table_set_alloc_range()` updates automatic allocation bounds and hint.

## Control Flow
Inline helpers provide fast bitmap and slot decoding paths used by request file lookup and registration.

## State And Persistence
The encoded `file_ptr` in resource nodes persists for the lifetime of registered slots. Allocation hint state persists per table.

## Dependencies And Integration Points
It depends on `io_uring_types.h`, resource node definitions, and `io_file_get_flags()` provided elsewhere. It is shared by fixed-file lookup, registration, fdinfo, and filetable implementation.

## Risks And Edge Cases
Pointer low-bit encoding assumes alignment leaves flag bits free. WARNs catch bitmap inconsistency but do not recover. Any change to request flag bit positions affects `io_slot_flags()` shifting.

## Test Signals
Fixed-file registration, NOWAIT flag behavior, fdinfo file printing, and KASAN/lockdep runs validate this header’s assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/filetable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/fs.c -->
# sources/distributed-fs/ceph-client/io_uring/fs.c

## Purpose
`fs.c` implements io_uring filesystem namespace operations: rename, unlink/rmdir, mkdir, symlink, and hardlink.

## Important APIs, Types, And Functions
- Per-op command structs store dirfds, delayed filenames, flags, mode, and a placeholder file pointer.
- Prep handlers: `io_renameat_prep`, `io_unlinkat_prep`, `io_mkdirat_prep`, `io_symlinkat_prep`, and `io_linkat_prep`.
- Issue handlers call `filename_renameat2`, `filename_unlinkat`/`filename_rmdir`, `filename_mkdirat`, `filename_symlinkat`, and `filename_linkat`.
- Cleanup handlers dismiss delayed filenames for operations that allocated them.

## Control Flow
Prep rejects unsupported SQE fields and fixed-file mode, reads dirfds/path pointers/flags, resolves paths through delayed filename helpers, marks the request for cleanup, and forces async execution. Issue handlers complete delayed filenames with scope helpers, call the corresponding VFS operation, clear cleanup state, set result, and complete.

## State And Persistence
Request-local state stores delayed filename objects until issue or cleanup. Persistent effects are filesystem namespace changes.

## Dependencies And Integration Points
The file depends on VFS internal filename helpers from `../fs/internal.h`, io_uring command storage, request cleanup flags, and async worker execution. `fs.h` exposes the handlers to the opcode table.

## Risks And Edge Cases
Delayed filename ownership is the main lifetime risk: every successful first allocation must be dismissed on second allocation failure or cleanup. These operations force async because namespace modifications can block. Fixed-file mode is rejected because path operations use dirfds and userspace paths.

## Test Signals
Tests should cover success and failure paths for rename/unlink/rmdir/mkdir/symlink/link, invalid flags, bad user pointers, cleanup after prep failure, cancellation before issue, and parity with syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/fs.h -->
# sources/distributed-fs/ceph-client/io_uring/fs.h

## Purpose
This header declares io_uring filesystem namespace operation handlers.

## Important APIs, Types, And Functions
- Rename, unlink, mkdir, symlink, and link prep/issue handlers.
- Cleanup hooks for operations that retain delayed filenames.

## Control Flow
No runtime flow is implemented here.

## State And Persistence
No state is defined here; declarations operate on per-request command storage in `fs.c`.

## Dependencies And Integration Points
Used by io_uring opcode definitions and cleanup dispatch.

## Risks And Edge Cases
Missing cleanup declarations would leak delayed filenames on canceled or failed requests. Prototype drift breaks opcode wiring.

## Test Signals
Build and filesystem operation tests validate handler declarations and cleanup hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/futex.c -->
# sources/distributed-fs/ceph-client/io_uring/futex.c

## Purpose
`futex.c` implements io_uring futex wait, waitv, wake, cancellation, and per-ring futex data caching.

## Important APIs, Types, And Functions
- `struct io_futex` stores user address, expected value, mask, futex flags, waitv count, and waitv unqueued state.
- `struct io_futex_data` wraps a single `futex_q` and request pointer.
- `struct io_futexv_data` stores ownership bit and flexible wait vector.
- `io_futex_prep()` and `io_futexv_prep()` validate SQEs and set inflight tracking.
- `io_futex_wait()`, `io_futexv_wait()`, and `io_futex_wake()` issue waits/wakes.
- `io_futex_cancel()` and `io_futex_remove_all()` integrate with generic cancellation.
- `io_futex_cache_init/free()` manage the per-ring allocation cache.

## Control Flow
Single futex wait prep validates flags, value, and mask. Issue allocates cached wait data under submit lock, initializes `futex_q`, calls `futex_wait_setup()`, and if successfully queued adds the request to `ctx->futex_list` and skips immediate completion. Wake callbacks set result zero, assign task-work completion, and queue completion.

Waitv prep allocates a vector, parses userspace waitv entries, and stores async data. Issue calls `futex_wait_multiple_setup()`, handles immediate errors, successful queueing, or races where a wake occurred during setup. Cancellation unqueues the futex or claims waitv ownership, removes the request from the hlist, sets `-ECANCELED`, and queues task work.

## State And Persistence
Per-ring state includes `ctx->futex_cache` and `ctx->futex_list`. Request async data holds futex queue/vector data until wake, cancel, or immediate failure. Inflight tracking ensures file/task exit cancellation can find queued waits.

## Dependencies And Integration Points
The file depends on kernel futex internals, io_uring task-work completion, generic cancellation helpers, allocation cache, submit locking, and `REQ_F_ASYNC_DATA` ownership.

## Risks And Edge Cases
Wait requests complete asynchronously and must remain discoverable for cancellation. Waitv uses an ownership bit to serialize wake and cancel completions. A zero mask is invalid for single wait. `futex_wait_multiple_setup()` can both queue and race with wake, requiring special `futexv_unqueued` handling. Cache objects must be returned exactly once.

## Test Signals
Tests should cover wait/wake success, wrong expected values, invalid flags/masks, cancellation while queued, cancellation racing wake, waitv immediate wake index, file/task exit cancellation, cache cleanup, and strict wake returning zero for zero wake count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/futex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/futex.h -->
# sources/distributed-fs/ceph-client/io_uring/futex.h

## Purpose
The header declares io_uring futex operation, cancellation, and cache functions with disabled-feature stubs.

## Important APIs, Types, And Functions
- Operation handlers: `io_futex_prep`, `io_futexv_prep`, `io_futex_wait`, `io_futexv_wait`, and `io_futex_wake`.
- Enabled `CONFIG_FUTEX` APIs for cancellation and cache lifecycle.
- Disabled stubs return no-op/false success for cancellation and cache lifecycle.

## Control Flow
Only disabled-feature stubs have local control flow, returning neutral values for callers.

## State And Persistence
No state is defined here. Functions operate on ring futex cache/list and request async data.

## Dependencies And Integration Points
It includes `cancel.h` and is used by opcode dispatch and generic cancellation code.

## Risks And Edge Cases
When futex support is disabled, callers must not dispatch futex operations but generic cancellation can safely call no-op stubs. Prototype correctness is important because futex cancellation is part of ring teardown.

## Test Signals
Builds with `CONFIG_FUTEX=y/n` and futex operation/cancellation tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/io-wq.c -->
# sources/distributed-fs/ceph-client/io_uring/io-wq.c

## Purpose
`io-wq.c` implements io_uring’s asynchronous worker pool. It creates per-task worker pools, separates bounded and unbounded work, serializes hashed work, handles cancellation, CPU hotplug/affinity, idle exit, and orderly teardown.

## Important APIs, Types, And Functions
- `struct io_wq` stores shared hash state, worker refs, CPU hotplug node, owner task, bounded/unbounded accounts, hash wait entry, hash tails, and CPU mask.
- `struct io_worker` tracks each worker task, refcount, current work, free/all list nodes, creation retry state, and exit state.
- `struct io_wq_acct` tracks per-class worker limits, running count, free/all lists, work list, locks, and stalled flag.
- Public APIs include `io_wq_create`, `io_wq_enqueue`, `io_wq_hash_work`, `io_wq_cancel_cb`, `io_wq_exit_start`, `io_wq_put_and_exit`, `io_wq_set_exit_on_idle`, `io_wq_cpu_affinity`, `io_wq_max_workers`, and worker scheduler hooks.

## Control Flow
`io_wq_create()` initializes the pool, refs shared hash state, copies the owner task’s cpuset mask, sets bounded/unbounded worker limits, and registers CPU hotplug state. `io_wq_enqueue()` inserts work into the appropriate account queue, preserving hash chains, wakes an idle worker, or creates a worker if concurrency/running-state requires it. If the pool is exiting or the work is pre-canceled, it runs cancellation immediately.

Worker threads run `io_wq_worker()`: they repeatedly acquire runnable work, mark themselves busy, submit work (including linked chains), free completed work, clear hash bits and wake stalled workers, then go idle with a timeout. Idle workers can exit after timeout, affinity mismatch, or exit-on-idle. Worker creation can occur immediately, via task_work, or delayed retry after temporary thread creation errors.

Cancellation first removes pending work from account queues, then marks running workers’ `cur_work` with cancel and signals worker tasks. Teardown sets exit, cancels pending worker-creation task_work, wakes workers, waits for `worker_done`, removes CPU hotplug state, cancels remaining pending work, drops hash/cpumask/task refs, and frees the pool.

## State And Persistence
Persistent pool state includes worker lists, free lists, account work queues, `nr_workers`, `nr_running`, shared hash map/wait queue, hash-tail array, CPU mask, and exit bits. Each worker stores `cur_work` under its own raw spinlock so cancellation can find running work. Hashed work uses upper work-flag bits and shared `hash->map` to prevent concurrent execution for the same key.

## Dependencies And Integration Points
The file depends on io_uring work submission/free callbacks (`io_wq_submit_work`, `io_wq_free_work`), task_work, PF_IO_WORKER scheduler hooks, cpuset/cpuhotplug, RCU nulls lists, raw spinlocks, delayed work, task limits, and generic cancellation via `io_wq_cancel_cb()`. `cancel.c`, eventfd async policy, and worker sleep/running hooks consume this interface.

## Risks And Edge Cases
This is a high-concurrency state machine. Risks include worker creation races with exit, losing work between pending queue and `cur_work`, hash stalls not waking, refcount imbalance during task_work cancellation, and teardown waits under heavy long-running work. The code uses worker refs, `create_state`, `worker_refs`, RCU lists, and hash wait queues to manage these hazards. Unbounded worker limits are clamped by `RLIMIT_NPROC`.

## Test Signals
Signals include io_uring async operation stress, hashed write serialization tests, cancellation of pending and running work, task exit/exec teardown, CPU hotplug affinity tests, worker max update tests, exit-on-idle behavior, and lockdep/KCSAN/KASAN under high concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/io-wq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/io-wq.h -->
# sources/distributed-fs/ceph-client/io_uring/io-wq.h

## Purpose
The header defines io-wq public types, flags, cancellation results, and worker-pool APIs used by io_uring core and cancellation paths.

## Important APIs, Types, And Functions
- Work flags: `IO_WQ_WORK_CANCEL`, `IO_WQ_WORK_HASHED`, `IO_WQ_WORK_UNBOUND`, `IO_WQ_WORK_CONCURRENT`, and `IO_WQ_HASH_SHIFT`.
- `enum io_wq_cancel` distinguishes pending cancellation success, running cancellation signal, and not found.
- `struct io_wq_hash` holds a shared refcounted hash serialization bitmap and wait queue.
- `struct io_wq_data` passes shared hash and owner task to `io_wq_create()`.
- Public APIs cover create/exit/enqueue/hash/cancel/affinity/max-workers and worker sleep/running hooks.
- `io_wq_current_is_worker()` identifies current io-wq worker context.

## Control Flow
Inline helpers check hashed work flags, drop hash refs, and provide no-op worker scheduler hooks when `CONFIG_IO_WQ` is disabled.

## State And Persistence
`io_wq_hash` persists across pools through refcounting. Work flags persist in `io_wq_work->flags` and drive queue selection, cancellation, and hash serialization.

## Dependencies And Integration Points
It depends on refcounting and `io_uring_types.h`. It is included by eventfd, cancellation, worker-pool implementation, and core request paths.

## Risks And Edge Cases
The upper 8 flag bits encode hash keys, so flag layout must remain synchronized with `io-wq.c`. `io_wq_current_is_worker()` relies on PF_IO_WORKER and `worker_private`, so scheduler integration must set/clear that pointer correctly.

## Test Signals
Builds with and without `CONFIG_IO_WQ`, async worker execution tests, eventfd async-only notification tests, and cancellation tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/io-wq.h -->
