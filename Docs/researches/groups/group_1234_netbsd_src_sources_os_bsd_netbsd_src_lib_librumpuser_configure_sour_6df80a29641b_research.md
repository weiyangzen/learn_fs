# Group Research: group_1234_netbsd_src_sources_os_bsd_netbsd_src_lib_librumpuser_configure_sour_6df80a29641b

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/configure -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/configure

## Summary
Generated GNU Autoconf 2.69 `configure` script for `rumpuser-posix 999`, producing `rumpuser_config.h` from `rumpuser_config.h.in`.

## Key Details
- Implements standard Autoconf shell setup: portable shell re-exec, option parsing, cache handling, compiler/preprocessor discovery, canonical build/host/target detection, and `config.status` generation.
- Enables large-file probing through `_FILE_OFFSET_BITS`, `_LARGE_FILES`, and related compiler option checks.
- Checks standard headers plus rumpuser-specific portability headers: `sys/param.h`, `sys/sysctl.h`, `sys/disk.h`, `sys/disklabel.h`, `sys/dkio.h`, `sys/atomic.h`, `paths.h`, and `sys/cdefs.h`.
- Checks types `clockid_t` and `register_t`.
- Checks functions used by the POSIX rumpuser layer, including `kqueue`, `chflags`, `strsuftoll`, `setprogname`, `getprogname`, `getenv_r`, memory-alignment routines, `arc4random_buf`, `getsubopt`, `fsync_range`, `__quotactl`, `utimensat`, `preadv`, and `pwritev`.
- Probes `clock_gettime` and `clock_nanosleep` directly and via `-lrt`, and probes `dlinfo` via `-ldl`.
- Detects `struct sockaddr_in.sin_len`, two-argument and three-argument `pthread_setname_np`, and whether `ioctl` takes an `int` command argument.

## Notes
This is a generated artifact; `configure.ac` is the compact authoritative source for the project-specific checks. The generated script still matters for bootstrap behavior on systems without Autoconf.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/configure -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/configure.ac -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/configure.ac

## Summary
Autoconf input defining POSIX rumpuser portability probes.

## Key Details
- Initializes package `rumpuser-posix` version `999` with bug reports to the rumpkernel GitHub URL.
- Generates `rumpuser_config.h`, uses `build-aux`, and declares C as the language.
- Requests large-file support and canonical target detection.
- Checks headers, types, functions, libraries, and structure members needed by the portable rumpuser implementation.
- Uses custom compile tests under `-Werror` for `sys/cdefs.h`, `pthread_setname_np` signatures, and `ioctl` command-argument type.
- Notes regeneration steps: run `autoreconf -iv`, update `rumpuser_port.h`, remove `autom4te.cache`, then commit/pull up.

## Notes
This file explains why `rumpuser_port.h` embeds NetBSD-default generated values while non-NetBSD/buildrump users can include a generated `rumpuser_config.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/configure.ac -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber.c

## Summary
Implements the fiber-based rumpuser backend: a cooperative ucontext scheduler plus rumpuser thread, lock, condition-variable, clock, parameter, and LWP glue.

## Key Details
- Maintains runnable and exited thread TAILQs, a `current_thread`, optional scheduler hook, and per-thread `ucontext_t` state.
- Schedules cooperatively with round-robin runnable selection and millisecond wakeup times based on `CLOCK_MONOTONIC`.
- Allocates default stacks with `mmap`; externally supplied stacks are marked with `THREAD_EXTSTACK` and are not unmapped on cleanup.
- Supports joinable fiber threads through `THREAD_MUSTJOIN`, `THREAD_JOINED`, and an internal join-wait queue.
- Provides sleep helpers for relative monotonic, absolute monotonic, and absolute realtime waits.
- Implements `rumpuser_init`, clock operations, environment-backed parameters, console/debug output, exit, signal forwarding, thread create/exit/join, mutexes, rwlocks, condition variables, and `curlwp` operations.
- Mutexes are owner-aware and recursive for the same LWP; condition-variable waits temporarily unschedule the rump kernel and release/reacquire the associated mutex.
- RW lock wakeup policy prefers queued writers over readers.

## Notes
The implementation assumes cooperative execution and effectively one active VCPU; `rumpuser_mutex_enter_nowrap` explicitly relies on no preemption.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber.h

## Summary
Internal declarations for the fiber rumpuser scheduler.

## Key Details
- Defines `struct thread` with name, LWP pointer, cookie, wakeup time, TAILQ link, `ucontext_t`, flags, and thread-local errno.
- Defines scheduler/thread flags: runnable, must-join, joined, external stack, and timed out.
- Sets default fiber stack size to 65536 bytes.
- Declares scheduler, wake/block, main-thread initialization, thread exit, scheduler hook, absolute realtime sleep, thread creation, and runnable-flag helpers.

## Notes
This header exposes enough internals for fiber BIO and service-provider support to share the cooperative scheduler.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber_bio.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber_bio.c

## Summary
Fiber backend implementation of rump block I/O.

## Key Details
- Performs reads with `pread` and writes with `pwrite` at the requested disk offset.
- Translates host `errno` through `rumpuser__errtrans`.
- For synchronous writes, uses `fsync_range(..., FDATASYNC, ...)` when available, otherwise falls back to `fsync`.
- Always invokes the supplied biodone callback with transferred byte count and translated error.

## Notes
Unlike the pthread BIO implementation, this backend runs I/O directly in the caller's cooperative fiber context.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber_bio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber_sp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber_sp.c

## Summary
Stub service-provider functions for the fiber backend.

## Key Details
- `rumpuser_sp_init` returns success and `rumpuser_sp_fini` is a no-op.
- Signal raise, copyin/copyout, string copy, and anonymous mmap service-provider operations all call `abort()`.
- The file comment states these service-provider functions are not supported for fibers yet.

## Notes
This is an intentional unsupported surface rather than a partial implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber_sp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser.c

## Summary
Core POSIX rumpuser hypercall support for the normal threaded backend.

## Key Details
- Validates `RUMPUSER_VERSION`, initializes randomness and threading, and stores the hypervisor upcall table in `rumpuser__hyp`.
- Implements rump clock queries and sleeps with `clock_gettime`, `nanosleep`, and optionally `clock_nanosleep`.
- Unschedules the rump kernel around blocking sleep operations, then reschedules with the saved lock count.
- Supplies parameters such as `RUMP_NCPU`, hostname, and arbitrary environment variables via `getenv_r`.
- Defaults `RUMP_NCPU` to `2`, with `RUMP_NCPU=host` mapped to `_SC_NPROCESSORS_ONLN`.
- Provides putchar, process exit/panic behavior, errno setting, debug printing, host signal raising, and page-size query.

## Notes
The absolute monotonic sleep path falls back to realtime polling plus relative sleeps when `clock_nanosleep` is unavailable.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_bio.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_bio.c

## Summary
Threaded POSIX block I/O backend for rumpuser.

## Key Details
- Defines a fixed 128-entry circular queue protected by a mutex and condition variable.
- `dobio` executes `pread`/`pwrite`, optional write sync, error translation, and biodone callback invocation.
- A worker thread registers with the rump kernel as a new LWP before servicing queued I/O.
- `RUMP_THREADS=0` disables the worker thread and executes BIO synchronously.
- Queue producers block when the ring is full and signal the worker on enqueue.
- The callback is invoked while the rump kernel is scheduled, then the worker unschedules again.

## Notes
Initialization is lazy and protected by a double-checked `inited` flag under `biomtx`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_bio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_component.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_component.c

## Summary
Exports stable component-facing wrappers around rumpuser scheduling, LWP, and errno translation operations.

## Key Details
- `rumpuser_component_unschedule` unschedules the rump kernel and returns the saved lock count as an opaque cookie.
- `rumpuser_component_schedule` restores scheduling from that cookie.
- Provides component helpers for creating/releasing kernel-thread LWP context, reading current LWP, and switching LWP.
- `rumpuser_component_errtrans` exposes host-to-rump errno translation.

## Notes
The file comments distinguish these component ABI functions from the broader rump kernel/hypervisor contract versioned by `RUMPUSER_VERSION`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_component.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_component.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_component.h

## Summary
Public declarations for rumpuser component helper functions.

## Key Details
- Declares schedule/unschedule wrappers.
- Declares host-error translation.
- Declares component kernel-thread and LWP helper functions.
- Uses an include guard for `_RUMP_RUMPUSER_COMPONENT_H_`.

## Notes
The header references `struct lwp` without defining it, expecting consumers to share the rump kernel type context.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_component.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_config.h.in -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_config.h.in

## Summary
Autoheader template for generated `rumpuser_config.h`.

## Key Details
- Contains `#undef` entries for all Autoconf-detected headers, functions, types, libraries, and package metadata.
- Covers rumpuser portability features such as clocks, dynamic linker support, filesystem sync, aligned allocation, environment helpers, vector I/O, pthread naming signatures, and NetBSD-style device headers.
- Includes large-file knobs `_FILE_OFFSET_BITS` and `_LARGE_FILES`.
- Defines `_DARWIN_USE_64_BIT_INODE` to `1` unless already defined.

## Notes
This file is data for `config.status`; consumers use the generated header or the NetBSD defaults embedded in `rumpuser_port.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_config.h.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_daemonize.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_daemonize.c

## Summary
Implements interlocked daemonization for rumpuser services.

## Key Details
- Prevents concurrent daemonization with a static `isdaemonizing` flag.
- Uses `socketpair(PF_LOCAL, SOCK_STREAM)` so the parent can wait for the child to report initialization status without SIGPIPE concerns.
- Forks before rump initialization creates threads; the child calls `setsid`.
- Allows `RUMP_STDOUT` and `RUMP_STDERR` to redirect standard output/error before forking.
- `rumpuser_daemonize_done` redirects stdin, and by default stdout/stderr, to `/dev/null` on success.
- Sends the final initialization error code to the parent, which exits with that status.

## Notes
The implementation intentionally does not `chdir("/")`; callers must decide whether to change directories.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_daemonize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_dl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_dl.c

## Summary
Bootstraps dynamically linked rump modules, components, event counters, sysctl setup functions, and kernel symbol tables.

## Key Details
- Compiles the main implementation only for ELF systems with `HAVE_DLINFO`; otherwise `rumpuser_dl_bootstrap` is a no-op.
- Uses `dlopen(NULL)` and `dlinfo(..., RTLD_DI_LINKMAP, ...)` to inspect the dynamic linker link map.
- Handles static-link heuristics by returning when no useful dynamic link map exists.
- Walks objects last-to-first to process likely dependencies before dependents.
- Collects ELF symbol and string tables from `librump*` objects and the main object, accepting symbols beginning with `rump`, `RUMP`, or `__`.
- Supports ELF32/ELF64 through accessor macros, and supports both SysV `DT_HASH` and GNU `DT_GNU_HASH` symbol counts.
- Adjusts dynamic-section pointers differently for glibc, Solaris, DragonFly, FreeBSD, NetBSD, musl-like systems, and MIPS exceptions.
- Processes link sets for modules, rump components, sysctl functions, and event counters via `dlsym` start/stop symbols.

## Notes
The symbol table is rebuilt into contiguous malloc-backed buffers before being handed to the rump kernel through `symload`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_dl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_errtrans.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_errtrans.c

## Summary
Translates host `errno` values into NetBSD/rump kernel errno numbers.

## Key Details
- Returns zero unchanged.
- Uses `#ifdef`-guarded switch cases so the same source builds on hosts with different errno macro sets.
- Maps common POSIX, networking, RPC, filesystem, authentication, message, STREAMS, and overflow errors to fixed rump errno numbers.
- Handles aliases such as `EWOULDBLOCK == EAGAIN` and `ENOTSUP == EOPNOTSUPP` without duplicate case labels.
- Defaults unknown host errors to rump `EINVAL` (`22`).

## Notes
The comment says the table was pseudo-automatically generated but is intended to be edited for duplicate errno values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_errtrans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_file.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_file.c

## Summary
POSIX file and device helper hypercalls for rumpuser.

## Key Details
- `rumpuser_getfileinfo` classifies paths as directory, regular file, block device, character device, or other.
- For device sizes, it tries NetBSD disklabel and wedge ioctls when available; otherwise it falls back to `lseek(fd, 0, SEEK_END)` and reports unsupported if that fails.
- `rumpuser_open` maps rump open flags to host `open` flags and wraps the blocking call with kernel unschedule/reschedule.
- `rumpuser_close` unschedules, calls `fsync`, closes the fd, and reschedules.
- Vector reads/writes cast `struct rumpuser_iovec` to `struct iovec`, using `readv`/`writev`, `preadv`/`pwritev` when available, or lseek-plus-vector-I/O fallback under unscheduling.
- `rumpuser_syncfd` validates sync flags and uses `fsync_range` when available, otherwise `fsync`.

## Notes
The file notes this code is expected to move to a new driver in a future hypercall revision.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_int.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_int.h

## Summary
Internal helper header for rumpuser implementation files.

## Key Details
- Declares the shared `rumpuser__hyp` hypervisor upcall table.
- Defines inline `rumpkern_unsched` and `rumpkern_sched` wrappers around backend schedule hooks.
- Provides `KLOCK_WRAP`, `DOCALL`, and `DOCALL_KLOCK` macros for host calls that must be made outside rump kernel scheduling.
- Defines fatal-check macros `NOFAIL` and `NOFAIL_ERRNO`.
- Declares internal thread init, signal translation, errno translation, and random initialization helpers.
- Defines `ET` so NetBSD returns native errors directly while other hosts translate them to rump errno values.

## Notes
This header centralizes the schedule-boundary convention used across file, BIO, clock, and component code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_int.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_mem.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_mem.c

## Summary
Memory allocation and mapping hypercalls for rumpuser.

## Key Details
- `rumpuser_malloc` uses `posix_memalign`, defaulting zero alignment to pointer-size alignment.
- Invalid alignment from `posix_memalign` is treated as a fatal programming error and aborts after printing a message.
- `rumpuser_free` delegates to `free`.
- `rumpuser_anonmmap` maps anonymous private memory with read/write and optional execute permissions.
- Uses `MAP_ALIGNED(alignbit)` when available; otherwise warns if explicit alignment was requested.
- `rumpuser_unmap` calls `munmap`.

## Notes
Errors are returned through `ET`, so non-NetBSD hosts translate mapping/allocation errno values to rump errno values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_port.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_port.h

## Summary
Primary portability header for building librumpuser on NetBSD and non-NetBSD hosts.

## Key Details
- Embeds NetBSD-default configure results when `RUMPUSER_CONFIG` is not defined.
- Includes generated `rumpuser_config.h` when `RUMPUSER_CONFIG` is defined.
- Enables `_GNU_SOURCE` on Linux/GNU/glibc targets and adjusts FreeBSD visibility for C11 interfaces.
- Provides fallbacks for `MIN`, `MAX`, `getsubopt`, `clockid_t`, `clock_gettime`, `getenv_r`, `posix_memalign`, `aligned_alloc`, and numerous NetBSD-style compiler/utility macros.
- Supplies platform-specific atomic and type fixes for Android, Apple, Solaris file-offset handling, and NetBSD MIPS N32 `register_t`.
- Defines rumpuser lock alignment as `COHERENCY_UNIT` on NetBSD and `64` elsewhere.
- Normalizes socket constants, `MSG_NOSIGNAL`, `INFTIM`, sockaddr length setting, path/hostname limits, and `TIMEVAL_TO_TIMESPEC`.

## Notes
This header is the compatibility contract that lets the rest of librumpuser mostly use NetBSD-flavored APIs while compiling on POSIX-like hosts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_port.h -->