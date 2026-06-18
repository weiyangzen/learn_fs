# Group Research: group_1287_netbsd_src_sources_os_bsd_netbsd_src_sys_sys_systm_h_sources_os_bsd_affd341d472d

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/systm.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/systm.h

Read completely: 781 lines.

Central NetBSD kernel system declaration header.

Key elements:
- Declares global kernel identity, memory, CPU, root, dump, swap, console, panic, shutdown, and boot state.
- Defines `struct sysent`, syscall entry flags, syscall argument access via `SCARG`, and syscall tracing/debug hooks.
- Provides generic stubs such as `voidop`, `nullop`, `enodev`, `enosys`, `enoioctl`, `enxio`, and `eopnotsupp`.
- Declares kernel formatting/logging APIs, panic paths, device/interface `aprint_*` helpers, and byte formatting helpers.
- Declares `copyin`, `copyout`, `kcopy`, user fetch/store, and user compare-and-swap APIs, with KASAN/KCSAN/KMSAN wrapper selection.
- Declares clock initialization, hardclock/statclock/profiling, NTP/PPS hooks, mountroot/rootspec hooks, shutdown/power/exec/exit/fork hooks, and `uiomove` helpers.
- Defines console magic sequence state, debugger entry macros, kernel lock macros, configuration lock APIs, preemption control, and sleepability assertions.

Risks and notes:
- Very high fanout kernel interface; small changes can affect nearly every subsystem.
- Syscall flags and argument layout are ABI- and machine-dependent.
- User/kernel copy and sanitizer indirections are security-critical.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/systm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/tape.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/tape.h

Read completely: 82 lines.

Defines tape device statistics structures exposed to kernel and userland.

Key elements:
- `TAPENAMELEN` fixes exported tape device name storage.
- `struct tape_sysctl` is a 64-bit-alignment-safe statistics export format.
- `struct tape` tracks device name, busy state, read/write transfer counts, bytes, attach time, last timestamp, total busy time, and TAILQ linkage.
- Defines `TAILQ_HEAD(tapelist_head, tape)` so userland can inspect the tape stats list shape.

Risks and notes:
- `struct tape_sysctl` is an exported statistics ABI; field order and widths matter.
- Time fields are split into 32-bit seconds/useconds for stable export layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/tape.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/termios.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/termios.h

Read completely: 314 lines.

Defines NetBSD terminal control ABI.

Key elements:
- Defines `c_cc[]` indexes for POSIX and NetBSD control characters.
- Defines input, output, control, and local mode flags, including hardware/software flow control and NetBSD extensions.
- Defines `tcflag_t`, `cc_t`, `speed_t`, and `struct termios`.
- Defines `tcsetattr` action constants, standard baud rates, and extended NetBSD baud rates.
- Userland prototypes cover `cfgetispeed`, `cfsetospeed`, `tcgetattr`, `tcsetattr`, `tcdrain`, `tcflow`, `tcflush`, `tcsendbreak`, `tcgetsid`, `cfmakeraw`, and `cfsetspeed`.
- Includes `sys/ttycom.h` for non-obsolete tty ioctls and `struct winsize`.
- Exposes `tcgetwinsize` and `tcsetwinsize`.

Risks and notes:
- `struct termios`, flag values, speed constants, and control indexes are user/kernel ABI.
- Feature-test guards control namespace exposure; broadening visibility can break strict POSIX builds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/termios.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/thmap.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/thmap.h

Read completely: 62 lines.

Declares a kernel-only opaque transactional/hash map style interface.

Key elements:
- Explicitly rejects userland inclusion.
- Defines opaque `thmap_t`.
- Flags include `THMAP_NOCOPY` and `THMAP_SETROOT`.
- `thmap_ops_t` supplies allocator/free callbacks.
- API covers create/destroy, get/put/delete by key bytes, staged garbage collection, root set/get, and final GC.

Risks and notes:
- Ownership and reclamation are central; callers must coordinate `thmap_stage_gc()` and `thmap_gc()`.
- Root handling through `uintptr_t` is intentionally low-level and implementation-coupled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/thmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/threadpool.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/threadpool.h

Read completely: 85 lines.

Declares NetBSD kernel threadpool and per-CPU threadpool interfaces.

Key elements:
- Kernel-only header.
- Opaque pool types include `threadpool`, `threadpool_percpu`, and `threadpool_thread`.
- `struct threadpool_job` contains caller lock, current worker thread pointer, queue link, refcount, condition variable, callback, and fixed job name.
- APIs initialize global threadpools, acquire/release shared pools by priority, and acquire/release per-CPU pools.
- Per-CPU pool refs can be local or remote by `cpu_info`.
- Job APIs initialize/destroy/mark done, schedule jobs, cancel synchronously, and cancel asynchronously.

Risks and notes:
- Job lifetime depends on refcount, lock, condition variable, and cancellation semantics.
- Callers must use the right pool priority and respect job lock ownership.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/threadpool.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/time.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/time.h

Read completely: 355 lines.

Defines public time structures, time conversion helpers, interval timers, and clock constants.

Key elements:
- Defines `struct timeval` and includes `struct timespec` from `sys/timespec.h`.
- NetBSD extensions provide timeval/timespec conversion and arithmetic macros.
- Defines obsolete `struct timezone` for compatibility.
- Defines `struct bintime`, bintime add/sub/compare helpers, and conversions among bintime, timeval, timespec, milliseconds, microseconds, and nanoseconds.
- Defines `itimerval`, `itimerspec`, `ITIMER_*`, `CLOCK_*`, `TIMER_ABSTIME`, and NetBSD `TIMER_RELTIME`.
- Kernel inclusion pulls in `timearith.h` and `timevar.h`.
- Userland declarations include `getitimer`, `gettimeofday`, `setitimer`, `utimes`, `adjtime`, `futimes`, `lutimes`, and `settimeofday` with time64 symbol renames where applicable.

Risks and notes:
- Public structures and constants are ABI-stable.
- Time conversion macros round down by design.
- Kernel and userland visibility diverge substantially.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/time.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timearith.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/timearith.h

Read completely: 77 lines.

Declares kernel time arithmetic validation and conversion helpers.

Key elements:
- Forward-declares `itimerspec`, `timespec`, and `timeval`.
- Declares `tstohz()` and `tvtohz()` for converting durations to ticks.
- Declares `itimerfix()` and `itimespecfix()` for validating/fixing timer intervals.
- Declares `itimer_transition()` for computing interval timer transitions and overrun state.

Risks and notes:
- Conversion to ticks is boundary-sensitive for very small, huge, or invalid intervals.
- Used indirectly by kernel time APIs included from `sys/time.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timearith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timeb.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/timeb.h

Read completely: 59 lines.

Defines the deprecated `ftime(2)` ABI.

Key elements:
- `struct timeb` contains epoch seconds, milliseconds, timezone minutes west, and DST flag.
- Userland prototype declares `ftime(struct timeb *)`.

Risks and notes:
- Compatibility-only interface; new code should use modern time APIs.
- Layout remains ABI-sensitive for old binaries.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timeb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timepps.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/timepps.h

Read completely: 247 lines.

Defines the Pulse-Per-Second API and NetBSD PPS ioctl/kernel support.

Key elements:
- Declares PPS API version, `pps_handle_t`, `pps_seq_t`, `pps_timeu_t`, `pps_info_t`, and `pps_params_t`.
- Defines PPS capture, offset, wait/poll, echo, timestamp format, and kernel-consumer mode bits.
- Defines PPS ioctls for create, destroy, set/get params, get capabilities, fetch, and kernel clock binding.
- Kernel section defines reference event flags, `struct pps_state`, and `pps_capture`, `pps_event`, `pps_ref_event`, `pps_init`, and `pps_ioctl`.
- Userland section provides inline wrappers around ioctl for the PPS API.

Risks and notes:
- PPS is precision-time infrastructure; timestamp format and edge-selection mistakes affect clock discipline.
- Userland `time_pps_kcbind()` only accepts `PPS_TSFMT_TSPEC`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timepps.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timerfd.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/timerfd.h

Read completely: 67 lines.

Defines NetBSD’s Linux-compatible timerfd interface.

Key elements:
- Defines timerfd flags mapped to existing file flags: `TFD_TIMER_ABSTIME`, `TFD_TIMER_CANCEL_ON_SET`, `TFD_CLOEXEC`, and `TFD_NONBLOCK`.
- Defines `TFD_IOC_SET_TICKS` ioctl for setting expiration tick count.
- Kernel declarations expose `do_timerfd_create`, `do_timerfd_gettime`, and `do_timerfd_settime`.
- Userland declarations expose `timerfd_create`, `timerfd_gettime`, and `timerfd_settime`.

Risks and notes:
- Linux compatibility depends on matching expected flag behavior.
- `TFD_TIMER_ABSTIME` and `TFD_TIMER_CANCEL_ON_SET` reuse open flag values intentionally.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timerfd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/times.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/times.h

Read completely: 65 lines.

Defines the POSIX `times(3)` process accounting ABI.

Key elements:
- Ensures `clock_t` is available from machine ANSI definitions.
- `struct tms` records user/system CPU time for the process and terminated children.
- Userland prototype declares `times(struct tms *)` with legacy symbol rename guard.

Risks and notes:
- `struct tms` is stable user ABI.
- Clock tick interpretation depends on system configuration and `sysconf(_SC_CLK_TCK)`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/times.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timespec.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/timespec.h

Read completely: 52 lines.

Defines standalone `struct timespec`.

Key elements:
- Includes `<sys/ansi.h>` and defines `time_t` when supplied by machine ANSI headers.
- `struct timespec` contains `time_t tv_sec` and `long tv_nsec`.

Risks and notes:
- This is a small but central ABI type used by clocks, timers, filesystems, sockets, and process interfaces.
- Field type changes would be ABI-breaking.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timespec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timetc.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/timetc.h

Read completely: 95 lines.

Defines kernel timecounter interface.

Key elements:
- Rejects normal userland inclusion; allowed for `_KERNEL` and `_KMEMUSER`.
- Defines `MAX_TCNAMELEN`.
- `struct timecounter` provides counter read callback, optional PPS poll callback, mask, frequency, name, quality, private pointer, and list linkage.
- Kernel declarations expose current `timecounter`, frequency query, attach/detach, set clock, tick notification, and bad-counter reporting.
- Optionally declares `_kern_timecounter` sysctl node.

Risks and notes:
- Timecounter quality/frequency/mask fields directly affect system timekeeping.
- Hardware counters must satisfy rollover assumptions documented in the header.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timetc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timevar.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/timevar.h

Read completely: 296 lines.

Defines kernel timekeeping and interval timer internals.

Key elements:
- Defines `struct itimer_ops`, `struct itimer`, `struct ptimer`, and `struct ptimers`.
- Supports real, virtual, profiling, monotonic, and POSIX timers.
- Declares precise and fast time query APIs: `binuptime`, `nanouptime`, `microuptime`, `bintime`, `nanotime`, `microtime`, and `get*` variants.
- Declares clock get/set/resolution helpers, nanosleep, settimeofday, timer create/set/get, rate checking, timecounter initialization, and timer lifecycle helpers.
- Provides `time_second`, `time_uptime`, and `time_uptime32` via atomic loads when 64-bit atomic load/store is available.
- Defines monotonic/wall conversion helpers.

Risks and notes:
- Timer state and locking are concurrency-sensitive.
- Fast time macros trade precision for performance.
- Timer table constants reserve slots 0-3 for `setitimer(2)` timers and expose POSIX timer limits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timevar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timex.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/timex.h

Read completely: 264 lines.

Defines NTP clock discipline public and kernel interface.

Key elements:
- Defines `NTP_API` version 4.
- Defines PLL/FLL performance constants such as `MAXPHASE`, `MAXFREQ`, `MINSEC`, `MAXSEC`, and `MAXTC`.
- Defines `MOD_*` control mode bits and `STA_*` clock status bits, including PPS, leap second, nanosecond, mode, and clock source status.
- Defines `TIME_*` clock states.
- `struct ntptimeval` exports current time, max/estimated error, TAI offset, and time state.
- `struct timex` carries clock discipline parameters and PPS statistics.
- Kernel declarations expose NTP update, adjtime, gettime, timestatus, `timecounter_lock`, and `time_adjtime`.
- Userland declarations expose `ntp_gettime` and `ntp_adjtime`.

Risks and notes:
- `struct timex` and `struct ntptimeval` are user/kernel ABI.
- Some fields are interpreted as microseconds or nanoseconds depending on `STA_NANO`.
- Read-only status bits must not be accepted as arbitrary user-settable state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/timex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/tls.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/tls.h

Read completely: 60 lines.

Defines machine-selected TLS TCB layout support.

Key elements:
- Includes machine type definitions.
- Builds only when `__HAVE_TLS_VARIANT_I` or `__HAVE_TLS_VARIANT_II` is defined.
- Errors if both TLS variants are enabled simultaneously.
- Defines `struct tls_tcb` layout differently for variant I and variant II.
- Declares runtime linker TLS allocation/free functions `_rtld_tls_allocate` and `_rtld_tls_free`.

Risks and notes:
- TCB layout is ABI-critical for threads, libc, runtime linker, and machine TLS access sequences.
- Exactly one TLS variant may be active.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/tls.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/tprintf.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/tprintf.h

Read completely: 44 lines.

Declares terminal/session printf helpers.

Key elements:
- Defines `tpr_t` as `struct session *`.
- Declares `tprintf_open`, `tprintf_close`, and printf-like `tprintf`.

Risks and notes:
- Thin interface around session-associated output.
- Format string checking is enabled through `__printflike`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/tprintf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/trace.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/trace.h

Read completely: 114 lines.

Defines legacy kernel trace event constants and conditional tracing macros.

Key elements:
- Defines filesystem buffer trace points for bread hits/misses, writes, read-ahead, exec demand faults, release, and realloc.
- Defines memory allocation and paging trace points.
- Defines `TR_NFLAGS`, `TRCSIZ`, and legacy `vtrace` operation constants.
- Under `_KERNEL && TRACE`, declares trace globals and `trace()` macro.
- Without `TRACE`, `trace()` compiles to no-op.

Risks and notes:
- Filesystem trace event numbers are stable within this legacy tracing facility.
- The `pack(v,b)` macro assumes vnode/mount fields and packs filesystem id with block number.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/tree.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/tree.h

Read completely: 761 lines.

Provides macro-generated intrusive splay tree and red-black tree implementations.

Key elements:
- Defines `SPLAY_HEAD`, `SPLAY_ENTRY`, accessors, rotations, prototypes, generation macros, and traversal helpers.
- Splay operations include insert, remove, find, next, min, max, and foreach.
- Defines `RB_HEAD`, `RB_ENTRY`, color/accessor macros, rotations, prototypes, generation macros, and traversal helpers.
- Red-black operations include insert, remove, find, nearest-find, next, previous, min, max, safe traversal, and reverse traversal.
- Supports `RB_AUGMENT` hook for augmented trees.
- Provides static generation variants for RB trees.

Risks and notes:
- This is macro infrastructure; comparison function correctness and intrusive field ownership are caller responsibilities.
- Splay lookups mutate tree shape.
- RB augmentation hooks must be correct across rotations and removal paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/tree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/tty.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/tty.h

Read completely: 340 lines.

Defines core kernel tty structures, state flags, queues, and driver APIs.

Key elements:
- Includes termios, select, selinfo, mutex, condition variable, queue, and callout support.
- Defines `struct clist` ring-buffer queues for raw, canonical, and output data.
- Defines `enum ttysigtype`.
- `struct tty` contains queues, condition variables, callout, line discipline, device, state, flags, process/session links, select state, termios, window size, driver callbacks, watermarks, signal queues, softc, and reference count.
- Defines tty state flags `TS_*`, character classification constants, modem commands, and `TTY_*` character flags.
- Provides controlling-terminal/background macros.
- Defines global tty list head for userland visibility.
- Kernel declarations cover clist operations, tty open/read/write/ioctl/poll/flush/sleep/signal/lifetime/locking APIs.

Risks and notes:
- Tty structure and state transitions are concurrency-sensitive.
- Queue internals are documented as private to `tty_subr.c`.
- Driver callbacks and `t_refcnt`/`constty` interaction are lifetime-sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/tty.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ttychars.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ttychars.h

Read completely: 62 lines.

Defines old BSD tty control-character compatibility structure.

Key elements:
- `struct ttychars` stores erase, kill, interrupt, quit, start, stop, EOF, break, suspend, delayed suspend, reprint, flush, word erase, and literal-next characters.
- Includes `ttydefaults.h` only under `USE_OLD_TTY`.

Risks and notes:
- Compatibility-only surface for older tty APIs.
- Layout is user-visible when old tty support is used.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ttychars.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ttycom.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ttycom.h

Read completely: 183 lines.

Defines tty ioctl ABI and window-size/pty structures.

Key elements:
- Defines public `struct winsize`.
- Under NetBSD/ioctl exposure, defines `struct ptmget`, `_PATH_PTMDEV`, modem status bits, tty ioctls, line discipline name length, pty packet bits, device flag bits, queue-size ioctls, and line discipline numbers.
- Includes path-sized pty names via `PATH_MAX`.
- Provides ioctl numbers for termios get/set, break/DTR control, process group/session, packet mode, window size, console, controlling tty, queue size, and pty allocation helpers.

Risks and notes:
- Ioctl numbers and structure layouts are ABI.
- `struct winsize` is intentionally visible even through strict termios inclusion.
- `ptmget` embeds `PATH_MAX`, so size depends on system limit ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ttycom.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ttydefaults.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ttydefaults.h

Read completely: 115 lines.

Defines system-wide default terminal settings.

Key elements:
- Defines default input, output, local, control flags, and default speed.
- Defines default control characters such as EOF, erase, interrupt, status, kill, quit, suspend, start/stop, literal-next, discard, word erase, and reprint.
- Defines `CTRL(x)` helper and compatibility aliases.
- Under `_KERNEL` and `TTYDEFCHARS`, defines or declares `ttydefchars[NCCS]`.

Risks and notes:
- Defaults influence first-open terminal behavior.
- The kernel array uses termios indexes and must stay synchronized with `NCCS` and control character constants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ttydefaults.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ttydev.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ttydev.h

Read completely: 60 lines.

Compatibility header for old tty speed constants.

Key elements:
- Defines old compact baud-code values only under `USE_OLD_TTY`.
- Includes values from `B0` through `B115200`.

Risks and notes:
- Compatibility-only header.
- These values differ from modern termios baud constants, which are actual speeds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ttydev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/types.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/types.h

Read completely: 380 lines.

Defines foundational NetBSD system types and selected compatibility declarations.

Key elements:
- Includes machine type, ANSI, integer, and feature-test headers.
- Defines fixed-width integer types and BSD aliases.
- Defines filesystem/storage types such as `blkcnt_t`, `blksize_t`, `fsblkcnt_t`, `fsfilcnt_t`, `daddr_t`, `dev_t`, `ino_t`, `off_t`, and `nlink_t`.
- Defines IDs and limits-related types: `gid_t`, `uid_t`, `pid_t`, `lwpid_t`, `id_t`, `rlim_t`, `cpuid_t`, `psetid_t`.
- Provides NetBSD compatibility aliases and deprecated endian transclusion.
- Declares `union __semun` for kernel/libc/kmemuser syscall argument use.
- Declares off_t-based `lseek`, `ftruncate`, and `truncate` under `_NETBSD_SOURCE`.
- Defines `major`, `minor`, and `makedev` encoding for `dev_t`.
- Defines kernel/standalone boolean compatibility, simple SET/ISSET/CLR macros, and cross-subsystem forward typedefs.

Risks and notes:
- This is a foundational ABI header; type width changes are broad ABI breaks.
- Device number encoding macros are storage/device ABI-sensitive.
- Namespace exposure is controlled by feature-test macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ucontext.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ucontext.h

Read completely: 115 lines.

Defines user context layout and kernel context helpers.

Key elements:
- Defines `uc_flags` bits for signal mask, stack, CPU, FPU, and reserved machine-dependent flags.
- Requires machine definitions for `_UC_TLSBASE`, `_UC_SETSTACK`, and `_UC_CLRSTACK`.
- Includes machine `mcontext.h`.
- Defines `ucontext_t` as `struct __ucontext`.
- `struct __ucontext` contains flags, link, signal mask, stack, machine context, and optional machine padding.
- Provides optional alignment/size macros.
- Kernel declarations cover get/set user context and CPU machine-context validation.
- Kernel asserts `sizeof(ucontext_t) == __UCONTEXT_SIZE` when defined.

Risks and notes:
- Signal delivery, context switching APIs, and machine ABI depend on this layout.
- Machine-dependent flag allocation must use the reserved `_UC_MD_BIT*` slots.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ucontext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ucred.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ucred.h

Read completely: 56 lines.

Defines user-visible credential export structure.

Key elements:
- Includes kernel or userland limit headers for `NGROUPS_MAX`.
- `struct uucred` contains unused compatibility field, effective uid/gid, group count, and group list.

Risks and notes:
- Comment explicitly says userland’s view should not change.
- `cr_groups[NGROUPS_MAX]` ties layout to configured group limit ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ucred.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/uidinfo.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/uidinfo.h

Read completely: 59 lines.

Declares per-user resource accounting structure and helpers.

Key elements:
- `struct uidinfo` stores hash linkage, uid, process count, LWP count, lock count, semaphore count, and socket buffer size.
- Declares counters for processes, LWPs, semaphores, and socket buffer accounting.
- Declares `uid_find` and `uid_init`.

Risks and notes:
- Resource accounting correctness affects per-user limits and denial-of-service controls.
- `chgsbsize` takes both `uidinfo` and tracked usage pointer, so callers must preserve accounting consistency.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/uidinfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/uio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/uio.h

Read completely: 123 lines.

Defines scatter/gather I/O structures and kernel uio state.

Key elements:
- Defines public `struct iovec`.
- Under NetBSD exposure, defines `enum uio_rw`, `enum uio_seg`, and optional `struct uio`.
- Kernel automatically exposes `struct uio`.
- `struct uio` contains iovec pointer/count, file offset, residual byte count, read/write direction, and vmspace.
- Defines deprecated `UIO_MAXIOV` and kernel `UIO_SMALLIOV`.
- Declares `uio_setup_sysspace`, userland `readv/writev/preadv/pwritev`, and kernel `ureadc`.

Risks and notes:
- `iovec` is public ABI.
- Kernel `uio` is central to VFS/device I/O paths; residual and segment-space handling are correctness-critical.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/uio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/un.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/un.h

Read completely: 112 lines.

Defines UNIX-domain socket public address structures, options, and selected kernel hooks.

Key elements:
- Defines `sa_family_t` when needed.
- Keeps `SUNPATHLEN` at 104 for binary compatibility.
- Defines `struct sockaddr_un` with length, family, and path.
- NetBSD extensions define `SOL_LOCAL`, credential-passing options, connection wait, and peer-id option.
- Defines `struct unpcbid` for peer pid/euid/egid.
- Kernel declarations cover UNIX socket initialization, locks, connect, connect2, disposal, and externalization.
- Userland `SUN_LEN` computes initialized sockaddr length under `_NETBSD_SOURCE`.

Risks and notes:
- `SUNPATHLEN` is intentionally historical ABI.
- Credential-passing options interact with security boundaries.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/un.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/unistd.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/unistd.h

Read completely: 347 lines.

Defines POSIX option constants, access/lseek constants, pathconf/sysconf names, and selected NetBSD extensions.

Key elements:
- Defines compile-time POSIX version constants and supported option macros.
- Defines access mode constants `F_OK`, `X_OK`, `W_OK`, `R_OK`.
- Defines `SEEK_SET`, `SEEK_CUR`, `SEEK_END`, and NetBSD `L_SET/L_INCR/L_XTND`.
- Defines `fsync_range` flags `FDATASYNC`, `FFILESYNC`, and `FDISKSYNC`.
- Defines `_PC_*` pathconf constants including ACL and hole-size extensions.
- Defines many `_SC_*` sysconf constants for POSIX, X/Open, realtime, thread, spawn, shared memory, physical pages, processor counts, and scheduler limits.
- Defines `_CS_PATH`.

Risks and notes:
- Numeric `_PC_*` and `_SC_*` constants are user ABI.
- Comments note some values are embedded in other headers, so renumbering is hazardous.
- POSIX option macros must match actual sysconf behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/unistd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/unpcb.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/unpcb.h

Read completely: 109 lines.

Defines kernel UNIX-domain socket protocol control block.

Key elements:
- Includes `sys/un.h` and mutex definitions.
- `struct unpcb` tracks backing socket, bound vnode, fake inode, connected peer, reference list, bound address, stream lock, address length, receive-buffer snapshots, creation time, flags, and peer credentials.
- Defines flags for old/new credential requests, connection wait, valid peer ids, bind-time peer id, busy state.
- Provides `sotounpcb(so)` cast helper.

Risks and notes:
- Comments document vnode references and peer-reference list semantics; lifetime is delicate.
- Creation time supports POSIX pipe stat behavior.
- Credential validity flags protect whether peer ids may be exposed to userland.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/unpcb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/userconf.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/userconf.h

Read completely: 39 lines.

Declares boot-time user configuration interface.

Key elements:
- Includes `sys/cpu.h`.
- Declares `userconf_bootinfo`, `userconf_init`, `userconf_prompt`, and `userconf_parse`.

Risks and notes:
- Small declaration header for boot configuration flow.
- `userconf_parse(char *)` implies mutable command buffer parsing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/userconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/userret.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/userret.h

Read completely: 68 lines.

Defines machine-independent work before returning to user mode.

Key elements:
- Includes lockdebug, interrupt, and psref debug support.
- Inline `mi_userret(struct lwp *)` disables preemption, asserts no leaked kernel lock or big-lock count, checks reschedule/userret exception state, re-enables preemption, and calls `lwp_userret` when needed.
- Adds lockdebug and psref barriers and asserts no preemption or psref leaks.

Risks and notes:
- This path runs at syscall/trap return to user mode and is scheduler/signal sensitive.
- Assertions encode important invariants: no kernel lock leak, no blocked lock count, no psref leaks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/userret.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/utsname.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/utsname.h

Read completely: 62 lines.

Defines `uname(3)` ABI structure.

Key elements:
- Defines `_SYS_NMLN` as 256 and `SYS_NMLN` under `_NETBSD_SOURCE`.
- `struct utsname` contains fixed-size strings for sysname, nodename, release, version, and machine.
- Declares `uname(struct utsname *)`.

Risks and notes:
- Fixed string lengths are ABI.
- This is simple but widely used system identity reporting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/utsname.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/uuid.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/uuid.h

Read completely: 82 lines.

Defines DCE-compatible UUID representation and helpers.

Key elements:
- Defines `_UUID_NODE_LEN` and `_UUID_STR_LEN`.
- `struct uuid` contains time fields, clock sequence fields, and 6-byte node.
- Kernel section exposes string formatting, endian encode/decode, and UUID generation helpers.
- Userland defines `uuid_t` alias and declares `uuidgen`.

Risks and notes:
- Struct layout matches DCE UUID representation and serialized encodings.
- Endian helpers are important for on-disk/on-wire UUID formats.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/uuid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/verified_exec.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/verified_exec.h

Read completely: 112 lines.

Defines Veriexec flags, ioctls, modes, statuses, and kernel verification hooks.

Key elements:
- Defines entry flags for direct execution, indirect execution, file open, and untrusted storage.
- Defines pseudo-device ioctls for load, table size, delete, query, dump, and flush.
- Defines strict modes: learning, IDS, IPS, lockdown.
- Defines fingerprint and per-page fingerprint status values.
- Kernel section declares fingerprint operation callbacks, initialization, fingerprint algorithm registration, file add/delete, verify, lookup, table delete, convert, dump, flush, purge, remove/rename/unmount/open checks.

Risks and notes:
- Security-sensitive execution/open policy interface.
- Ioctl and property-list formats are user/kernel contract.
- Vnode/mount hooks are tightly coupled to VFS mutation and exec/open paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/verified_exec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/vfs_syscalls.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/vfs_syscalls.h

Read completely: 93 lines.

Declares shared VFS syscall helper routines for native and compatibility code.

Key elements:
- Includes system types and filesystem type definitions.
- Forward-declares stat, statvfs, and quotactl args.
- Declares stat/statat/file-handle stat helpers.
- Declares statvfs/getvfsstat helpers, including copy callback support.
- Declares time-setting helpers for `utimes`, `utimens`, and `utimensat`.
- Declares open-by-pathbuf, file-handle copyin/free, and `dofhopen`.
- Declares link/unlink/rename/mknod/chmod/chown/access/mkdir/symlink/quotactl/sync/chdir/fchdir helpers.
- Declares `vfs_syncwait`, `chdir_lookup`, `change_root`, and mount compatibility names.

Risks and notes:
- Central VFS syscall factoring point; helper semantics affect native and compat syscall behavior.
- `enum uio_seg` parameters distinguish user vs kernel address spaces for path/time buffers.
- File-handle helpers are sensitive to copyin size validation and lifetime.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/vfs_syscalls.h -->