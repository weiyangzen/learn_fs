# Group Research: group_1207_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_sys_Lint_sbrk_c_sourc_c91677480148

Scope: subset A from `Docs/research_subset_a.md`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_sbrk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_sbrk.c

## Purpose
Provides a lint-only stub for `sbrk`.

## Key Elements
Includes `<unistd.h>` and defines `sbrk(intptr_t incr)` returning `NULL`.

## Dependencies
Used by NetBSD libc lint builds, not runtime syscall dispatch.

## Behavior/Risks
It intentionally ignores the argument and returns a dummy pointer; correctness matters only for lint signature coverage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_sbrk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_syscall.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_syscall.c

## Purpose
Provides a lint-only variadic stub for `syscall`.

## Key Elements
Includes `<stdarg.h>` and `<unistd.h>` and defines `syscall(int arg1, ...)` returning `0`.

## Dependencies
Consumed by libc lint generation/checking.

## Behavior/Risks
No runtime behavior; it exists to make lint understand the public variadic syscall interface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Makefile.inc

## Purpose
Builds the NetBSD libc system-call wrapper layer, including architecture-specific assembly stubs, C compatibility glue, lint stubs, and syscall manual-page links.

## Key Elements
Adds syscall wrapper sources such as `accept4.c`, `sched.c`, `sigwait.c`, `statvfs.c`, and time/offset compatibility glue. It generates assembly stubs from `SYS.h` using `RSYSCALL`, `PSEUDO`, `PSEUDO_NOERROR`, `WSYSCALL`, and related macros; creates lint files with `makelintstub`; and declares extensive `MAN`/`MLINKS` mappings.

## Dependencies
Depends on `${ARCHDIR}/sys`, `${.CURDIR}/sys`, `${DESTDIR}/usr/include/sys/syscall.h`, `${ARCHDIR}/SYS.h`, `makelintstub`, make conditionals such as `RUMPRUN`/`MKLINT`, and generated temporary assembly targets.

## Behavior/Risks
The file encodes ABI compatibility details for old 64-bit offset padding, `*50` time syscalls, no-error syscalls, pseudo syscalls, weak syscall aliases, and architecture overrides. Build correctness depends on generated names matching syscall headers and on architecture-specific `.S` files taking precedence over default C glue.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/__sigaction_siginfo.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/__sigaction_siginfo.c

## Purpose
Implements the libc compatibility entry point `__sigaction_siginfo`.

## Key Elements
Builds the signal trampoline symbol name from `__SIGTRAMP_SIGINFO_VERSION` and calls `__sigaction_sigtramp(sig, act, oact, trampoline, version)`.

## Dependencies
Uses `<signal.h>`, `extern.h`, `__sigaction_sigtramp`, and the architecture-provided `__sigtramp_siginfo_*` trampoline symbol.

## Behavior/Risks
This is a versioned ABI shim; comments state it should become plain `sigaction` at the next libc major bump. The trampoline version must match kernel/libc signal ABI expectations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/__sigaction_siginfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/accept4.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/accept4.c

## Purpose
Implements `accept4` in terms of NetBSD's `paccept`.

## Key Elements
Passes socket, address, address length, `NULL` signal mask, and flags to `paccept`.

## Dependencies
Uses `<sys/socket.h>` and libc namespace handling.

## Behavior/Risks
Thin semantic adapter; behavior is delegated to `paccept`, so flag validation and accept behavior live there.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/accept4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/adjtime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/adjtime.c

## Purpose
Implements `adjtime` with a syscall-first path and fallback to `/dev/clockctl`.

## Key Elements
Calls `____adjtime50`; if it fails with `EPERM`, opens `_PATH_CLOCKCTL` write-only close-on-exec, caches `__clockctl_fd`, and issues `CLOCKCTL_ADJTIME`.

## Dependencies
Uses `sys/clockctl.h`, `ioctl`, `open`, `errno`, `____adjtime50`, and shared global `__clockctl_fd`.

## Behavior/Risks
Open errors intentionally preserve the original `EPERM`. Once clockctl is opened, later calls always use it, so shared global fd state affects all related time-setting wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/adjtime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/clock_getcpuclockid.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/clock_getcpuclockid.c

## Purpose
Provides the POSIX-style `clock_getcpuclockid` API.

## Key Elements
Calls `clock_getcpuclockid2(P_PID, (id_t)pid, clock_id)` and returns an error number instead of setting `errno` as the function result.

## Dependencies
Uses `<time.h>`, `<errno.h>`, `pid_t`, `id_t`, and `P_PID`.

## Behavior/Risks
It saves and restores `errno`, so callers receive errors through the return value. This wrapper must preserve POSIX's non-`-1` error convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/clock_getcpuclockid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/clock_settime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/clock_settime.c

## Purpose
Implements `clock_settime` with a syscall-first path and fallback to `/dev/clockctl`.

## Key Elements
Calls `____clock_settime50`; if it fails with `EPERM`, opens `_PATH_CLOCKCTL`, caches `__clockctl_fd`, and issues `CLOCKCTL_CLOCK_SETTIME`.

## Dependencies
Uses `sys/clockctl.h`, `ioctl`, `open`, `errno`, `____clock_settime50`, and shared global `__clockctl_fd`.

## Behavior/Risks
Open failure hides the open error and restores `EPERM`. The shared clockctl fd is reused by other time-changing wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/clock_settime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/epoll.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/epoll.c

## Purpose
Provides compatibility wrappers for `epoll_create`, `epoll_wait`, and `epoll_pwait`.

## Key Elements
`epoll_create` validates positive size and calls `epoll_create1(0)`. `epoll_wait` delegates to `epoll_pwait` with no signal mask. `epoll_pwait` converts millisecond timeout to `timespec` and calls `epoll_pwait2`.

## Dependencies
Uses `<sys/epoll.h>`, `<sys/time.h>`, `<errno.h>`, and `epoll_create1`/`epoll_pwait2`.

## Behavior/Risks
Negative timeout becomes infinite wait. Millisecond-to-nanosecond conversion is simple and bounded by `int timeout`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/epoll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/eventfd_read.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/eventfd_read.c

## Purpose
Implements the convenience `eventfd_read` helper.

## Key Elements
Reads exactly one `eventfd_t` from the descriptor; on full read stores it in `*valp` and returns `0`.

## Dependencies
Uses `<sys/eventfd.h>`, `read`, and `errno`.

## Behavior/Risks
Partial reads are treated as impossible but mapped to `EIO`; descriptor behavior is delegated to the kernel eventfd implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/eventfd_read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/eventfd_write.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/eventfd_write.c

## Purpose
Implements the convenience `eventfd_write` helper.

## Key Elements
Writes one `eventfd_t` value to the descriptor and returns `0` only for a complete write.

## Dependencies
Uses `<sys/eventfd.h>`, `write`, and `errno`.

## Behavior/Risks
Partial writes are treated as impossible but mapped to `EIO`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/eventfd_write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/fdiscard.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/fdiscard.c

## Purpose
Provides C glue for `fdiscard` with 64-bit offset padding.

## Key Elements
Declares `__fdiscard(int, int, off_t, off_t)` and calls it with a zero pad argument.

## Dependencies
Uses `<sys/types.h>`, `<sys/syscall.h>`, and `<unistd.h>`.

## Behavior/Risks
ABI compatibility shim for old compiler/syscall calling conventions; real behavior is in `__fdiscard`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/fdiscard.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/ftruncate.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/ftruncate.c

## Purpose
Provides `ftruncate` C glue with 64-bit offset padding.

## Key Elements
Weak-aliases `ftruncate` to `_ftruncate` where supported and calls `__ftruncate(fd, 0, length)`.

## Dependencies
Uses syscall glue declaration `__ftruncate`.

## Behavior/Risks
Thin ABI shim; correctness depends on matching the kernel syscall's padded argument layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/ftruncate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/lseek.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/lseek.c

## Purpose
Provides `lseek` C glue with 64-bit offset padding.

## Key Elements
Weak-aliases `lseek` to `_lseek` and calls `__lseek(fd, 0, offset, whence)`.

## Dependencies
Uses syscall glue declaration `__lseek`.

## Behavior/Risks
ABI shim only; offset and `whence` validation occur in the underlying syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/lseek.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/makelintstub -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/makelintstub

## Purpose
Generates C lint stubs for syscall assembly wrappers.

## Key Elements
Parses options `-n`, `-p`, `-o`, and `-s`; preprocesses the syscall header with `${CPP} -D_LIBC -C`; extracts syscall prototype comments; emits generated includes, ANSI and K&R-style function definitions, and dummy zero returns.

## Dependencies
Requires `CPP` in the environment, POSIX shell tools, `sed`, and syscall prototype comments in `syscall.h`.

## Behavior/Risks
Fails if syscall metadata is missing or if both `-n` and `-p` are given. Generated signatures depend on exact comment format in the preprocessed syscall header.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/makelintstub -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/mknodat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/mknodat.c

## Purpose
Provides `mknodat` C glue with device argument padding.

## Key Elements
Calls `__mknodat(fd, path, mode, 0, dev)`.

## Dependencies
Uses `<sys/stat.h>` and syscall glue declaration `__mknodat`.

## Behavior/Risks
ABI shim only; path, mode, and device validation are handled by the kernel syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/mknodat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/mmap.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/mmap.c

## Purpose
Provides `mmap` C glue with 64-bit offset padding.

## Key Elements
Weak-aliases `mmap` to `_mmap` and calls `__mmap(addr, len, prot, flags, fd, 0, offset)`.

## Dependencies
Uses `<sys/mman.h>` and syscall glue declaration `__mmap`.

## Behavior/Risks
Thin ABI adapter; all mapping validation and failure behavior are delegated to the syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/mmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/ntp_adjtime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/ntp_adjtime.c

## Purpose
Implements `ntp_adjtime` with direct syscall use and `/dev/clockctl` fallback.

## Key Elements
Calls `__ntp_adjtime(tp)` first; on `EPERM` opens cached `_PATH_CLOCKCTL` and issues `CLOCKCTL_NTP_ADJTIME`. It returns `args.retval` after a successful ioctl because ioctl cannot directly supply the syscall return value.

## Dependencies
Uses `<sys/timex.h>`, `sys/clockctl.h`, `ioctl`, `open`, and shared `__clockctl_fd`.

## Behavior/Risks
`ntp_adjtime` can be callable by unprivileged users for read-only mode, so fallback is only attempted after `EPERM`. Shared clockctl fd state affects subsequent calls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/ntp_adjtime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/posix_fadvise.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/posix_fadvise.c

## Purpose
Provides `posix_fadvise` C glue for the NetBSD `__posix_fadvise50` syscall.

## Key Elements
Calls `__posix_fadvise50(fd, 0, offset, size, hint)`.

## Dependencies
Uses `<sys/fcntl.h>` and the `__posix_fadvise50` declaration.

## Behavior/Risks
Preserves POSIX return-value convention through the underlying no-error syscall wrapper; offset padding must match the ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/posix_fadvise.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/posix_fallocate.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/posix_fallocate.c

## Purpose
Provides `posix_fallocate` C glue with 64-bit offset padding.

## Key Elements
Calls `__posix_fallocate(fd, 0, off, len)`.

## Dependencies
Uses `<fcntl.h>` and syscall glue declaration `__posix_fallocate`.

## Behavior/Risks
No-error syscall wrapper; result convention depends on generated `PSEUDO_NOERROR` handling in the build.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/posix_fallocate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/posix_madvise.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/posix_madvise.c

## Purpose
Implements `posix_madvise` as a direct wrapper around `madvise`.

## Key Elements
Returns `madvise(addr, len, advice)`.

## Dependencies
Uses `<sys/mman.h>`.

## Behavior/Risks
Unlike some POSIX APIs that return error numbers directly, this wrapper follows `madvise` syscall-style return behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/posix_madvise.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/ppoll.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/ppoll.c

## Purpose
Implements `ppoll` in terms of NetBSD `pollts`.

## Key Elements
Passes file descriptors, count, timeout `timespec`, and signal mask directly to `pollts`.

## Dependencies
Uses `<sys/poll.h>` and `<sys/time.h>`.

## Behavior/Risks
Semantic adapter only; timeout and signal-mask behavior comes from `pollts`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/ppoll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/pread.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/pread.c

## Purpose
Provides `pread` C glue with 64-bit offset padding and syscall aliases.

## Key Elements
Weak-aliases `pread` and `_pread` to `_sys_pread`; `_sys_pread` calls `__pread(fd, buf, nbyte, 0, offset)`.

## Dependencies
Uses syscall declarations `_sys_pread` and `__pread`.

## Behavior/Risks
ABI adapter only. Alias setup is important because generated weak syscall wrappers use `_sys_*` names.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/pread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/preadv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/preadv.c

## Purpose
Provides `preadv` C glue with 64-bit offset padding.

## Key Elements
Calls `__preadv(fd, iovp, iovcnt, 0, offset)`.

## Dependencies
Uses `<sys/uio.h>` and syscall glue declaration `__preadv`.

## Behavior/Risks
Thin ABI shim; iovec validation and I/O behavior are delegated to the syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/preadv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/pwrite.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/pwrite.c

## Purpose
Provides `pwrite` C glue with 64-bit offset padding and syscall aliases.

## Key Elements
Weak-aliases `pwrite` and `_pwrite` to `_sys_pwrite`; `_sys_pwrite` calls `__pwrite(fd, buf, nbyte, 0, offset)`.

## Dependencies
Uses syscall declarations `_sys_pwrite` and `__pwrite`.

## Behavior/Risks
ABI adapter only; aliasing must match generated syscall wrapper names.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/pwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/pwritev.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/pwritev.c

## Purpose
Provides `pwritev` C glue with 64-bit offset padding.

## Key Elements
Calls `__pwritev(fd, iovp, iovcnt, 0, offset)`.

## Dependencies
Uses `<sys/uio.h>` and syscall glue declaration `__pwritev`.

## Behavior/Risks
Thin ABI shim; validation and I/O semantics are in the underlying syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/pwritev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/sched.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/sched.c

## Purpose
Implements POSIX scheduling and NetBSD affinity convenience wrappers over lower-level scheduler syscalls.

## Key Elements
Maps `sched_setparam`, `sched_getparam`, `sched_setscheduler`, and `sched_getscheduler` to `_sched_setparam`/`_sched_getparam` for all LWPs. Provides priority min/max queries, round-robin interval reporting, and `sched_getaffinity_np`/`sched_setaffinity_np`.

## Dependencies
Uses `<sched.h>`, `<signal.h>`, `sysconf`, `kill`, `_sched_*` syscalls, and `cpuset_t`.

## Behavior/Risks
Uses `P_ALL_LWPS` to target all LWPs in a process. `sched_setscheduler` returns the old policy on success. Invalid policies set `EINVAL`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/semctl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/semctl.c

## Purpose
Implements public variadic `semctl` over the kernel `____semctl50` interface.

## Key Elements
Reads a `union __semun` variadic argument for commands that need one and passes its address to `____semctl50`.

## Dependencies
Uses System V IPC semaphore headers, `<stdarg.h>`, and `____semctl50`.

## Behavior/Risks
Only selected commands consume the vararg. If a caller omits the required argument for those commands, behavior follows normal variadic C misuse.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/semctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/settimeofday.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/settimeofday.c

## Purpose
Implements `settimeofday` with syscall-first behavior and `/dev/clockctl` fallback.

## Key Elements
Defines global `__clockctl_fd = -1`; calls `____settimeofday50`, opens `_PATH_CLOCKCTL` on `EPERM`, and issues `CLOCKCTL_SETTIMEOFDAY`.

## Dependencies
Uses `sys/clockctl.h`, `ioctl`, `open`, `errno`, and `____settimeofday50`.

## Behavior/Risks
This file owns the shared clockctl fd used by related wrappers. It preserves original `EPERM` if opening clockctl fails.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/settimeofday.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/sigqueue.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/sigqueue.c

## Purpose
Implements POSIX `sigqueue` through NetBSD `sigqueueinfo`.

## Key Elements
Zeroes a `siginfo_t`, fills signal number, `SI_QUEUE`, sender pid, effective uid, and supplied value, then calls `sigqueueinfo`.

## Dependencies
Uses `<signal.h>`, `memset`, `getpid`, `geteuid`, and `sigqueueinfo`.

## Behavior/Risks
The wrapper constructs userland signal metadata; delivery and permission checks are handled by `sigqueueinfo`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/sigqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/sigtimedwait.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/sigtimedwait.c

## Purpose
Implements public `sigtimedwait` around the internal syscall.

## Key Elements
Copies a non-null timeout into a local `timespec` before passing it to `__sigtimedwait`; passes `NULL` otherwise.

## Dependencies
Uses `<signal.h>`, `<time.h>`, and `__sigtimedwait`.

## Behavior/Risks
The local copy protects the caller's timeout object from syscall-side modification.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/sigtimedwait.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/sigwait.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/sigwait.c

## Purpose
Implements `sigwait` using `__sigtimedwait`.

## Key Elements
Calls `__sigtimedwait(set, NULL, NULL)`, restores the caller's original `errno`, returns the captured error number on failure, and stores the signal number on success.

## Dependencies
Uses `<signal.h>`, `<errno.h>`, and weak aliasing to `_sigwait`.

## Behavior/Risks
Preserves POSIX convention: error number is returned directly and `errno` is restored.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/sigwait.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/sigwaitinfo.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/sigwaitinfo.c

## Purpose
Implements `sigwaitinfo` as an infinite-timeout `sigtimedwait`.

## Key Elements
Weak-aliases public `sigwaitinfo` to `_sigwaitinfo`; `_sigwaitinfo` returns `sigtimedwait(set, info, NULL)`.

## Dependencies
Uses `<signal.h>` and `sigtimedwait`.

## Behavior/Risks
Thin adapter; blocking and signal selection semantics are delegated to `sigtimedwait`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/sigwaitinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/statvfs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/statvfs.c

## Purpose
Implements default-waiting variants of VFS statistics calls.

## Key Elements
`statvfs`, `fstatvfs`, and `fhstatvfs` call `statvfs1`, `fstatvfs1`, and `fhstatvfs1` with `ST_WAIT`.

## Dependencies
Uses `<sys/statvfs.h>`.

## Behavior/Risks
Forces `ST_WAIT` behavior for these standard APIs; alternate no-wait behavior requires the `*vfs1` APIs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/statvfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/swapon.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/swapon.c

## Purpose
Implements legacy `swapon` using `swapctl`.

## Key Elements
Calls `swapctl(SWAP_ON, __UNCONST(name), 0)`.

## Dependencies
Uses `<sys/swap.h>` and `swapctl`.

## Behavior/Risks
Casts away constness because `swapctl` takes a mutable pointer; actual swap activation behavior is in the kernel.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/swapon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/truncate.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/truncate.c

## Purpose
Provides `truncate` C glue with 64-bit offset padding.

## Key Elements
Calls `__truncate(path, 0, length)`.

## Dependencies
Uses syscall glue declaration `__truncate`.

## Behavior/Risks
ABI shim only; path and length validation are delegated to the syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/truncate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/vadvise.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/vadvise.c

## Purpose
Provides obsolete `vadvise` compatibility symbol.

## Key Elements
Ignores the argument, sets `errno = EINVAL`, and returns `-1`.

## Dependencies
Uses `<errno.h>` and `__USE`.

## Behavior/Risks
Always fails; retained for ABI/source compatibility rather than functionality.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/sys/vadvise.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/Makefile.inc

## Purpose
Builds libc termios helper functions and their manual-page links.

## Key Elements
Adds termios source files for speed accessors, raw-mode setup, drain/flow/flush/get/set operations, process group/session helpers, and window-size helpers.

## Dependencies
Uses `${.CURDIR}/termios` path setup and NetBSD make `SRCS`, `MAN`, and `MLINKS`.

## Behavior/Risks
Build metadata only; missing a source here would omit a public termios helper from libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/cfgetispeed.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/cfgetispeed.c

## Purpose
Returns the input speed from a `struct termios`.

## Key Elements
Asserts non-null input and returns `t->c_ispeed`.

## Dependencies
Uses `<termios.h>` and libc weak aliasing.

## Behavior/Risks
No validation of the stored speed value; caller must pass a valid termios pointer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/cfgetispeed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/cfgetospeed.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/cfgetospeed.c

## Purpose
Returns the output speed from a `struct termios`.

## Key Elements
Asserts non-null input and returns `t->c_ospeed`.

## Dependencies
Uses `<termios.h>` and libc weak aliasing.

## Behavior/Risks
No validation of the stored speed value.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/cfgetospeed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/cfmakeraw.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/cfmakeraw.c

## Purpose
Converts an existing `termios` structure to raw mode.

## Key Elements
Clears input translation/control flags, disables output post-processing, disables echo/canonical/signals/extensions, clears size/parity, and sets `CS8`.

## Dependencies
Uses `<termios.h>`.

## Behavior/Risks
Modifies only the provided structure; caller must apply it with `tcsetattr`. Source notes an unresolved `MIN/TIME` setting question.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/cfmakeraw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/cfsetispeed.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/cfsetispeed.c

## Purpose
Sets the input speed field in a `termios` structure.

## Key Elements
Assigns `t->c_ispeed = speed` and returns `0`.

## Dependencies
Uses `<termios.h>` and libc weak aliasing.

## Behavior/Risks
Does not validate `speed`; validation occurs later when applied to a device.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/cfsetispeed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/cfsetospeed.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/cfsetospeed.c

## Purpose
Sets the output speed field in a `termios` structure.

## Key Elements
Assigns `t->c_ospeed = speed` and returns `0`.

## Dependencies
Uses `<termios.h>` and libc weak aliasing.

## Behavior/Risks
Does not validate `speed`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/cfsetospeed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/cfsetspeed.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/cfsetspeed.c

## Purpose
Sets both input and output speeds in a `termios` structure.

## Key Elements
Assigns `t->c_ispeed = t->c_ospeed = speed` and returns `0`.

## Dependencies
Uses `<termios.h>` and libc weak aliasing.

## Behavior/Risks
Does not validate `speed`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/cfsetspeed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcdrain.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcdrain.c

## Purpose
Waits for terminal output to drain.

## Key Elements
Calls `ioctl(fd, TIOCDRAIN, 0)`.

## Dependencies
Uses `<sys/ioctl.h>` and `<termios.h>`.

## Behavior/Risks
Actual blocking and error behavior are provided by the terminal driver.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcdrain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcflow.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcflow.c

## Purpose
Controls terminal software/hardware flow.

## Key Elements
Maps `TCOOFF`/`TCOON` to `TIOCSTOP`/`TIOCSTART`; for `TCIOFF`/`TCION`, fetches current attributes and writes the configured stop/start control character if not disabled.

## Dependencies
Uses `ioctl`, `tcgetattr`, `write`, and `<termios.h>`.

## Behavior/Risks
Invalid actions set `EINVAL`. For input flow actions, write failures propagate.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcflow.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcflush.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcflush.c

## Purpose
Flushes terminal input/output queues.

## Key Elements
Maps `TCIFLUSH`, `TCOFLUSH`, and `TCIOFLUSH` to `FREAD`, `FWRITE`, or both, then calls `ioctl(fd, TIOCFLUSH, &com)`.

## Dependencies
Uses `<sys/ioctl.h>`, `<fcntl.h>`, and `<termios.h>`.

## Behavior/Risks
Invalid selector sets `EINVAL`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcflush.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetattr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetattr.c

## Purpose
Fetches terminal attributes.

## Key Elements
Calls `ioctl(fd, TIOCGETA, t)`.

## Dependencies
Uses `<sys/ioctl.h>` and `<termios.h>`.

## Behavior/Risks
Requires a valid output `termios` pointer; device-specific errors come from ioctl.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetpgrp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetpgrp.c

## Purpose
Returns the foreground process group for a terminal.

## Key Elements
Calls `ioctl(fd, TIOCGPGRP, &s)` and converts a returned `-1` to a large invalid positive value for SVID compatibility.

## Dependencies
Uses `<sys/ioctl.h>`, `<termios.h>`, and `pid_t`.

## Behavior/Risks
Compatibility mapping can produce a value that is intentionally not a valid process group.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetpgrp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetsid.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetsid.c

## Purpose
Returns the terminal session id.

## Key Elements
Calls `ioctl(fd, TIOCGSID, &s)` and returns it as `pid_t`.

## Dependencies
Uses `<sys/ioctl.h>`, `<termios.h>`, and `pid_t`.

## Behavior/Risks
Thin ioctl wrapper; terminal driver supplies errors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetsid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetwinsize.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetwinsize.c

## Purpose
Gets terminal window size.

## Key Elements
Defines `_NETBSD_SOURCE` as needed for ioctl constants and calls `ioctl(fd, TIOCGWINSZ, ws)`.

## Dependencies
Uses `<sys/ioctl.h>` and `<termios.h>`.

## Behavior/Risks
Thin ioctl wrapper; caller must provide writable `struct winsize`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetwinsize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcsendbreak.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcsendbreak.c

## Purpose
Sends a terminal break condition.

## Key Elements
Sets break with `TIOCSBRK`, sleeps for 400 ms, then clears break with `TIOCCBRK`.

## Dependencies
Uses `ioctl`, `nanosleep`, and `<termios.h>`.

## Behavior/Risks
Ignores `len`; failure to clear break is returned as an error after the sleep.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcsendbreak.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcsetattr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcsetattr.c

## Purpose
Sets terminal attributes with standard timing options.

## Key Elements
If `TCSASOFT` is present, copies the termios structure and sets `CIGNORE`. Maps `TCSANOW`, `TCSADRAIN`, and `TCSAFLUSH` to `TIOCSETA`, `TIOCSETAW`, and `TIOCSETAF`.

## Dependencies
Uses `<sys/ioctl.h>` and `<termios.h>`.

## Behavior/Risks
Invalid option values set `EINVAL`. The local copy prevents mutating caller memory for `TCSASOFT`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcsetattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcsetpgrp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcsetpgrp.c

## Purpose
Sets the foreground process group for a terminal.

## Key Elements
Casts `pid_t pgrp` into an `int` and calls `ioctl(fd, TIOCSPGRP, &s)`.

## Dependencies
Uses `<sys/ioctl.h>`, `<termios.h>`, and `pid_t`.

## Behavior/Risks
Assumes process group ids fit in `int`, matching the ioctl ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcsetpgrp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcsetwinsize.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcsetwinsize.c

## Purpose
Sets terminal window size.

## Key Elements
Defines `_NETBSD_SOURCE` as needed for ioctl constants and calls `ioctl(fd, TIOCSWINSZ, ws)`.

## Dependencies
Uses `<sys/ioctl.h>` and `<termios.h>`.

## Behavior/Risks
Thin ioctl wrapper; terminal driver handles validation and signaling side effects.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/termios/tcsetwinsize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/thread-stub/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/thread-stub/Makefile.inc

## Purpose
Adds libc's non-pthread thread stub sources.

## Key Elements
Includes `bsd.own.mk`, sets `.PATH`, and adds `__isthreaded.c`, `thread-stub.c`, and `thread-stub-init.c`.

## Dependencies
NetBSD make infrastructure and libc thread-stub directory.

## Behavior/Risks
Build metadata only; omitting these files would break weak pthread/reentrant fallback behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/thread-stub/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/thread-stub/__isthreaded.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/thread-stub/__isthreaded.c

## Purpose
Defines the libc global thread-state flag.

## Key Elements
Defines `int __isthreaded = 0`.

## Dependencies
Used by libc reentrant stubs and overridden/updated when libpthread is active.

## Behavior/Risks
Single global controls whether stubs abort if used after threading is enabled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/thread-stub/__isthreaded.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/thread-stub/thread-stub-init.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/thread-stub/thread-stub-init.c

## Purpose
Provides weak initialization and errno hooks for non-pthread libc builds.

## Key Elements
Under `_REENTRANT`, weak-aliases `__libc_thr_init` to a no-op startup stub and `__libc_thr_errno` to a stub that aborts with `SIGABRT`.

## Dependencies
Uses `reentrant.h`, `<signal.h>`, and weak aliases.

## Behavior/Risks
`__libc_thr_errno_stub` intentionally aborts; real threaded errno handling must be supplied by libpthread.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/thread-stub/thread-stub-init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/thread-stub/thread-stub.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/thread-stub/thread-stub.c

## Purpose
Supplies libc thread-operation stubs used when applications are not linked with libpthread.

## Key Elements
Defines weak aliases for pthread/thread, mutex, mutexattr, condition variable, rwlock, TSD, once, signal mask, self, yield, create, exit, cancel-state, equality, and CPU helpers. Lock-like operations no-op while checking `__isthreaded`; thread creation returns `EOPNOTSUPP`; join/detach handle self specially; yield calls `_sys_sched_yield`.

## Dependencies
Uses `reentrant.h`, `tsd.h`, `__isthreaded`, `SIGABRT`, `sigprocmask`, `_sys_sched_yield`, `exit`, and libc weak/strong alias macros.

## Behavior/Risks
If these stubs are used after threading is active, many paths abort. The TSD implementation is minimal, process-global, does not run destructors, and does not recycle deleted keys.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/thread-stub/thread-stub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/time/Makefile

## Purpose
Upstream tzcode/tzdb makefile for building timezone tools, libc time support archive, timezone data, checks, installs, and release tarballs.

## Key Elements
Defines configurable package/version/install paths, data forms, leap-second modes, compiler feature macros, source/data lists, build targets for `zic`, `zdump`, `date`, `tzselect`, `libtz.a`, generated `.zi` data, `leapseconds`, validation checks, reproducible timestamps, and distribution/signature targets.

## Dependencies
Uses POSIX make/sh, C compiler, `awk`, `curl`, `gpg`, `tar`, `gzip`, optional `git`, tzdb source data, scripts such as `ziguard.awk`, `zishrink.awk`, `checktab.awk`, and source files like `localtime.c`, `asctime.c`, `difftime.c`, `strftime.c`, `zic.c`, and `zdump.c`.

## Behavior/Risks
This is portable upstream infrastructure, not NetBSD-only libc build glue. It contains network-fetch and release-signing targets, many platform feature switches, and validation policy embedded in make recipes; downstream changes can affect generated timezone data and reproducibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/time/Makefile.inc

## Purpose
Integrates selected time-library sources and manuals into NetBSD libc.

## Key Elements
Adds `asctime.c`, `difftime.c`, `localtime.c`, `getdate.c`, `strftime.c`, and `strptime.c`; installs related manpages and links; adds `-DUSG_COMPAT -DSUPPORT_POSIX2008`; suppresses one `strftime` format warning.

## Dependencies
Uses NetBSD make variables and sources in `${.CURDIR}/time`.

## Behavior/Risks
Controls which upstream tzcode pieces become libc. Feature macros affect exported compatibility variables and POSIX behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/asctime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/time/asctime.c

## Purpose
Implements `asctime`, `asctime_r`, `ctime`, `ctime_r`, and `ctime_rz` using fixed C/POSIX formatting rather than locale-sensitive `strftime`.

## Key Elements
Formats weekday/month names from static English tables, handles null `tm` by returning placeholder text and `EINVAL`, guards buffer overflow with `snprintf`, pads traditional four-digit years where possible, and supports static or public `asctime_r` depending on POSIX feature macros.

## Dependencies
Uses `private.h`, `namespace.h`, `stdio`, `localtime`, `localtime_r`, `localtime_rz`, and timezone types.

## Behavior/Risks
Static `asctime` storage is shared and non-thread-safe by design. Out-of-range years may use expanded spacing or overflow failure with `EOVERFLOW`; null `timeptr` returns a placeholder string if a buffer exists.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/asctime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/checktab.awk -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/time/checktab.awk

## Purpose
Validates tzdb country and zone table consistency.

## Key Elements
Reads `iso3166.tab` and a selected zone table, verifies column counts, country-code format/order/duplicates, coordinate format, country use, comment necessity, zone coverage, and rule usage. It includes temporary/special accepted zones and can emit warnings for countries without zones.

## Dependencies
Uses awk with tab-separated parsing for tables, then space-separated parsing for zone data files.

## Behavior/Risks
Reports errors to stderr and exits nonzero on inconsistencies. Special-case zone exemptions are embedded, so policy updates require script maintenance.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/checktab.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/difftime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/time/difftime.c

## Purpose
Computes `double` difference between two `time_t` values while avoiding overflow where possible.

## Key Elements
Uses direct double subtraction when safe, unsigned arithmetic when `time_t` is unsigned, `uintmax_t` when wide enough, same-sign subtraction for signed values, and long double fallback for opposite-sign wide cases.

## Dependencies
Uses `private.h` for `time_t` and `TYPE_SIGNED`.

## Behavior/Risks
Carefully avoids signed overflow in most cases. The final wide opposite-sign fallback can suffer double rounding, as documented in the source.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/difftime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/getdate.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/time/getdate.c

## Purpose
Implements POSIX `getdate` using templates from the `DATEMSK` environment variable.

## Key Elements
Validates `DATEMSK`, stats and opens the template file, parses each non-comment logical line with `fparseln`, tries `strptime`, fills unspecified fields from current local time or future matching weekday/month/hour rules, normalizes with `mktime`, and returns a static `struct tm`.

## Dependencies
Uses `getenv`, `stat`, `fopen`, `fparseln`, `strptime`, `time`, `localtime`, `mktime`, and global `getdate_err`.

## Behavior/Risks
Not thread-safe because it uses static result storage and global `getdate_err`. Timezone scanning is intentionally limited to current localtime behavior. One template mismatch path returns without closing the opened file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/getdate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/leapseconds.awk -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/time/leapseconds.awk

## Purpose
Generates tzdb `leapseconds` data from `leap-seconds.list`.

## Key Elements
Prints a fixed explanatory header, skips blanks/comments, tracks previous TAI-UTC offset, detects positive or negative leap corrections, maps January/July effective dates to previous December/June end dates, and emits `Leap` lines marked stationary UTC.

## Dependencies
Uses awk and expects input fields from public-domain `leap-seconds.list`.

## Behavior/Risks
Output depends on month names and field positions in the source list. It ignores the first observed offset and emits changes only when a previous offset exists.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/leapseconds.awk -->