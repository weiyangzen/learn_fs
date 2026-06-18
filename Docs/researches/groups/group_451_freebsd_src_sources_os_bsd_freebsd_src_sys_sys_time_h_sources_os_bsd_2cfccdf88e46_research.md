# Group Research: group_451_freebsd_src_sources_os_bsd_freebsd_src_sys_sys_time_h_sources_os_bsd_2cfccdf88e46

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/freebsd-src`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/time.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/time.h

Core FreeBSD time ABI and kernel timekeeping interface header.

Key responsibilities:
- Defines `struct timezone`, DST constants, interval timer IDs, `struct itimerval`, `struct clockinfo`, and CPU clock selector constants.
- Under BSD visibility, defines `struct bintime`, fixed-point `sbintime_t` constants, bintime arithmetic helpers, sbintime/bintime/timespec/timeval conversions, and scaling helpers with explicit floor/ceil rounding.
- Provides timespec/timeval/timer macros for clear, isset, compare, add, subtract, and valid interval checks.
- Under `_KERNEL` or `_STANDALONE`, declares clock driver hooks, exported timecounter state, UTC/uptime timestamp accessors, boottime accessors, itimer/rate/tvtohz helpers, tick conversion macros, and frequency conversion macros.
- For userland, declares `setitimer`, `utimes`, and BSD/XSI time APIs including `adjtime`, `gettimeofday`, `settimeofday`, and `clock_getcpuclockid2`.

Dependencies:
- Includes `_timeval`, `types`, `timespec`, and `_clock_id`; kernel consumers depend on global `hz`, timecounter state, and `struct bintime`.

Notable risks:
- This is a high-visibility ABI and kernel timing contract; layout, rounding behavior, and macro semantics affect libc, drivers, timers, schedulers, and filesystem timestamp code.
- The conversion helpers intentionally use floor/ceil asymmetrically; replacing them with ordinary rounding would change interval and timeout guarantees.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/time.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timeb.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/timeb.h

Deprecated System V/BSD `ftime(2)` compatibility header.

Key responsibilities:
- Emits a GCC warning for includes of this deprecated header outside libutil internals.
- Defines `time_t` if needed.
- Defines `struct timeb` with seconds, milliseconds, timezone minutes west of UTC, and DST flag fields.
- Declares userland `ftime(struct timeb *)` when not compiling kernel code.

Dependencies:
- Includes `sys/_types.h`; userland prototypes use `sys/cdefs.h`.

Notable risks:
- Retained solely for compatibility; new code should not depend on millisecond-era `ftime()` semantics.
- The warning is intentionally suppressed for `_IN_LIBUITL`, preserving build compatibility for internal legacy users.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timeb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timeet.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/timeet.h

Kernel event timer interface between hardware timer drivers and machine-independent timer code.

Key responsibilities:
- Defines `struct eventtimer` with list linkage, name, capability flags, quality, active state, frequency, minimum/maximum periods, start/stop callbacks, event/deregister callbacks, private argument fields, and sysctl node.
- Defines event timer capabilities for periodic, one-shot, per-CPU, C3-stop, and power-of-two divisor behavior.
- Declares global event timer mutex and `ET_LOCK`/`ET_UNLOCK` wrappers.
- Declares driver registration/deregistration/frequency-change APIs and consumer APIs for finding, initializing, starting, stopping, banning, and freeing event timers.
- Exposes the `_kern_eventtimer` sysctl tree when `SYSCTL_DECL` is available.

Dependencies:
- Kernel-only; includes lock, mutex, queue, and time headers.

Notable risks:
- Header guard names reference `TIMEEC`/`TIMETC` inconsistently, but the guard still protects this file.
- Correct capability flags and quality ordering are critical to timer selection and suspend/CPU-idle behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timeet.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timeffc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/timeffc.h

Feed-forward clock public and kernel interface for FreeBSD's alternate clock synchronization model.

Key responsibilities:
- Defines `struct ffclock_estimate`, the user/kernel estimate passed by synchronization daemons, including update time, counter value, next leap-second counter, period estimate, error bounds, status, total leap seconds, and pending leap adjustment.
- Under kernel BSD visibility, declares sysclock/ffclock sysctl trees, system clock selectors, feed-forward status bits, snapshot conversion flags, feedback and feed-forward clock info records, and `struct sysclock_snap`.
- Declares snapshot, conversion, reset, counter-read, last-tick, absolute-time, interval-time, and error-bound APIs for feed-forward clocks.
- Declares full wrapper families for feed-forward and feedback absolute/uptime accessors in bintime, timespec, and timeval forms.
- Provides inline `*_fromclock()` selectors that route to feedback or feed-forward implementations by `SYSCLOCK_*`.
- In userland, declares `ffclock_getcounter`, `ffclock_getestimate`, and `ffclock_setestimate`.

Dependencies:
- Includes `_ffcounter`; kernel declarations depend on `bintime`, `timespec`, `timeval`, sysctl declarations, and timecounter internals.

Notable risks:
- Flag combinations alter whether timestamps are fast, monotonic-interpolated, leap-second-adjusted, or uptime-relative.
- This header deliberately exposes specialized feedback-clock entry points but warns they are not general-consumption APIs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timeffc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timepps.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/timepps.h

FreeBSD implementation of the RFC 2783 Pulse Per Second timing API.

Key responsibilities:
- Defines PPS API version, handle and sequence types, NTP fixed-point timestamp type, PPS timestamp union, normal and feed-forward PPS info records, and PPS parameter record.
- Defines capture, offset, echo, wait/poll, timestamp-format, timestamp-clock, and kernel-consumer constants.
- Defines ioctl argument records for fetch, feed-forward-counter fetch, and kernel-consumer binding.
- Defines `PPS_IOC_*` ioctl numbers for create, destroy, params, capabilities, fetch, kernel bind, and feed-forward counter fetch.
- Under `_KERNEL`, defines `struct pps_state`, ABI/lock flags, and kernel PPS entry points including capture, event, init, ioctl, and `hardpps`.
- In userland, provides inline `time_pps_*` wrappers around ioctls, including timeout handling that maps null timeout to negative timespec fields.

Dependencies:
- Includes `_ffcounter`, `ioccom`, and `time`.

Notable risks:
- PPS timestamp paths are precision-sensitive; wrong clock-format or leap/ffcounter handling can corrupt time discipline.
- Kernel drivers using ABI-aware initialization must set driver ABI and optional mutex state consistently before registration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timepps.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timerfd.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/timerfd.h

Linux-compatible timerfd user/kernel ABI header.

Key responsibilities:
- Includes `sys/time.h` intentionally to reproduce glibc namespace pollution expected by software using timerfd.
- Defines `timerfd_t` as a 64-bit expiration count type.
- Maps creation flags to `O_NONBLOCK` and `O_CLOEXEC`.
- Defines timer setting flags for absolute time and cancel-on-clock-set behavior.
- Declares userland `timerfd_create`, `timerfd_gettime`, and `timerfd_settime`.
- Declares kernel `timerfd_jumped()` notification hook for clock jumps.

Dependencies:
- Includes `sys/types.h`, `sys/fcntl.h`, and `sys/time.h`.

Notable risks:
- Compatibility depends on matching Linux-visible constants and header side effects closely enough for portable applications.
- Cancel-on-set behavior requires correct kernel notification on realtime clock discontinuities.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timerfd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timers.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/timers.h

Kernel POSIX timer management header.

Key responsibilities:
- Defines kernel `struct itimer` with mutex, sigevent, current timer specification, owning process, flags, use count, overrun counters, clock id, signal info, and callout.
- Defines timer lifecycle flags for deleting, wanted, and process-stopped states.
- Sets per-process `TIMER_MAX` to 32 and defines lock/unlock helpers.
- Defines `struct itimers` as the per-process timer table.
- Defines `struct kclock`, an implementation vtable for create, settime, delete, and gettime operations.
- Declares exec/exit cleanup and signal-acceptance helpers.

Dependencies:
- Includes `sys/time.h`; kernel users need mutex, sigevent, proc, ksiginfo, and callout definitions from surrounding includes.

Notable risks:
- Timer lifecycle combines callouts, signal delivery, process exit/exec, and locking; reference/use-count transitions must be carefully synchronized.
- `TIMER_MAX` is part of process resource behavior and compatibility expectations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timers.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/times.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/times.h

POSIX `times(3)` CPU accounting ABI header.

Key responsibilities:
- Defines `clock_t` if needed.
- Defines `struct tms` with user/system CPU time for the process and terminated children.
- Declares userland `times(struct tms *)`.

Dependencies:
- Includes `sys/_types.h` and, for userland prototypes, `sys/cdefs.h`.

Notable risks:
- Simple compatibility ABI; field type and order must remain stable for POSIX consumers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/times.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timespec.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/timespec.h

Timespec utility and POSIX interval timer specification header.

Key responsibilities:
- Includes the canonical `struct timespec` definition.
- Under BSD visibility, defines `TIMEVAL_TO_TIMESPEC` and `TIMESPEC_TO_TIMEVAL` conversion macros.
- Defines `struct itimerspec` with interval and current-value `timespec` fields for POSIX timer syscalls.

Dependencies:
- Includes `sys/cdefs.h` and `sys/_timespec.h`.

Notable risks:
- The timeval conversion macros truncate nanoseconds to microseconds when converting back to timeval.
- `struct itimerspec` is a public ABI shared by POSIX timers and timerfd.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timespec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timetc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/timetc.h

Kernel timecounter hardware interface header.

Key responsibilities:
- Defines `struct timecounter`, including callbacks to read the counter, poll PPS, fill native/32-bit vDSO timehands, counter mask, frequency, name, quality, flags, private pointer, and registration linkage.
- Documents timecounter requirements: fixed known frequency and sufficient width to avoid rapid rollover.
- Defines flags for C2-stop and suspend-safe behavior.
- Declares global current timecounter and minimum ticktock frequency.
- Declares timecounter frequency, initialization, clock-set, ticktock, CPU tick calibration, and clock calibration helpers.
- Exposes `_kern_timecounter` sysctl tree when available.

Dependencies:
- Kernel-only; depends on `u_int`, `timespec`, vDSO timehands types, and machine-dependent vDSO support.

Notable risks:
- Timecounter quality and flags directly affect system clock source selection and suspend/idle correctness.
- vDSO fill callbacks must be consistent with hardware capabilities or userland fast time reads can become wrong.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timetc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timex.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/timex.h

Network Time Protocol kernel discipline ABI header.

Key responsibilities:
- Defines NTP API version and kernel discipline constants for maximum phase/frequency error, PLL/FLL interval limits, nanosecond scale, scaled PPM, and max time constant.
- Defines `timex.modes` control bits for offset, frequency, max/estimated error, status, time constant, PPS max, TAI, micro/nano resolution, and clock A/B selection.
- Defines status bits for PLL/FLL, PPS discipline, leap insert/delete, unsynchronized state, PPS faults, hardware fault, resolution, mode, and clock source.
- Defines clock state constants for `ntptimeval.time_state`.
- Defines `struct ntptimeval` for `ntp_gettime` and `struct timex` for `ntp_adjtime`, including PPS statistics fields.
- Declares kernel `ntp_update_second()` or userland `ntp_adjtime()`/`ntp_gettime()` on FreeBSD.

Dependencies:
- Includes `_timespec` on FreeBSD and `sys/cdefs.h` for userland declarations.

Notable risks:
- Units for several fields depend on `STA_NANO`; callers must not assume all offsets/jitter are always nanoseconds.
- Read-only status bits are explicitly masked by `STA_RONLY` and should not be accepted as daemon-controlled input.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/timex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/tree.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/tree.h

Generic intrusive tree macro library for splay trees and rank-balanced trees.

Key responsibilities:
- Defines splay tree head/entry/access macros, initializers, rotations, link/assemble helpers, prototype generation, implementation generation, insert/remove/find/next/min/max wrappers, and iteration macros.
- Defines rank-balanced tree head/entry/access macros using low pointer bits in the parent pointer to encode red/rank-difference state.
- Implements weak-AVL-style rank-balanced insert, remove, rebalance, find, nearest-find, next/prev, adjacent-position insert, min/max, reinsert, and forward/reverse safe iteration macros.
- Supports static or external generated functions via `RB_PROTOTYPE[_STATIC]` and `RB_GENERATE[_STATIC]`.
- Provides augmentation hooks through `RB_AUGMENT`/`RB_AUGMENT_CHECK` and diagnostic rank verification when `_RB_DIAGNOSTIC` is enabled.

Dependencies:
- Includes `sys/cdefs.h`; assumes tree element pointers have at least two low zero bits for rank-balanced metadata.

Notable risks:
- This header generates real code through macros; comparator behavior, element alignment, and intrusive field use must be correct at every call site.
- Rank-balanced tree internals encode metadata in pointer bits, which is efficient but sensitive to unusual alignment or manual pointer manipulation.
- Augmentation hooks must be idempotent and correct, or tree metadata users can observe stale subtree summaries.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/tree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/tslog.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/tslog.h

Optional kernel timestamp logging macro header.

Key responsibilities:
- Defines event kind constants for enter, exit, thread, and event records.
- Provides convenience macros for function entry/exit, named events, source line events, wait/unwait/hold/release events, fork, exec, namei, and process-exit logging.
- When `TSLOG` is enabled, routes macros to `tslog()` and `tslog_user()` declarations.
- When `TSLOG` is disabled, compiles logging macros away.

Dependencies:
- Kernel-only; under `TSLOG`, includes `_types` and `pcpu` for `pid_t`/current CPU-related context.

Notable risks:
- Because disabled macros become empty statements, callers must not rely on logging expressions for side effects.
- Enabled logging is low-level tracing and must avoid adding unsafe work to sensitive kernel paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/tslog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/tty.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/tty.h

Central kernel TTY structure and public TTY management interface.

Key responsibilities:
- Defines `struct tty`, including lock ownership, global list linkage, flags, revoke count, input/output queues and watermarks, wait condition variables, poll state, async I/O state, termios/window state, init/lock termios states, driver and hook pointers, process/session ownership, softc pointers, device node, and SIGINFO print buffer.
- Defines TTY flags for device naming, init/lock/callout devices, open modes, gone/openclose, async I/O, literal input, high watermarks, flow stopped, exclusive access, bypass path, zombie, hook presence, and busy state.
- Defines userland export `struct xtty` for `kern.ttys`.
- Under `_KERNEL`, declares allocation, locking, device creation, signal, wait/wakeup, output, ioctl, window-size, console, flush, watermark, dev-name, status, console selection, and pty allocation helpers.
- Includes line discipline, device switch, and hook headers for kernel users.

Dependencies:
- Includes queue, locks, mutexes, condition variables, selinfo, termios, tty ioctl, and tty queue headers.

Notable risks:
- TTY state is heavily lock-annotated; fields marked `(t)`, `(l)`, and `(c)` have different lifetime and synchronization rules.
- Flag values are shared with debugging and `pstat(8)`, so renumbering or semantic changes can break observability.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/tty.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ttycom.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ttycom.h

TTY ioctl ABI header.

Key responsibilities:
- Defines ioctl numbers for exclusive mode, pty number, buffer flush, termios get/set, line discipline get/set, pty master validation, drain wait, input timestamp, drain, pty signal/external/user-control modes, controlling tty, console redirection, session ID, status, window size, modem control, output start/stop, packet mode, simulated input, output queue count, process group, DTR, and break control.
- Defines modem bit constants and aliases.
- Defines packet-mode event bits.
- Defines line discipline numbers for termios, SLIP, PPP, netgraph, and Bluetooth H4.

Dependencies:
- Includes `sys/ioccom.h` and `_winsize`.

Notable risks:
- Numeric ioctl slots preserve historical gaps and conflicts with tun/tap; changing values would break userland and driver ABI.
- `TIOCSTI`, console control, process-group, and pty signal ioctls have security-sensitive implementations outside this header.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ttycom.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ttydefaults.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ttydefaults.h

System-wide default terminal settings header.

Key responsibilities:
- Defines default input, output, local, control flags, and default speed for first TTY open.
- Defines `CTRL(x)` control-character conversion and default control characters for EOF, EOL, erase, interrupt, status, kill, quit, suspend, start/stop, literal-next, discard, word erase, reprint, min, and time.
- Provides compatibility aliases for old control-character names.
- When `TTYDEFCHARS` is defined, emits the `ttydefchars[]` array in NCCS order and statically asserts its size.

Dependencies:
- Uses termios flag and control-character constants; the optional array includes `sys/cdefs.h` and `_termios`.

Notable risks:
- The header intentionally treats lowercase letters as uppercase in `CTRL(x)` despite strict control-character conversion expectations.
- `ttydefchars[]` ordering must remain synchronized with `NCCS` and termios control index definitions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ttydefaults.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ttydevsw.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ttydevsw.h

Kernel TTY driver switch interface.

Key responsibilities:
- Requires inclusion through `sys/tty.h`.
- Defines callback typedefs for open, close, output wakeup, input wakeup, normal/control ioctl, parameter update, modem signal control, mmap, packet notification, destructor, and busy/drain status.
- Defines `struct ttydevsw` vtable with default flags, callbacks, and spare slots.
- Provides inline wrappers for each driver callback, asserting TTY locking where needed and checking that the TTY is not gone.
- Suppresses spurious output wakeups when no output is available and input wakeups when the input high-water mark remains set.

Dependencies:
- Depends on `struct tty`, `termios`, thread, vm offset/paddr/memattr types, and line discipline helpers from `sys/tty.h`.

Notable risks:
- Wrapper preconditions are part of the driver contract; callbacks invoked without required locks can race TTY teardown or queue state.
- Optional-looking vtable entries are called unconditionally by wrappers, so drivers must populate the methods they expose to common TTY code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ttydevsw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ttydisc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ttydisc.h

Kernel TTY line discipline interface.

Key responsibilities:
- Requires inclusion through `sys/tty.h`.
- Declares top-half routines for open, close, bytes-available query, read, write, canonicalization, and optimization.
- Declares bottom-half routines for modem state, receive-character paths, simple/bypass receive, receive completion, receive polling, output getc, UIO getc, and output poll.
- Defines receive error flags for framing, parity, overrun, and break.
- Provides inline read/write poll helpers that assert the TTY lock and query input canonicalized bytes or output queue space.

Dependencies:
- Depends on `struct tty`, `uio`, queue helpers, and TTY locking macros.

Notable risks:
- The bypass receive path depends on `TF_BYPASS`; line discipline optimization must keep flag state consistent with termios processing needs.
- Bottom-half functions are commonly called from driver contexts and must honor locking and wakeup expectations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ttydisc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ttyhook.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ttyhook.h

Kernel TTY hook interface for intercepting and injecting terminal traffic.

Key responsibilities:
- Requires inclusion through `sys/tty.h`.
- Defines hook callback typedefs for input character, bypass input, input completion, input poll, output injection, output capture, output poll, and close.
- Defines `struct ttyhook` vtable.
- Declares hook registration and unregistration.
- Provides helpers for hook softc access and testing whether a named hook exists.
- Provides inline wrappers for each hook callback, asserting TTY lock ownership and non-gone state where appropriate.

Dependencies:
- Depends on `struct tty`, proc, and TTY lock/teardown macros from `sys/tty.h`.

Notable risks:
- Hook callbacks run inside TTY data paths and can alter input/output behavior; registration must preserve lifetime and locking rules.
- `ttyhook_hashook()` only checks function pointer presence; callers must still hold appropriate TTY state before dispatch.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ttyhook.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ttyqueue.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ttyqueue.h

Kernel TTY input/output queue data structure and API header.

Key responsibilities:
- Requires inclusion through `sys/tty.h`.
- Defines `struct ttyinq` with block pointers, begin/line/reprint/end offsets, block count, and quota for canonical input buffering.
- Defines fixed input block payload size of 128 bytes.
- Defines `struct ttyoutq` with block pointers, begin/end offsets, block count, and quota for output buffering.
- Defines output block payload size based on a 256-byte block minus next pointer size.
- Declares input queue sizing, free, UIO read, write, no-fragment write, canonicalize, break-canonicalize, findchar, flush, peek, unput, reprint position, and iteration functions.
- Declares output queue flush, sizing, free, read, UIO read, write, and no-fragment write functions.
- Provides inline queue capacity/usage helpers with `MPASS` invariants.

Dependencies:
- Kernel-only APIs depend on `struct tty`, `struct uio`, and queue block implementations elsewhere.

Notable risks:
- Canonical line state uses multiple offsets into block chains; off-by-one or incorrect flush/canonicalize transitions can corrupt terminal input semantics.
- Quota and high-water logic must stay synchronized with `tty.h` watermark flags.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ttyqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/turnstile.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/turnstile.h

Kernel turnstile priority-propagation wait queue interface for contested non-sleepable locks.

Key responsibilities:
- Documents the turnstile lifecycle: chain locking, wait/trywait/cancel, lookup, signal/broadcast, unpend, disown, claim, allocation, and free.
- Defines exclusive and shared queue identifiers.
- Declares initialization, priority adjustment, allocation/free, broadcast/signal, chain lock/unlock, claim/disown, empty/head lookup, turnstile lookup/trywait/wait/unpend, lock/unlock, and assertion APIs.

Dependencies:
- Kernel-only; forward-declares `lock_object`, `thread`, and `turnstile`.

Notable risks:
- Correct use requires pairing high-level lock state changes with turnstile ownership and `turnstile_unpend()` wakeups.
- Priority inheritance correctness depends on accurate owner claiming when a lock with waiters is acquired.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/turnstile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/types.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/types.h

Foundational FreeBSD typedef and small compatibility utility header.

Key responsibilities:
- Includes compiler definitions, machine endian definitions, base private types, offset definitions, and pthread types.
- Defines BSD/System V compatibility integer aliases, deprecated `u_int*_t` and quad types, address pointer aliases, core POSIX scalar types, capability types, kernel-export-safe address/size types, VM scalar types, resource types, and syscall argument type.
- Under kernel/standalone builds, defines kernel-only types such as `boolean_t`, `device_t`, interrupt mask, user offset, memory attribute, and `vm_page_t`, plus C bool shims for older C modes.
- Under BSD visibility, includes select definitions, defines `major`, `minor`, and `makedev` encoders/decoders for FreeBSD `dev_t`, and provides enum-width helper macros for uint8-backed enums.
- Declares legacy-visible `ftruncate`, `lseek`, `mmap`, and `truncate` prototypes for non-kernel compatibility.

Dependencies:
- Central header depending on many low-level machine and sys private type headers.

Notable risks:
- This header is transitively included almost everywhere; namespace pollution is intentional but any change has very wide blast radius.
- `dev_t` encoding/decoding preserves historical compatibility and should not be casually changed.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ucontext.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ucontext.h

User context and machine context public/kernel interface.

Key responsibilities:
- Includes signal, machine-dependent ucontext, and generic `_ucontext` definitions.
- Defines `UCF_SWAPPED`, used by `swapcontext(3)`.
- Declares userland `getcontext`, `getcontextx`, `setcontext`, `makecontext`, `signalcontext`, and `swapcontext`, plus BSD-visible internal helpers for extended context allocation/fill.
- Under `_KERNEL`, defines machine-independent `get_mcontext()` flag `GET_MC_CLEAR_RET` and declares machine-dependent `get_mcontext` and `set_mcontext` functions.

Dependencies:
- Depends on `sys/signal.h`, `machine/ucontext.h`, and `sys/_ucontext.h`.

Notable risks:
- User context APIs expose register/signal ABI details and are architecture-sensitive.
- `getcontext`/`__fillcontextx` are marked `__returns_twice`, which affects compiler assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ucontext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ucoredump.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ucoredump.h

Kernel coredump writer and coredumper registration interface.

Key responsibilities:
- Defines coredump writer callback types for initialization, write, and extend operations.
- Defines vnode-backed writer context, public vnode writer/extend function declarations, `struct coredump_writer`, and `struct coredump_params`.
- Defines core output buffer size and declares `core_write`, `core_output`, and sbuf drain helper.
- Exposes tunables for packing file/vmmap info and compressing user cores.
- Defines coredumper probe priorities and coredumper probe/handle callbacks.
- Defines `struct coredumper` with list linkage, name, callbacks, and blockcount reference counter.
- Declares coredumper register/unregister.

Dependencies:
- Kernel-only; includes `_uio`, blockcount, and queue headers; depends on vnode, compressor, ucred, thread, and sbuf types.

Notable risks:
- Coredumper handle callbacks are documented to enter with the proc lock held and return with it dropped, a non-obvious ownership transfer.
- Probe callbacks run under the proc lock and must not sleep.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ucoredump.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ucred.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ucred.h

Credential structure, external credential ABI, and credential mutation interface.

Key responsibilities:
- Defines credential flags for capability mode and group-set state.
- Defines kernel/internal `struct ucred` when `_KERNEL` or `_WANT_UCRED` is set, including reference/user counts, audit info, UID/GID sets, jail, login class, MAC label, dynamic group storage, and inline small-group storage.
- Defines external `struct xucred` and version, including compatibility union for effective group and supplementary groups.
- Defines `struct setcred`, initializer, and setcred flag bits for updating UIDs, GIDs, supplementary groups, and MAC label.
- Under `_KERNEL`, defines valid setcred mask, 32-bit compatibility records, user_setcred, batched credential reference helpers, credential copy/dup/free/COW/group/resource helpers, process credential setters, and group membership predicates.
- In userland, declares `setcred()`.

Dependencies:
- Includes `sys/types.h`, optional lock/mutex internals, and BSM audit definitions.

Notable risks:
- Comments explicitly warn not to check `cr_uid` directly for superuserness; privilege checks must go through `priv(9)`.
- `xucred` group layout carries historical ambiguity where effective GID is also first group element.
- Credential copy ranges use `cr_startcopy`/`cr_endcopy` markers and must remain synchronized with fields intended for copy-on-write duplication.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ucred.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/uio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/uio.h

Scatter/gather I/O vector and kernel `uio` movement interface.

Key responsibilities:
- Includes shared `iovec` and private `_uio` enum definitions.
- Defines `ssize_t` and `off_t` if needed.
- Under `_KERNEL`, defines `struct uio` with iovec array, count, target offset, residual byte count, segment flag, read/write direction, and owning thread.
- Defines `UIO_MAXIOV` as 1024.
- Declares allocation, free, clone, iovec/uio copyin, mapped copyout, external error copyout, physical copyin/copyout, bus-DMA-vector physical copy, `uioadvance`, and `uiomove` variants for buffers, physical pages, nofault memory, and VM objects.
- In userland, declares `readv`, `writev`, and BSD-visible `preadv`/`pwritev`, using fortified wrappers when enabled.

Dependencies:
- Includes `sys/cdefs.h`, `_types`, `_iovec`, and `_uio`; kernel APIs depend on thread, VM object/page, and bus DMA segment types.

Notable risks:
- `uio_resid`, offsets, and iovec counts drive copy loops throughout filesystems and device drivers; overflow and partial-copy behavior are critical.
- The `UIO_MAXIOV` comment ties the constant to public `IOV_MAX` compatibility expectations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/uio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/umtx.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/umtx.h

Userland synchronization object syscall ABI header.

Key responsibilities:
- Defines common umtx, umutex, rwlock, and semaphore state bits and flags, including contested, priority inheritance/protect, robust, non-consistent, process-shared, reader preference, waiter bits, and count masks.
- Documents mutex owner word layout: high bit as contention indicator and remaining bits as owner TID, with low values reserved for special markers.
- Defines `_umtx_op` operation codes for waits, wakes, mutexes, condition variables, rwlocks, private variants, semaphores, shared memory, robust lists, and minimum timeout operations.
- Defines operation modifier flags for i386/32-bit handling and flags for condition-variable waits, absolute timeout, unpark checking, and umtx shared-memory operations.
- Defines robust-list parameter structure.
- Declares `_umtx_op()` and `_umtx_op_err()`.

Dependencies:
- Includes `sys/_umtx.h`.

Notable risks:
- Numeric operation codes and bit layouts are user/kernel ABI and also consumed by tracing/decoding tools.
- Robust mutex owner-dead/not-recoverable encodings share contested-bit space and require precise userspace/kernel interpretation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/umtx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/umtxvar.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/umtxvar.h

Kernel-internal umtx/futex wait-queue and priority-inheritance state header.

Key responsibilities:
- Defines umtx key types shared by native umtx and Linux futex code, covering simple waits, condition variables, semaphores, normal/PI/PP mutexes, rwlocks, futexes, shared memory, and robust variants.
- Defines `struct umtx_key` mapping user synchronization objects to either shared VM object/offset identity or private vmspace/address identity.
- Defines sharing modes, absolute timeout state, priority-inheritance record `struct umtx_pi`, waiting-thread record `struct umtx_q`, per-key wait queue, and hash-chain structure with shared/exclusive queues, spare queues, busy/waiter state, and PI list.
- Provides key matching helper.
- Declares timeout copy/init, exec cleanup, key get/release, queue allocation/free, busy/unbusy, insert/remove, requeue, signal, sleep, PI sleep, wake, PI operations, and per-thread umtx lifecycle hooks.
- Provides default shared-queue insert/remove aliases and chain lock/unlock helpers.

Dependencies:
- Kernel-only; includes `_timespec` and depends on VM object/vmspace, proc, thread, mutex, tail/list queues, and PI priority types.

Notable risks:
- Key identity is the correctness boundary for process-shared versus private waits; mismatches can wake wrong waiters or miss wakeups.
- Priority inheritance state requires both chain locks and umtx locks in documented cases.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/umtxvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/un.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/un.h

UNIX-domain socket address and local socket option ABI header.

Key responsibilities:
- Defines `sa_family_t` if needed.
- Defines `SUNPATHLEN` as 104 bytes, preserving historical mbuf-era binary compatibility.
- Defines `struct sockaddr_un` with length, family, and pathname fields.
- Under BSD visibility, defines `SOL_LOCAL`, local socket options for peer credentials and credential passing, vendor option base, and userland `SUN_LEN()` length helper.

Dependencies:
- Includes `sys/cdefs.h` and `sys/_types.h`.

Notable risks:
- The pathname limit is intentionally retained for ABI compatibility even though the original mbuf constraint no longer applies.
- `SUN_LEN()` uses `strlen`, so callers must pass initialized, NUL-terminated pathname fields.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/un.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/unistd.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/unistd.h

Kernel/user visible POSIX option, pathconf, seek, rfork, and miscellaneous syscall constant header.

Key responsibilities:
- Defines implemented, unsupported, or runtime-determined POSIX option macros and target `_POSIX_VERSION`.
- Defines access mode constants, seek constants, BSD `SEEK_DATA`/`SEEK_HOLE`, and legacy `L_SET`/`L_INCR`/`L_XTND` aliases.
- Defines `_PC_*` pathconf names for POSIX and FreeBSD filesystem features including ACLs, capabilities, MAC, deallocation, named attributes/xattrs, hidden/system attributes, clone block size, case insensitivity, and minimum hole size.
- Defines BSD `rfork()` flags, signal-number packing helpers, valid/user/kernel-only flag masks, and process-descriptor/vfork/spawn semantics.
- Defines `kcmp()` selectors, swapoff force flag, `close_range()` flags, and `copy_file_range()` user-visible cloning flag.

Dependencies:
- Includes `sys/cdefs.h`.

Notable risks:
- Values that are zero require runtime `sysconf()` support capable of determining real availability.
- `RFPPWAIT` and `RFSPAWN` intentionally share the high bit in kernel/user interpretations, so context matters.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/unistd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/unpcb.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/unpcb.h

UNIX-domain socket protocol control block and exported sysctl record header.

Key responsibilities:
- Defines generation counter type `unp_gen_t`.
- Under kernel or `_WANT_UNPCB`, defines `struct unpcb` with PCB lock, connection pointer, atomic refcount, flags, garbage-collector flags, bound address, socket pointer, pair-lock busy count, vnode association, peer credentials, reference-list linkage, all-PCB linkage, refs head, generation count, file back-pointer, message/reference counts, fake inode/mode, and dead-list linkage.
- Defines PCB flags for peer credential availability, credential passing, connecting/binding/waiting state, and garbage-collector state.
- Provides `sotounpcb()` cast macro.
- When socketvar is included, defines exported `struct xunpcb` and `struct xunpgen` sysctl records with stable kernel-address-sized fields and sockaddr copies.
- Declares kernel peer-credential copy helper.

Dependencies:
- Uses queue and ucred headers, socket/vnode/file types, cache-line alignment, socketvar export types, and UNIX socket address definitions.

Notable risks:
- The locking key distinguishes atomic, constant, PCB lock, linkage lock, and list lock fields; misusing these can race connection teardown or garbage collection.
- Exported sysctl structures include kernel addresses for observability and ABI compatibility, so field changes affect tools like netstat and fstat.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/unpcb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/user.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/user.h

Public process, file descriptor, VM map, VM object, kstack, knote, and VM layout export ABI header.

Key responsibilities:
- Defines `struct kinfo_proc`, the central `KERN_PROC` export record, with extensive process, credential, signal, VM, scheduling, timing, jail, tracing, priority, rusage, PCB, kstack, path, thread, and spare fields.
- Defines legacy `struct user` for a.out core dumps and compatibility aliases.
- Defines file-descriptor export constants for file types, vnode types, special fd records, ntsync types, and file flags.
- Defines legacy `struct kinfo_ofile` and current `struct kinfo_file`, including unions for sockets, vnodes/files, semaphores, pipes, ptys, proc descriptors, eventfd, timerfd, jaildesc, kqueue, inotify, and ntsync details.
- Defines lockf export record and constants.
- Defines VM map entry types, protection bits, flags, legacy/current VM map entry structures, VM object flags and record, kstack record, signal trampoline record, VM layout flags/record, and knote record.
- Under `_KERNEL`, declares sysctl packing/output helpers for proc, filedesc, cwd, vmmap, kqueues, vnode-type conversion, and kinfo packing.

Dependencies:
- Pulls in machine PCB, process, VM, resource, signal, socket, queue, ucred, uio, mutex/lock, event, time, and caprights definitions depending on kernel/user build.

Notable risks:
- Many structures have fixed-size compatibility warnings; changing sizes can break existing binaries unless a new MIB/ABI path is provided.
- New fields must consume spare areas matching alignment and size across all supported architectures, and initialization must be added in both kernel and libkvm paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/user.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/utsname.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/utsname.h

`uname(3)` ABI header.

Key responsibilities:
- Defines `SYS_NMLN` as 32 in kernel for FreeBSD 1.1 ABI compatibility, or 256 by default for userland unless already overridden.
- Defines `struct utsname` fields for OS name, node name, release, version, and machine type.
- Declares variable-record-size `__xuname()`.
- Provides inline `uname()` wrapper passing `SYS_NMLN` to `__xuname`.

Dependencies:
- Includes `sys/cdefs.h`.

Notable risks:
- The structure size depends on `SYS_NMLN`, so the inline wrapper and `__xuname` length parameter are central to compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/utsname.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/uuid.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/uuid.h

DCE-compatible UUID structure and generation/parsing interface.

Key responsibilities:
- Defines UUID node length and kernel UUID generation batch maximum.
- Defines `struct uuid` in DCE 1.1 source layout: time fields, clock sequence fields, and 6-byte node.
- Under `_KERNEL`, exposes UUID node length, kernel UUID generation, Ethernet node add/delete, string formatting helpers, sbuf formatting, validation/parsing flags and functions, comparison, and big/little-endian encode/decode helpers.
- In userland, aliases `uuid_t` to `struct uuid` and declares `uuidgen()`.

Dependencies:
- Includes `sys/types.h`; kernel formatting uses `struct sbuf`.

Notable risks:
- `UUIDGEN_BATCH_MAX` limits allocations per call and should be preserved as a resource-safety boundary.
- Validation can check only format or also semantics depending on flags; callers must request the intended strictness.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/uuid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/vdso.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/vdso.h

FreeBSD vDSO timekeeping and fast random-generation shared data header.

Key responsibilities:
- Defines `struct vdso_timehands` and `struct vdso_timekeep` for userland fast time reads, including algorithm, generation, scale, counter offset/mask, bintime offset, boottime, and machine-dependent fields.
- Defines busy/current/version and timehands algorithm constants.
- Defines `struct vdso_fxrng_generation_1`, asserts its size, and maps the current fxrng generation type/version constants.
- In userland, declares vDSO clock/gettimeofday/timecounter/timekeep helper entry points.
- Under `_KERNEL`, defines per-sysentvec timekeep state, declares optional fxrng seed generation push, timekeep push, native CPU/timecounter vDSO fill helpers, and `alloc_sv_tk()`.
- Under 32-bit compatibility, defines 32-bit bintime/timehands/timekeep structures and fill/allocation helpers.

Dependencies:
- Includes `sys/types.h` and `machine/vdso.h`; uses `struct bintime`, `clockid_t`, timecounter, and machine-dependent vDSO macros.

Notable risks:
- Generation counters and busy markers are concurrency ABI between kernel writers and userland readers.
- Native and compat32 layouts must match the consuming vDSO code exactly, including machine-dependent fields.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/vdso.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/vmem.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/vmem.h

Extent/arena allocator interface for virtual or resource address ranges.

Key responsibilities:
- Defines opaque `vmem_t`, address and size types, minimum/maximum address constants, and utilization typemask bits.
- Defines import, release, and reclaim callback types.
- For non-kernel builds, defines M_* allocation flags needed by vmem userspace consumers.
- Declares create/init/destroy, import callback setup, size limit setup, reclaim callback setup, normal allocation/free, constrained allocation/free, static span add, quantum-size roundup, utilization query, diagnostic lookup/printing, print-all, and startup functions.
- Documents allocation policies such as first fit, best fit, next fit, blocking behavior, quantum caches, alignment, phase, no-cross boundaries, and min/max constraints.

Dependencies:
- Includes `sys/types.h`.

Notable risks:
- `vmem_xalloc()` constraint semantics are subtle: min/max apply to last/first bytes as documented, not just starting address.
- Normal allocation/free honor quantum caches, while constrained allocation bypasses them; callers must choose the right path for alignment-sensitive resources.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/vmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/vmmeter.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/vmmeter.h

Virtual memory and system activity counter header.

Key responsibilities:
- Defines `MAXSLP`, used by userland and scheduler logic for sleep-state interpretation.
- Defines `struct vmtotal`, the aggregate VM/run/sleep/swap state summary.
- Under kernel or `_WANT_VMMETER`, defines cache-line-aligned `struct vmmeter` with counter(9)-backed activity counters for context switches, traps, syscalls, interrupts, VM faults, pager activity, reactivation, page daemon work, frees, fork activity, and wired/no-free counts, followed by constant page distribution thresholds and page size/count values.
- Defines `VM_METER_NCOUNTERS` as the counter field count before `v_page_size`.
- Under `_KERNEL`, declares global `vm_cnt`, memory-pressure domainsets, counter add/inc/fetch macros, user wire count, wire/no-free helpers, free count, and low-memory threshold predicates for severe/minimum pressure globally, per-domain, or domain-set masked.

Dependencies:
- Uses counter(9), domainset, cache-line alignment, and VM page accounting globals.

Notable risks:
- The split between counter fields and constant fields is encoded by `VM_METER_NCOUNTERS`; inserting fields before `v_page_size` changes counter initialization/iteration expectations.
- Low-memory predicates are used at user/kernel boundaries and in pageout decisions, so domainset state must reflect current VM pressure accurately.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/vmmeter.h -->