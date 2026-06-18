# subset-b-009229 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/options.c -->
# sources/test-tools/fio/options.c

## Purpose
`options.c` is fio's central job-option registry and parser glue. It defines the global `fio_options` table, parser callbacks for compound options, default/keyword substitution helpers, command-line `getopt_long()` integration, option-set tracking, and cleanup for option-owned allocations. It turns user-facing job-file and command-line strings into `struct thread_options`, selected engine private options, `thread_data` runtime fields, and several process-wide settings.

## Important APIs, Types, and Functions
The main exported APIs are `fio_options_parse()`, `fio_cmd_option_parse()`, `fio_cmd_ioengine_option_parse()`, `fio_fill_default_options()`, `fio_options_dup_and_init()`, `fio_options_set_ioengine_opts()`, `fio_show_option_help()`, `fio_options_mem_dupe()`, `fio_options_free()`, `fio_dump_options_free()`, `fio_option_find()`, `fio_option_mark_set()`, `__fio_option_is_set()`, `fio_get_kb_base()`, `add_option()`, `invalidate_profile_options()`, `add_opt_posval()`, and `del_opt_posval()`. Important parser callbacks include block-size splits, priority splits, replay skipping, ignored errors, random/file-service distributions, steady-state criteria, filename/directory expansion, patterns, CPU masks, NUMA policies, offset/size percent or zone forms, log names, data placement IDs and scheme validation, memory backing, and clock source updates.

## Control Flow
`fio_options_parse()` sorts job options by metadata priority, duplicates each raw string with environment and fio keyword substitution, parses against `fio_options`, marks successfully parsed options in `thread_options.set_options`, then retries unknown options against the selected ioengine after `ioengine_load()`. The large `fio_options[]` table describes each option's name, alias, type, destination offsets, defaults, bounds, enum values, parent/hide relationships, category/group, callbacks, and validation. Compound callback flow generally duplicates and trims user input, splits comma/colon/range syntax, validates percentages or platform limits, fills per-direction arrays, and frees temporary parse allocations on dry-run or error. Long-option arrays are built by walking core options and then replacing the ioengine-option tail when an engine is selected.

## State and Persistence
Most state is in `struct thread_options` inside each `thread_data`: file names, engine names, block sizes, random distributions, zones, verification policies, logging, rate limits, CPU masks, cgroups, credentials, data-placement IDs, and option-set bits. Some callbacks update `thread_data` fields such as `file_service_nr`, `zipf_theta`, `pareto_h`, `gauss_dev`, and `ts_cache_mask`. Process-wide state includes `client_sockaddr_str`, `fio_clock_source`, `fio_clock_source_set`, and `exitall_on_terminate`. Persistent effects are indirect: selected options later cause fio to create files, write logs, replay traces, use cgroups, change scheduling/affinity, and choose ioengines; parsing itself only validates some paths with `stat()`/`lstat()`.

## Dependencies and Integration Points
The file depends on fio core headers (`fio.h`, `verify.h`, `parse.h`, `options.h`, `optgroup.h`, `zbd.h`), pattern parsing, OS abstraction helpers, ioengine loading, NUMA and CPU affinity feature macros, and platform-specific option availability. It is consumed by job-file parsing, command-line parsing, profile injection, external ioengine loading, help output, JSON/normal reporting configuration, verification, zoned block device handling, data placement, and statistics/logging.

## Risks and Edge Cases
The parser mutates duplicated strings heavily with `strsep()` and embedded NULs, so callbacks must preserve and free the original pointer. Percentage distribution code must account for missing percentages, over-100 totals, and direction fan-out. CPU masks must reject CPUs beyond both fio's mask width and currently configured CPUs. `bc_calc()` invokes `which` and `bc` through the shell for keyword-derived math and intentionally refuses quoted strings, but it is still sensitive to shell availability and expression length. `fio_get_kb_base()` uses a magic-field heuristic for private options and may fall back to the global default. Error paths around `calloc()`/`realloc()` and callback-owned allocations are important because options can be parsed repeatedly in dry-run, profile, and client/server flows.

## Test Signals
Useful tests include parsing representative job files for every major group, unknown option retry against ioengine private options, aliases and parent-hidden options, environment substitution with `${VAR}`, `$pagesize/$mb_memory/$ncpus` math, dry-run cleanup of split arrays, read-only rejection of write/trim jobs, external ioengine path validation, CPU/NUMA parsing failures, direction-specific block-size and zone splits, data-placement ID ranges, steady-state thresholds, ignored errno names and numbers, and leak checks after `fio_options_free()` and `fio_dump_options_free()`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/options.h -->
# sources/test-tools/fio/options.h

## Purpose
`options.h` exposes fio's option table interface to the rest of the program. It declares the global option capacity, option registration/mutation helpers, cleanup helpers, filename-list utilities, and the option-set query macro used by runtime code to distinguish defaults from explicit user input.

## Important APIs, Types, and Functions
The header declares `FIO_MAX_OPTS`, `fio_options`, `client_sockaddr_str`, `add_option()`, `invalidate_profile_options()`, `add_opt_posval()`, `del_opt_posval()`, `fio_options_free()`, `fio_dump_options_free()`, `get_next_str()`, `get_max_str_idx()`, `get_name_by_idx()`, `set_name_idx()`, `__fio_option_is_set()`, `fio_option_mark_set()`, `find_option()`, `find_option_c()`, `fio_option_find()`, and `fio_get_kb_base()`. `fio_option_is_set()` wraps `offsetof(struct thread_options, name)` and calls the offset-based lookup.

## Control Flow
Consumers include this header to find or mutate registered options and to ask whether a field was explicitly set. `o_match()` performs name-or-alias comparisons for option-table scans. Filename helpers declared here are implemented in `options.c` and are used when fio expands colon-separated file or directory lists.

## State and Persistence
The header itself owns no storage other than extern declarations. It grants access to the process-global `fio_options` array and `client_sockaddr_str`, and its macros query `thread_options.set_options` indirectly.

## Dependencies and Integration Points
It depends on `parse.h`, `lib/types.h`, `struct fio_option`, and `struct thread_options`. It is a bridge between parser internals, job setup, profiles, ioengines, and runtime code that needs explicit-option detection.

## Risks and Edge Cases
`fio_option_is_set()` relies on field names existing in `struct thread_options` and on `options.c` finding all options with matching `off1`; duplicate offsets are supported but can make the answer true because of any aliasing option. `FIO_MAX_OPTS` bounds dynamic additions and must remain large enough for profiles and build-time options.

## Test Signals
Signals include successful compilation of all users, explicit-vs-default checks for fields with aliases, option addition near capacity, profile invalidation, and filename-list parsing of escaped colons.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/kcompat.h -->
# sources/test-tools/fio/os/kcompat.h

## Purpose
`kcompat.h` provides tiny kernel-style integer aliases for fio code or imported headers that expect Linux kernel type names.

## Important APIs, Types, and Functions
It includes `<stdint.h>` and defines `u64` as `uint64_t` and `u32` as `uint32_t`.

## Control Flow
There is no runtime control flow. Inclusion supplies type aliases at preprocessing time.

## State and Persistence
The file has no state and no persistent effects.

## Dependencies and Integration Points
It integrates with source that shares definitions with kernel ABI headers or helper code where `u32`/`u64` naming is expected without pulling in broader kernel headers.

## Risks and Edge Cases
The aliases are macros rather than typedefs, so they can collide if another header has already defined the names differently. It deliberately does not define signed, 8-bit, 16-bit, or endian-qualified variants.

## Test Signals
Compile coverage for files including kernel-compatible ABI definitions is sufficient; no runtime tests are meaningful.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/kcompat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/linux/io_uring.h -->
# sources/test-tools/fio/os/linux/io_uring.h

## Purpose
`io_uring.h` vendors the Linux userspace ABI definitions needed by fio's io_uring engine. It lets fio build against systems whose libc/kernel headers may not expose all of the io_uring structures, opcodes, setup flags, feature flags, mmap offsets, and registration commands that fio wants to use or probe.

## Important APIs, Types, and Functions
Important ABI types are `struct io_uring_sqe`, `struct io_uring_cqe`, `struct io_sqring_offsets`, `struct io_cqring_offsets`, `struct io_uring_params`, resource registration/update structs, probe structs, restrictions, PI attributes, and `struct io_uring_getevents_arg`. Important constants include `IORING_OP_*`, `IOSQE_*`, `IORING_SETUP_*`, `IORING_ENTER_*`, `IORING_FEAT_*`, `IORING_REGISTER_*`, CQE/SQ ring flags, mmap offsets, timeout/poll/splice/fsync flags, and `IORING_REGISTER_FILES_SKIP`.

## Control Flow
There is no executable code. The structs define the memory layout shared with Linux syscalls: users fill SQEs, map rings using offsets returned in `io_uring_params`, read CQEs, and pass registration/probe structs to `io_uring_register()`.

## State and Persistence
Runtime state lives in kernel-created rings and userspace mappings described by these structs. The header persists no state itself, but layout mistakes would corrupt submission/completion interpretation.

## Dependencies and Integration Points
It depends on Linux UAPI types from `<linux/fs.h>` and `<linux/types.h>`. fio's io_uring engine, feature probing, registered file/buffer handling, polling, SQ/CQ sizing, PI attributes, and newer command support depend on this ABI matching the kernel.

## Risks and Edge Cases
Because this mirrors a moving kernel ABI, stale definitions can hide or misdescribe newer flags. Flexible array members and packed fields must match kernel layout across architectures. Optional features such as SQE128/CQE32, registered-ring FDs, mixed CQEs, PI attributes, and fixed uring commands must be gated by kernel feature/probe results before use.

## Test Signals
Build tests on older and newer Linux headers, io_uring engine smoke tests, feature-probe validation, fixed-buffer/file registration tests, CQE size variants, and syscall failure handling on kernels lacking specific flags are the strongest signals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/linux/io_uring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/mac/posix.c -->
# sources/test-tools/fio/os/mac/posix.c

## Purpose
`os/mac/posix.c` implements a macOS compatibility version of `posix_fadvise()` for fio. macOS lacks the POSIX API, so fio maps common advice values to `fcntl(F_RDAHEAD)` and cache invalidation using `mmap()` plus `msync(MS_INVALIDATE)`.

## Important APIs, Types, and Functions
`posix_fadvise()` is the exported function. `set_readhead()` toggles read-ahead with `F_RDAHEAD`. `discard_pages()` aligns an offset/length to page boundaries, maps file ranges in chunks up to `MMAP_CHUNK_SIZE`, invalidates cached pages with `msync()`, and unmaps them.

## Control Flow
`posix_fadvise()` switches on advice: `NORMAL` is a no-op, `RANDOM` disables read-ahead, `SEQUENTIAL` enables read-ahead, `DONTNEED` calls `discard_pages()`, and unknown advice returns `EINVAL`. `discard_pages()` loops over large ranges in bounded 16 GiB mappings, preserving and returning errno from `mmap()`, `msync()`, or `munmap()` failures.

## State and Persistence
The file does not persist fio state. It may alter kernel read-ahead behavior for an fd and invalidate page-cache residency for mapped file ranges. It logs errors through fio's logging layer.

## Dependencies and Integration Points
It depends on macOS `fcntl`, `mmap`, `msync`, `munmap`, page-size `sysconf()`, `MIN()`, and `log_err()`. `os-mac.h` includes `mac/posix.h` and defines `CONFIG_POSIX_FADVISE`, allowing common fio fadvise paths to compile on macOS.

## Risks and Edge Cases
Offset and length alignment expands the invalidation range to page boundaries. The implementation is documented as slower under Rosetta. Mapping with `PROT_NONE|MAP_SHARED` can fail for file types or ranges not mappable by macOS. Very large ranges rely on chunking to avoid oversized mappings.

## Test Signals
Tests should cover each advice value, invalid advice, unaligned ranges, ranges larger than 16 GiB, non-mappable fds, and fio workloads using `fadvise_hint=random/sequential/dontneed` on macOS.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/mac/posix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/mac/posix.h -->
# sources/test-tools/fio/os/mac/posix.h

## Purpose
`os/mac/posix.h` declares the macOS `posix_fadvise()` compatibility shim and defines the advice constants that fio's common code expects.

## Important APIs, Types, and Functions
It defines `POSIX_FADV_NORMAL`, `POSIX_FADV_RANDOM`, `POSIX_FADV_SEQUENTIAL`, and `POSIX_FADV_DONTNEED`, and declares `int posix_fadvise(int fd, off_t offset, off_t len, int advice)`.

## Control Flow
There is no runtime control flow in the header; the implementation is in `posix.c`.

## State and Persistence
The header has no state. It enables common fio code to request macOS file-cache advice through the compatibility function.

## Dependencies and Integration Points
It is included by `os-mac.h`, which exposes `CONFIG_POSIX_FADVISE` for macOS builds. It relies on the including context to provide `off_t`.

## Risks and Edge Cases
The constants are local compatibility values, not necessarily OS-native ABI values. All callers must link the corresponding `posix.c` implementation.

## Test Signals
Build/link tests for macOS and runtime fadvise tests through fio's `fadvise_hint` option validate this file.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/mac/posix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os-aix.h -->
# sources/test-tools/fio/os/os-aix.h

## Purpose
`os-aix.h` selects fio's AIX platform capabilities and supplies inline OS helpers for direct I/O, anonymous mapping, block-device sizing, physical memory detection, and thread affinity discovery.

## Important APIs, Types, and Functions
It defines `FIO_OS os_aix`, `FIO_HAVE_ODIRECT`, `FIO_USE_GENERIC_INIT_RANDOM_STATE`, `OS_MAP_ANON`, `OS_MSG_DONTWAIT`, and `FIO_USE_GENERIC_SWAP`. Inline helpers are `blockdev_invalidate_cache()`, `blockdev_size()`, and `os_phys_mem()`.

## Control Flow
`blockdev_size()` issues `ioctl(fd, IOCINFO, &devinfo)` and computes bytes from SCSI disk block count and block size. `os_phys_mem()` reads `_SC_AIX_REALMEM` via `sysconf()` and converts KiB to bytes. Cache invalidation is unsupported and returns `ENOTSUP`.

## State and Persistence
There is no persistent state. Calls query kernel/device state and report capability through compile-time macros.

## Dependencies and Integration Points
The header depends on AIX `<sys/devinfo.h>`, `<sys/ioctl.h>`, `unistd`, and fio's `file.h`. It feeds common fio file/device sizing, memory sizing, random seed initialization, byte swapping, and options that require direct I/O support.

## Risks and Edge Cases
`blockdev_size()` assumes the device reports `info.un.scdk` fields; non-disk devices may fail or report incompatible union members. `_SC_AIX_REALMEM` failure returns zero physical memory, which affects keyword substitution and memory-derived options.

## Test Signals
AIX build coverage, block-device size checks against known disks, `$mb_memory` keyword validation, and direct-I/O option smoke tests provide useful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os-aix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os-ashmem.h -->
# sources/test-tools/fio/os/os-ashmem.h

## Purpose
`os-ashmem.h` emulates SysV shared-memory calls on Android/Bionic using ashmem or `ASharedMemory_create()` when normal SysV shared memory is unavailable.

## Important APIs, Types, and Functions
It maps `shmid_ds` to `shmid64_ds`, defines `SHM_HUGETLB`, and provides inline replacements for `shmctl()`, `shmget()`, `shmat()`, and `shmdt()`. It uses `/dev/ashmem` unless `CONFIG_ASHAREDMEMORY_CREATE` enables the Android shared-memory API.

## Control Flow
`shmget()` creates or opens an ashmem object, names it from the key, and allocates requested size plus eight bytes for length storage. `shmat()` maps the full ashmem fd, stores the mapping size at the front, and returns an aligned pointer after that header. `shmdt()` subtracts one `uint64_t` to recover the stored size and unmaps. `shmctl(IPC_RMID)` unpins and closes the fd.

## State and Persistence
The only state is the fd-backed ashmem region and the hidden length word at the beginning of each mapping. Lifetime is fd/mapping scoped; there is no SysV-style global key registry in this shim.

## Dependencies and Integration Points
Android builds include this from `os-linux.h` under `__ANDROID__`. It integrates with fio's shared-memory allocation paths when `CONFIG_NO_SHM` is not set.

## Risks and Edge Cases
The shim only implements the subset fio needs. `shmat()` does not check `mmap()` failure before writing the length word, which is a risk if mapping fails. Key semantics and permission flags do not fully match SysV shared memory. `shmctl()` only meaningfully handles `IPC_RMID`.

## Test Signals
Android shared-memory allocation/free tests, failure injection for ashmem open/ioctl/mmap, alignment checks on 32-bit ARM, and fio shared-memory buffer runs are the key signals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os-ashmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os-dragonfly.h -->
# sources/test-tools/fio/os/os-dragonfly.h

## Purpose
`os-dragonfly.h` adapts fio to DragonFly BSD. It declares supported features and implements CPU masks/affinity, I/O priority mapping, block/character device sizing, trim, filesystem free-space, physical memory, thread id, and removed-shm attachment behavior.

## Important APIs, Types, and Functions
It defines `FIO_HAVE_ODIRECT`, `FIO_HAVE_FS_STAT`, `FIO_HAVE_TRIM`, `FIO_HAVE_CHARDEV_SIZE`, `FIO_HAVE_GETTID`, `FIO_HAVE_CPU_AFFINITY`, `FIO_HAVE_IOPRIO`, and `FIO_HAVE_SHM_ATTACH_REMOVED`. Helpers include `fio_cpuset_init()`, `fio_cpu_set()/clear()/isset()/count()`, `fio_setaffinity()`, `fio_getaffinity()`, `blockdev_size()`, `chardev_size()`, `os_trim()`, `get_fs_free_size()`, `os_phys_mem()`, `gettid()`, and `shm_attach_to_open_removed()`.

## Control Flow
Affinity is implemented with DragonFly `usched_set()` for the current thread only, adding CPUs one by one. Device size uses `DIOCGPART`; trim uses `DAIOCTRIM` or legacy `IOCTLTRIM`; free space uses `statvfs()`. Shared-memory behavior is queried from `kern.ipc.shm_allow_removed`.

## State and Persistence
The header has no static state. Calls can change thread CPU binding and issue device trim commands; other helpers query kernel state.

## Dependencies and Integration Points
It depends on DragonFly `sysctl`, `statvfs`, disk-slice, scheduler, and resource headers. Its feature macros enable fio options and code paths for affinity, trim, ioprio, direct I/O, and filesystem stats.

## Risks and Edge Cases
Affinity ignores the passed pid and applies to the current thread because of `usched_set()` limitations. The cpumask compatibility macros assume DragonFly's x86_64 layout for older headers. I/O priority has no class concept, so fio's class/hint arguments are collapsed to a simple priority value.

## Test Signals
DragonFly build tests, affinity set/get for current thread, trim against disposable block devices, sysctl-based memory/free-space checks, and ioprio option parsing are relevant.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os-dragonfly.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os-freebsd.h -->
# sources/test-tools/fio/os/os-freebsd.h

## Purpose
`os-freebsd.h` supplies fio's FreeBSD feature declarations and inline wrappers for CPU affinity, disk sizing, trim, physical memory, filesystem free space, and thread id.

## Important APIs, Types, and Functions
It defines feature macros for direct I/O, generic random seeds, character device size, filesystem stats, trim, gettid, CPU affinity, and removed-shm attachment. Helpers include cpuset initialization/destruction, CPU bit operations, `fio_setaffinity()`, `fio_getaffinity()`, `blockdev_size()`, `chardev_size()`, `blockdev_invalidate_cache()`, `os_phys_mem()`, `gettid()`, `get_fs_free_size()`, `os_trim()`, and `shm_attach_to_open_removed()`.

## Control Flow
Affinity uses FreeBSD `cpuset_setaffinity()` and `cpuset_getaffinity()`. Disk size uses `DIOCGMEDIASIZE`; trim sends `DIOCGDELETE` with an offset/length pair. Memory and removed-shm support are read through `sysctl`; free space uses `statvfs()`.

## State and Persistence
No static state is stored. Affinity calls change scheduler state for a process/thread target, and trim can persistently discard device ranges.

## Dependencies and Integration Points
The header depends on FreeBSD `sysctl`, disk, threading, socket, param, cpuset, and statvfs APIs. The macros enable fio's direct I/O, trim verification, affinity options, filesystem stats, and shared-memory behavior checks.

## Risks and Edge Cases
`fio_getaffinity()` uses `CPU_WHICH_PID` while `fio_setaffinity()` uses `CPU_WHICH_TID`, so pid/tid interpretation matters. Cache invalidation is unsupported. Trim ioctl semantics should be tested across FreeBSD releases and device classes.

## Test Signals
FreeBSD build coverage, `cpus_allowed` parsing and enforcement, block/char device size checks, disposable-device trim, and `shm_attach_to_open_removed()` on kernels with different `kern.ipc.shm_allow_removed` values are useful.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os-freebsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os-hpux.h -->
# sources/test-tools/fio/os/os-hpux.h

## Purpose
`os-hpux.h` adapts fio to HP-UX, including direct I/O capability, POSIX advice mappings, AIO control-block type selection, block/char device sizing, physical memory, and CPU count.

## Important APIs, Types, and Functions
It defines `FIO_HAVE_ODIRECT`, `FIO_USE_GENERIC_INIT_RANDOM_STATE`, `FIO_HAVE_CHARDEV_SIZE`, `FIO_USE_GENERIC_SWAP`, `FIO_OS_HAVE_AIOCB_TYPEDEF`, `os_aiocb_t` as `struct aiocb64`, and `FIO_HAVE_CPU_CONF_SYSCONF`. Inline helpers are `blockdev_invalidate_cache()`, `blockdev_size()`, `chardev_size()`, `os_phys_mem()`, and `cpus_configured()`.

## Control Flow
`blockdev_size()` calls `ioctl(DIOC_DESCRIBE_EXT)` and combines high/low max SVA fields with logical block size. `os_phys_mem()` uses `pstat(PSTAT_STATIC)` and multiplies physical pages by page size. `cpus_configured()` uses `mpctl(MPC_GETNUMSPUS)`.

## State and Persistence
There is no persistent state. Helpers query kernel/device properties; cache invalidation is unsupported.

## Dependencies and Integration Points
It relies on HP-UX fadvise/mman/mpctl/diskio/pstat/AIO headers and fio `file.h`. Its macros drive option availability for direct I/O, char-device sizing, generic random seeds, and POSIX AIO typedef handling.

## Risks and Edge Cases
Device size computation depends on HP-UX disk descriptor fields and may not apply to all device types. `MSG_WAITALL` is locally defined if missing. CPU count and memory queries can return unusual values on partitioned systems.

## Test Signals
HP-UX build/link coverage, POSIX AIO builds, disk size comparisons, physical memory keyword checks, and direct-I/O job smoke tests validate this header.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os-hpux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os-linux-syscall.h -->
# sources/test-tools/fio/os/os-linux-syscall.h

## Purpose
`os-linux-syscall.h` supplies fallback Linux syscall numbers for architectures where libc or kernel headers may not define every number fio needs.

## Important APIs, Types, and Functions
It conditionally defines `__NR_ioprio_set`, `__NR_ioprio_get`, `__NR_fadvise64`, `__NR_sys_splice`, `__NR_sys_tee`, `__NR_sys_vmsplice`, `__NR_shmget`, `__NR_shmat`, `__NR_shmctl`, `__NR_shmdt`, `__NR_preadv2`, and `__NR_pwritev2` for supported architecture macros.

## Control Flow
There is no runtime flow. Preprocessor branches select definitions based on `arch/arch.h` macros such as x86, x86_64, ppc, ia64, alpha, s390, sparc, arm, mips64, sh, hppa, aarch64, loongarch64, and riscv64.

## State and Persistence
No state is stored. The values are used by `syscall()` wrappers in Linux OS and engine code.

## Dependencies and Integration Points
`os-linux.h` includes this header before defining ioprio, gettid, and preadv2/pwritev2 wrappers. Splice engines, fadvise paths, Android/shared-memory paths, and io priority handling may depend on these numbers.

## Risks and Edge Cases
Syscall numbers are architecture ABI constants; wrong values cause hard-to-debug `ENOSYS` or unintended syscall invocation. Some architectures only define subsets, leaving common code to rely on existing system headers or fallback stubs. Unknown architectures emit a warning rather than a hard error.

## Test Signals
Cross-compile builds for each architecture, runtime smoke tests for ioprio and preadv2/pwritev2 where available, and compile checks with old kernel headers are important.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os-linux-syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os-linux.h -->
# sources/test-tools/fio/os/os-linux.h

## Purpose
`os-linux.h` is fio's Linux and Android platform adapter. It declares Linux feature availability and provides wrappers for CPU affinity, I/O priorities, device sizing, cache invalidation, memory/free-space queries, trim, scheduling, byte swaps, pwritev2/preadv2, fallocate, and CPU feature probing.

## Important APIs, Types, and Functions
The header defines many `FIO_HAVE_*` capabilities, `os_cpu_mask_t`, CPU mask macros, ioprio classes and encoding helpers, `ioprio_set()`, `gettid()`, `blockdev_invalidate_cache()`, `blockdev_size()`, `os_phys_mem()`, `arch_cache_line_size()`, `get_fs_free_size()`, `os_trim()`, `fio_set_sched_idle()`, fallback `preadv2()`/`pwritev2()`, `shm_attach_to_open_removed()`, `fio_fallocate()`, and `os_cpu_has()`.

## Control Flow
Affinity maps to `sched_setaffinity()`/`sched_getaffinity()` according to configure-detected signatures. I/O priority is encoded with class, hint, and level before the `__NR_ioprio_set` syscall. Device size and trim use `BLKGETSIZE64`, `BLKFLSBUF`, and `BLKDISCARD` ioctls. Cache line size reads sysfs. Free space uses `statfs()`. `preadv2()`/`pwritev2()` wrappers split 64-bit offsets for 32-bit ABIs. CPU feature probing checks AArch64 HWCAP bits for CRC crypto.

## State and Persistence
The header has no static state. Helpers can change thread scheduling, affinity, I/O priority, allocate file space, discard block ranges, or invalidate block-device cache. Other helpers only query kernel state.

## Dependencies and Integration Points
It depends on Linux ioctl, syscall, mmap, sched, fs, SCSI generic, byteorder, Android ashmem, fio `file.h`, and architecture headers. Its feature macros drive the options table, engines, trim support, disk utilization, cgroups, pwritev2 flags, write hints, atomic writes, and CPU-specific checksum paths.

## Risks and Edge Cases
Kernel headers and libc may disagree on newer constants; this header supplies many fallback definitions. `FIO_HAVE_RWF_ATOMIC` is declared with fallback `RWF_ATOMIC`, but runtime support still depends on kernel/filesystem behavior. Sysfs cache-line reading can fail and must fall back in `os.h`. `fallocate()` has a workaround for old glibc returning positive errno values.

## Test Signals
Linux builds across glibc/musl/Android, affinity and ioprio option tests, block-device size/cache/trim tests, pwritev2 flag tests, cgroup/disk-util jobs, fallocate modes, and CPU feature detection on AArch64 are strong signals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os-linux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os-mac.h -->
# sources/test-tools/fio/os/os-mac.h

## Purpose
`os-mac.h` adapts fio to macOS. It declares macOS feature support and implements direct-I/O toggling, disk/char device sizing, memory detection, thread id, native preallocation, CPU feature detection, byte swaps, and POSIX fadvise compatibility exposure.

## Important APIs, Types, and Functions
It defines `FIO_OS os_mac`, `FIO_USE_GENERIC_INIT_RANDOM_STATE`, `FIO_HAVE_GETTID`, `FIO_HAVE_CHARDEV_SIZE`, `FIO_HAVE_NATIVE_FALLOCATE`, `FIO_HAVE_CPU_HAS`, `FIO_OS_DIRECTIO`, and `CONFIG_POSIX_FADVISE`. Helpers include `fio_set_odirect()`, `blockdev_size()`, `chardev_size()`, `blockdev_invalidate_cache()`, `os_phys_mem()`, `gettid()`, `fio_fallocate()`, and `os_cpu_has()`.

## Control Flow
Direct I/O is approximated with `fcntl(F_NOCACHE)`. Block size uses `DKIOCGETBLOCKCOUNT` and `DKIOCGETBLOCKSIZE`; char-device size falls back to block sizing or reports unknown size. Preallocation calls `fcntl(F_PREALLOCATE)` followed by `ftruncate()`. CPU feature detection currently treats AArch64 macOS as supporting the CRC32C feature.

## State and Persistence
No global state is stored. Calls may alter fd cache behavior and preallocate/truncate files.

## Dependencies and Integration Points
It depends on macOS disk, sysctl, Mach thread, endian, and `OSByteOrder` APIs, plus `mac/posix.h`. Its macros enable common fio paths for native fallocate, fadvise, direct I/O setup, and CPU-accelerated checksums.

## Risks and Edge Cases
`mach_thread_self()` returns a send right that typical code should deallocate; using it as a thread id can be platform-specific. `fio_fallocate()` truncates to `len`, not `offset + len`, matching the local implementation but worth checking for nonzero offsets. `F_NOCACHE` is not identical to Linux `O_DIRECT`.

## Test Signals
macOS build tests, direct-I/O/fadvise jobs, raw disk size checks, native preallocation tests with nonzero offset, and ARM64 checksum feature selection tests are relevant.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os-mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os-netbsd.h -->
# sources/test-tools/fio/os/os-netbsd.h

## Purpose
`os-netbsd.h` provides fio's NetBSD platform feature declarations and helpers for disk sizing, cache invalidation status, physical memory, thread id, filesystem free space, byte swaps, and optional thread affinity query.

## Important APIs, Types, and Functions
It defines `FIO_HAVE_ODIRECT`, `FIO_USE_GENERIC_INIT_RANDOM_STATE`, `FIO_HAVE_FS_STAT`, `FIO_HAVE_GETTID`, `OS_MAP_ANON`, swap macros, and optional `FIO_HAVE_GET_THREAD_AFFINITY`. Inline helpers include `blockdev_size()`, `blockdev_invalidate_cache()`, `os_phys_mem()`, `gettid()`, and `get_fs_free_size()`.

## Control Flow
`blockdev_size()` reads `struct disklabel` through `ioctl(DIOCGDINFO)` and multiplies sectors by sector size. `os_phys_mem()` uses `sysctl(CTL_HW, HW_PHYSMEM64)`. `gettid()` uses `_lwp_self()` when no configured gettid exists. Free space uses `statvfs()`.

## State and Persistence
There is no persistent state. Helpers query kernel/device state; cache invalidation is unsupported.

## Dependencies and Integration Points
It depends on NetBSD LWP, disklabel, dkio, endian, sysctl, and statvfs headers. It also undefines rbtree names to avoid conflicts with fio's own rbtree definitions.

## Risks and Edge Cases
Disklabel sizing may be insufficient for newer or nontraditional devices. Lack of `FIO_HAVE_TRIM` means trim-related options should be unsupported through common code. Header symbol conflict workarounds must stay aligned with NetBSD system headers.

## Test Signals
NetBSD build tests, disk size checks, filesystem free-space checks, and workloads using direct I/O and generic random seeds are useful.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os-netbsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os-openbsd.h -->
# sources/test-tools/fio/os/os-openbsd.h

## Purpose
`os-openbsd.h` adapts fio to OpenBSD with feature declarations and helpers for disk sizing, memory, thread id, filesystem free space, removed shared-memory behavior, byte swaps, and optional thread affinity query.

## Important APIs, Types, and Functions
It defines `FIO_USE_GENERIC_INIT_RANDOM_STATE`, `FIO_HAVE_FS_STAT`, `FIO_HAVE_GETTID`, `FIO_HAVE_SHM_ATTACH_REMOVED`, `OS_MAP_ANON`, swap macros, optional `FIO_HAVE_GET_THREAD_AFFINITY`, and helpers `blockdev_size()`, `blockdev_invalidate_cache()`, `os_phys_mem()`, `gettid()`, `get_fs_free_size()`, and `shm_attach_to_open_removed()`.

## Control Flow
Disk size uses `ioctl(DIOCGDINFO)` and disklabel fields. Memory uses `sysctl(CTL_HW, HW_PHYSMEM64)`. `gettid()` casts `pthread_self()`. `shm_attach_to_open_removed()` parses `uname().release` and returns true for OpenBSD 5.1 or newer.

## State and Persistence
There is no static state. Helpers query OS state; cache invalidation is unsupported.

## Dependencies and Integration Points
It depends on OpenBSD disklabel, dkio, endian, utsname, sysctl, statvfs, and fio `file.h`. It undefines `RB_*` names to avoid tree macro conflicts with fio headers.

## Risks and Edge Cases
Version parsing assumes single-digit major/minor release components; the code explicitly rejects unexpected formats. OpenBSD lacks direct I/O and trim declarations here, so common option availability must reflect that. `pthread_self()` as integer thread id is a compatibility approximation.

## Test Signals
OpenBSD build tests, disk/free-space/memory query tests, release parsing across supported versions, and shared-memory removal behavior checks are useful.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os-openbsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os-qnx.h -->
# sources/test-tools/fio/os/os-qnx.h

## Purpose
`os-qnx.h` adapts fio to QNX. It provides missing POSIX/Linux-like definitions, disables SysV shared-memory header use, and implements block sizing, memory sizing, filesystem free-space, thread id feature declaration, and byte swaps.

## Important APIs, Types, and Functions
It defines `FIO_OS os_qnx`, `FIO_NO_HAVE_SHM_H`, `FIO_USE_GENERIC_INIT_RANDOM_STATE`, `FIO_HAVE_FS_STAT`, `FIO_HAVE_GETTID`, local `__u64`/`__u32`, `SA_RESTART` fallback, `OS_MAP_ANON`, and helpers `blockdev_size()`, `blockdev_invalidate_cache()`, `os_phys_mem()`, and `get_fs_free_size()`.

## Control Flow
`blockdev_size()` uses `fstat()` and computes bytes from `st_blocksize * st_nblocks`. `os_phys_mem()` walks QNX syspage `asinfo` entries and sums ranges named `"ram"`. Free space uses `statvfs()`. Cache invalidation is unsupported.

## State and Persistence
No persistent state is stored. Helpers only query kernel metadata.

## Dependencies and Integration Points
It depends on QNX syspage, statvfs, CAM command, utsname, and sys/tree-interacting headers. Feature macros drive fio option availability for filesystem stats and generic random seeding while disabling normal shm headers.

## Risks and Edge Cases
The `os_phys_mem()` implementation uses C99-style loop declarations and asserts syspage element sizing. Block sizing via `st_blocksize * st_nblocks` may describe allocated blocks rather than full raw-device capacity depending on fd type. Shared-memory support is intentionally limited.

## Test Signals
QNX build tests, physical memory comparison to system tools, block/file size checks, filesystem free-space checks, and fio workloads that avoid unsupported shm paths validate this header.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os-qnx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os-solaris.h -->
# sources/test-tools/fio/os/os-solaris.h

## Purpose
`os-solaris.h` adapts fio to Solaris. It declares platform features and implements char-device sizing, generic block sizing, direct I/O enabling, physical memory/free-space queries, processor-set based affinity, ctime compatibility, and thread id support.

## Important APIs, Types, and Functions
It defines `FIO_HAVE_CPU_AFFINITY`, `FIO_HAVE_CHARDEV_SIZE`, `FIO_USE_GENERIC_BDEV_SIZE`, `FIO_HAVE_FS_STAT`, `FIO_USE_GENERIC_INIT_RANDOM_STATE`, `FIO_HAVE_GETTID`, `FIO_OS_DIRECTIO`, `FIO_MAX_CPUS`, `os_cpu_mask_t` as `psetid_t`, `struct solaris_rand_seed`, and helpers `chardev_size()`, `blockdev_invalidate_cache()`, `os_phys_mem()`, `get_fs_free_size()`, `fio_set_odirect()`, `fio_cpu_isset()`, `fio_cpu_count()`, `fio_cpuset_init()`, `fio_cpuset_exit()`, and `gettid()`.

## Control Flow
Character-device size uses `DKIOCGMEDIAINFO`. Direct I/O calls `directio(fd, DIRECTIO_ON)`. Affinity creates processor sets, assigns CPUs with `pset_assign()`, binds LWPs with `pset_bind()`, and counts/tests membership with `pset_info()`. Free space uses `statvfs()` and memory uses `sysconf()`.

## State and Persistence
Processor sets are OS resources created/destroyed by cpuset helpers. Direct I/O changes fd behavior. Other helpers query state; cache invalidation is unsupported.

## Dependencies and Integration Points
It depends on Solaris pset, dkio, byteorder, statvfs, mmap, pthread, and directio APIs. Its feature macros enable fio affinity options, direct I/O setup, filesystem stats, char-device sizing, and generic block-size logic.

## Risks and Edge Cases
Processor-set creation can fail and must be destroyed to avoid leaks. `fio_cpu_clear()` and `fio_cpu_set()` have side effects on global processor-set assignment, not just local masks. `gettid()` returns `pthread_self()` cast to int-like return, which may be lossy depending on type width.

## Test Signals
Solaris build tests, processor-set lifecycle tests, directio jobs, DKIO media-size checks, statvfs free-space checks, and CPU affinity option tests are important.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os-solaris.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os-windows-7.h -->
# sources/test-tools/fio/os/os-windows-7.h

## Purpose
`os-windows-7.h` defines fio's Windows CPU mask shape for Windows 7 and later processor-group APIs.

## Important APIs, Types, and Functions
It defines `FIO_MAX_CPUS` as 512, `FIO_CPU_MASK_STRIDE` as 64, `FIO_CPU_MASK_ROWS` as `FIO_MAX_CPUS / FIO_CPU_MASK_STRIDE`, and `os_cpu_mask_t` as a struct containing `uint64_t row[FIO_CPU_MASK_ROWS]`.

## Control Flow
There is no runtime flow. The constants determine how `windows/cpu-affinity.c` maps linear CPU indexes into row/bit positions and Windows processor groups.

## State and Persistence
The type stores in-memory CPU masks only. It has no persistent state.

## Dependencies and Integration Points
`os-windows.h` includes this header and declares CPU affinity helpers that consume `os_cpu_mask_t`.

## Risks and Edge Cases
The hard cap of 512 logical CPUs is based on an older Hyper-V limit and may be too small for future or very large systems. All row/offset math in the implementation depends on these constants.

## Test Signals
Windows affinity tests on systems with more than 64 CPUs and compile-time checks for mask row count validate this definition.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os-windows-7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os-windows.h -->
# sources/test-tools/fio/os/os-windows.h

## Purpose
`os-windows.h` adapts fio to Windows by declaring POSIX-like shims, Windows feature support, direct/open flag placeholders, path and clock defaults, device sizing, memory and random seed helpers, scheduling, mkdir emulation, and CPU affinity APIs.

## Important APIs, Types, and Functions
It defines `FIO_OS os_windows`, `FIO_HAVE_ODIRECT`, `FIO_HAVE_CPU_AFFINITY`, `FIO_HAVE_CHARDEV_SIZE`, `FIO_HAVE_GETTID`, `FIO_EMULATED_MKDIR_TWO`, `FIO_PREFERRED_ENGINE "windowsaio"`, path separator `\\`, signal and fcntl placeholders, POSIX prototypes, and helpers `blockdev_size()`, `chardev_size()`, `blockdev_invalidate_cache()`, `os_phys_mem()`, `gettid()`, `init_random_seeds()`, `fio_set_sched_idle()`, and `fio_mkdir()`.

## Control Flow
`blockdev_size()` uses an existing `HANDLE` or opens the path with `CreateFile()`, then calls `DeviceIoControl(IOCTL_DISK_GET_LENGTH_INFO)`. Random seeds come from `CryptAcquireContext()` and `CryptGenRandom()`. `fio_mkdir()` checks existing directory attributes, calls `CreateDirectoryA()`, and maps Windows errors to POSIX errno except for the device namespace case.

## State and Persistence
Helpers may open/close handles, create directories, change thread priority, and fill random seed buffers. The header itself has no static state.

## Dependencies and Integration Points
It depends on Winsock, Windows, PSAPI, fio Windows POSIX shims, `smalloc`, debug/log helpers, hweight, and `os-windows-7.h`. Its declarations are used by fio core, file setup, random initialization, scheduler-idle support, and Windows async I/O engine paths.

## Risks and Edge Cases
`O_DIRECT` and `O_SYNC` are placeholder bits for runtime rejection outside Windows native open paths. `blockdev_size()` must handle the difference between POSIX fd-backed files and Windows handles. Many POSIX functions are declared here but implemented elsewhere, so link coverage matters. `sysconf()` values are shim-defined.

## Test Signals
Windows builds, `windowsaio` smoke tests, raw disk size checks, random seed initialization failure handling, mkdir behavior for existing directories and `\\.` namespace, and CPU affinity tests validate this adapter.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os-windows.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/os.h -->
# sources/test-tools/fio/os/os.h

## Purpose
`os.h` is fio's cross-platform OS abstraction umbrella. It selects the platform-specific header, fills missing feature defaults, provides generic fallbacks, normalizes byte-order helpers, and exposes common helpers for cache line size, block sizing, random seed initialization, filesystem free space, CPU count, thread id, shared-memory behavior, fallocate, CPU feature probing, mkdir, and clock ticks.

## Important APIs, Types, and Functions
It defines OS enum IDs, `cpu_features`, includes the selected `os-*.h`, and supplies fallback macros for `EDQUOT`, `OS_MSG_DONTWAIT`, POSIX fadvise constants, CPU affinity, I/O priority, `OS_O_DIRECT`, huge pages, `FIO_O_NOATIME`, `OS_RAND_MAX`, preferred engine/clock/path separator, `socklen_t`, `os_ctime_r`, byte swapping, endian conversion, `os_cache_line_size()`, generic `blockdev_size()`, generic `init_random_seeds()`, `get_fs_free_size()`, `cpus_configured()`, `CPU_COUNT()`, `gettid()`, `shm_attach_to_open_removed()`, `fio_fallocate()`, `os_cpu_has()`, `fio_mkdir`, and `os_clk_tck()`.

## Control Flow
Preprocessor OS detection includes exactly one platform header or errors out. Runtime helpers are mostly simple fallbacks: read `/dev/urandom`, seek to file end for generic block size, query `sysconf()`, count CPU bits by iterating configured CPUs, or return safe unsupported defaults. Endian macros use platform byte-swap functions or generic swaps depending on configuration.

## State and Persistence
The header owns no state. Generic helpers may read random bytes or seek an fd; fallback `fio_fallocate()` sets `errno = ENOSYS`.

## Dependencies and Integration Points
Nearly all fio source includes this abstraction directly or indirectly. It is the contract that allows `options.c`, engines, file code, memory allocators, logging, verification, and platform-specific code to compile against common names.

## Risks and Edge Cases
Fallbacks often return success/no-op for unsupported features, so compile-time feature macros must be correct to avoid silently ignoring user intent. Generic `blockdev_size()` changes the fd offset with `lseek()`. Endian typecheck macros require correct integer widths. `os_clk_tck()` is external on platforms lacking `_SC_CLK_TCK`, requiring platform implementation.

## Test Signals
Builds on every supported OS, feature-matrix tests for unsupported options, endian conversion unit tests, random seed fallback tests, generic block size tests, CPU count and affinity fallback tests, and clock tick link tests are useful.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/os.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/cpu-affinity.c -->
# sources/test-tools/fio/os/windows/cpu-affinity.c

## Purpose
`windows/cpu-affinity.c` implements fio's Windows CPU mask and affinity operations, including support for Windows processor groups on systems with more than 64 logical CPUs.

## Important APIs, Types, and Functions
Exports are `first_set_cpu()`, `fio_setaffinity()`, `fio_cpuset_init()`, `fio_getaffinity()`, `fio_cpu_clear()`, `fio_cpu_set()`, `fio_cpu_isset()`, `fio_cpu_count()`, and `fio_cpuset_exit()`. Internal helpers include `print_mask()`, `last_set_cpu()`, `mask_to_group_mask()`, and `cpu_to_row_offset()`.

## Control Flow
`mask_to_group_mask()` finds the first set linear CPU, maps it to a Windows processor group by walking active groups and counts, rejects masks spanning multiple groups, extracts a group-relative bitmask from fio's row mask, and returns group plus affinity mask. `fio_setaffinity()` opens the target thread and applies `SetThreadGroupAffinity()`. `fio_getaffinity()` opens a process, requires it to be associated with exactly one group, reads `GetProcessAffinityMask()`, and expands that group-relative mask back into fio's linear rows. Bit operations map CPU indexes to row/offset and update/test/count bits.

## State and Persistence
The module stores no global state. `fio_setaffinity()` changes thread affinity. `fio_getaffinity()` returns a snapshot in caller-provided `os_cpu_mask_t`.

## Dependencies and Integration Points
It depends on `os/os.h`, Windows group affinity APIs, fio debug logging, `hweight64()`, and the mask constants from `os-windows-7.h`. It backs the `cpumask`, `cpus_allowed`, and CPU split logic used by `options.c` on Windows.

## Risks and Edge Cases
Masks spanning processor groups are rejected because Windows thread group affinity can bind a thread to one group at a time. `fio_getaffinity()` rejects processes associated with multiple groups. The row/offset helper appears suspicious: `*offset = cpu << FIO_CPU_MASK_STRIDE * *row` looks like a shift expression where modulo/subtraction was intended, so high CPU indexes should be tested carefully. Fixed `FIO_MAX_CPUS` also limits very large systems.

## Test Signals
Unit tests for first/last set CPU, row/offset mapping at 0, 63, 64, 127, and 511, affinity set/get on single-group and multi-group hosts, rejection of cross-group masks, and hweight-based counts are important.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/cpu-affinity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/dlls.c -->
# sources/test-tools/fio/os/windows/dlls.c

## Purpose
`windows/dlls.c` provides the Windows implementation of `os_clk_tck()` for platforms where `os.h` cannot use `_SC_CLK_TCK`. It dynamically queries and raises Windows timer resolution to derive a clock tick frequency for fio timing code.

## Important APIs, Types, and Functions
The sole exported function is `os_clk_tck(long *clk_tck)`. It dynamically loads `ntdll.dll` and resolves `NtQueryTimerResolution` and `NtSetTimerResolution`.

## Control Flow
If loading `ntdll.dll` or either symbol fails, it logs a debug message and uses 64 Hz as a conservative lower-bound clock frequency. Otherwise it queries minimum/maximum/current timer resolution, requests the maximum resolution, and computes ticks per second as `10000000 / maxRes` because Windows timer resolution units are 100 ns.

## State and Persistence
The function can change process/system timer resolution through `NtSetTimerResolution()`. It does not store the loaded module handle or restore prior resolution.

## Dependencies and Integration Points
It depends on Windows dynamic loading APIs and fio debug logging. `os.h` declares `os_clk_tck()` externally when `_SC_CLK_TCK` is not available, and timing/statistics code consumes the resulting frequency.

## Risks and Edge Cases
Using maximum timer resolution may have system-wide power/performance effects. Failure fallback is coarse. The library handle is not freed, which is usually acceptable for process lifetime but worth noting. Undocumented NT APIs can change behavior across Windows versions.

## Test Signals
Windows timing initialization tests, fallback behavior with mocked missing symbols, sanity checks that `clk_tck` is nonzero, and verification that high-resolution timing improves without destabilizing long fio runs are useful.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/dlls.c -->
