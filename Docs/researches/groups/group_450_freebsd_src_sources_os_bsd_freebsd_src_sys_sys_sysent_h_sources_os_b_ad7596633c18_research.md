# Group Research: group_450_freebsd_src_sources_os_bsd_freebsd_src_sys_sys_sysent_h_sources_os_b_ad7596633c18

Scope: subset A from `Docs/research_subset_a.md`, covering the listed FreeBSD `sys/sys` headers under `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sysent.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sysent.h

## Scope

This header defines FreeBSD kernel syscall dispatch metadata, per-ABI execution vectors, syscall module registration helpers, and shared-page/sysvec initialization declarations. It is a central contract between generated syscall tables, kernel syscall handlers, executable image activation, ABI compatibility layers, auditing, and DTrace systrace.

## APIs And Constants

- Defines `sy_call_t` syscall handler signature and systrace probe/argument callback types.
- Defines `struct sysent`, the syscall table entry: handler, optional systrace arg translator, argument count, syscall flags, audit event, DTrace probe IDs, and thread-count state.
- Defines syscall flags such as `SYF_CAPENABLED` and thread state flags `SY_THR_STATIC`, `SY_THR_DRAINING`, `SY_THR_ABSENT`, and `SY_THR_INCR`.
- Defines `struct sysentvec`, the executable ABI vector containing syscall table pointers, signal delivery, core dump, auxv/string copyout, register setup, limits, syscall argument fetching, shared-page/vDSO offsets, thread hooks, trap hook, hardware capability pointers, exec/exit protection hooks, set-id policy, fork return handling, and regset ranges.
- Defines sysvec flags for ABI width and behavior: `SV_ILP32`, `SV_LP64`, `SV_AOUT`, `SV_SHP`, `SV_SIGSYS`, `SV_TIMEKEEP`, `SV_ASLR`, `SV_RNG_SEED_VER`, `SV_SIG_DISCIGN`, `SV_SIG_WAITNDQ`, and `SV_DSO_SIG`.
- Defines ABI constants `SV_ABI_LINUX`, `SV_ABI_FREEBSD`, and `SV_ABI_UNDEF`, plus process/current-process access macros.
- Under `_KERNEL`, declares the native `sysent[]`, `syscallnames[]`, `nosys_sysent`, `nosys()`, loadable syscall placeholders, registration/deregistration helpers, shared-page helpers, and exec sysvec initialization hooks.
- Provides `SYSENT_INIT_VALS`, `MAKE_SYSENT`, `SYSCALL_MODULE`, `SYSCALL_MODULE_HELPER`, `SYSCALL_INIT_HELPER*`, and related helper macros for static and loadable syscall definitions.

## Control Flow And Integration

- Kernel syscall dispatch indexes a `struct sysentvec` selected by the process ABI, then a `struct sysent` selected by syscall number.
- Syscall modules register by replacing a slot in a syscall table while preserving the old `struct sysent` for deregistration.
- Syscall helper arrays support bulk registration with per-helper `registered` state so partial setup can be unwound.
- Systrace hooks are conditionally active when `KDTRACE_HOOKS` is present; otherwise `SYSTRACE_ENABLED()` folds to zero.
- `sysentvec` integrates executable loading with machine-dependent register setup, signal trampoline placement, shared page/vDSO mapping, ABI-specific syscall argument fetch/return semantics, and process/thread lifecycle hooks.

## Dependencies

- Includes BSM audit definitions and uses `au_event_t` for per-syscall audit classification.
- Refers to core kernel types such as `thread`, `proc`, `image_params`, `trapframe`, `vnode`, `rlimit`, `ksiginfo`, `coredump_writer`, and `note_info_list`.
- Ties into module loading, SYSINIT ordering, exec image activation, signal delivery, ptrace/core dump paths, and DTrace systrace.

## Risks And Invariants

- `struct sysent` field layout and `SYSENT_INIT_VALS` must remain consistent with generated syscall code and syscall table initializers.
- `struct sysentvec` is ABI-critical; changing hooks, flags, or address fields affects every process using that ABI.
- Loadable syscall registration must preserve and restore old entries exactly to avoid stale handlers or wrong audit metadata.
- `SYF_CAPENABLED` is part of Capsicum syscall policy; incorrect flags can expose or block syscalls in capability mode.
- Thread-count state flags protect dynamic syscall unload from racing active syscall execution.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sysent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/syslimits.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/syslimits.h

## Scope

This header defines a small set of POSIX/system limit constants used by userland and the kernel-facing public headers. It intentionally avoids defining values that applications should obtain dynamically through `sysconf()`.

## APIs And Constants

- Defines `ARG_MAX` as `2 * 256 * 1024` except on `__ILP32__`, where it is `256 * 1024`.
- Defines defaults for `CHILD_MAX`, `NGROUPS_MAX`, and `OPEN_MAX` only when not already provided.
- Defines terminal, pathname, pipe, and vector limits: `MAX_CANON`, `MAX_INPUT`, `NAME_MAX`, `PATH_MAX`, `PIPE_BUF`, and `IOV_MAX`.
- Leaves `HOST_NAME_MAX` undefined by design.

## Control Flow And Integration

- This file is purely declarative and has no runtime control flow.
- It warns when included directly outside the intended include chain, unless building standalone, kernel, `<limits.h>`, or `<sys/param.h>` contexts.
- The comments explicitly discourage adding new variables here because many limits are runtime-configurable or should be queried dynamically.

## Dependencies

- No type dependencies beyond the preprocessor context.
- Consumed by public limits headers and kernel/userland code that needs legacy compile-time constants.

## Risks And Invariants

- Compile-time constants here are ABI and application-compatibility expectations; lowering values can break existing builds or runtime assumptions.
- Defining too many dynamic limits statically can encourage incorrect portable code, which is why `HOST_NAME_MAX` remains undefined.
- The ILP32 `ARG_MAX` split reflects kernel virtual-address-space pressure and should not be changed without checking exec argument-copy paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/syslimits.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/syslog.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/syslog.h

## Scope

This header defines the FreeBSD syslog priority/facility namespace, log socket paths, openlog/setlogmask option flags, optional name lookup tables, and userland syslog function prototypes.

## APIs And Constants

- Defines log socket paths `_PATH_LOG` and `_PATH_LOG_PRIV`.
- Defines priorities `LOG_EMERG` through `LOG_DEBUG`, `LOG_PRIMASK`, `LOG_PRI()`, and `LOG_MAKEPRI()`.
- Defines facilities `LOG_KERN`, `LOG_USER`, `LOG_MAIL`, `LOG_DAEMON`, `LOG_AUTH`, `LOG_SYSLOG`, `LOG_LPR`, `LOG_NEWS`, `LOG_UUCP`, `LOG_CRON`, `LOG_AUTHPRIV`, `LOG_FTP`, `LOG_NTP`, `LOG_SECURITY`, `LOG_CONSOLE`, and `LOG_LOCAL0` through `LOG_LOCAL7`.
- Defines `LOG_NFACILITIES`, `LOG_FACMASK`, and `LOG_FAC()`.
- When `SYSLOG_NAMES` is enabled, defines `CODE`, `prioritynames[]`, and `facilitynames[]`, including deprecated aliases and internal `none`/`mark` entries.
- Defines `LOG_MASK()` and `LOG_UPTO()` for `setlogmask()`.
- Defines `openlog()` option flags `LOG_PID`, `LOG_CONS`, `LOG_ODELAY`, `LOG_NDELAY`, `LOG_NOWAIT`, and `LOG_PERROR`.
- In userland, declares `closelog()`, `openlog()`, `setlogmask()`, `syslog()`, and BSD-visible `vsyslog()`.
- In kernel builds, defines pseudo-priority `LOG_PRINTF`.

## Control Flow And Integration

- Priority occupies the low three bits and facility occupies higher bits, so call sites build a single integer selector.
- Userland prototypes avoid directly including a varargs header by using `__va_list` from `<sys/_types.h>`.
- The optional name arrays are static header data used by parsers such as syslog configuration tools when `SYSLOG_NAMES` is requested.

## Dependencies

- Userland declarations depend on `<sys/cdefs.h>` for declaration and printf-format attributes and `<sys/_types.h>` for `__va_list`.
- Facility and priority constants must stay aligned with `syslogd(8)` string mappings and existing syslog protocol expectations.

## Risks And Invariants

- Priority encoding assumes three priority bits; changing `LOG_PRIMASK` or facility shifts would break existing logs and parsers.
- Facility values are externally visible and must remain stable for configuration compatibility.
- `LOG_NDELAY` and `LOG_ODELAY` comments document historical semantic drift; callers may still rely on old names.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/syslog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sysproto.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sysproto.h

## Scope

This automatically generated header declares FreeBSD syscall argument structures, syscall implementation prototypes, compatibility syscall surfaces, and audit event mappings. It is generated from the syscall master description and is consumed by syscall implementations, syscall table generation, ABI compatibility code, and audit metadata setup.

## APIs And Generated Surfaces

- Defines padding helpers `PAD_`, `PADL_`, and `PADR_` so syscall argument structures preserve register-sized argument slots across little-endian and big-endian targets.
- Includes required public kernel/user ABI types from `sys/types.h`, `sys/signal.h`, `sys/cpuset.h`, `sys/domainset.h`, `_ffcounter`, `_semaphore`, `ucontext`, `wait`, and BSM audit events.
- Declares 495 syscall argument structures and 495 matching syscall implementation prototypes.
- Declares argument/prototype pairs for core process, file, VFS, VM, socket, time, scheduler, security, audit, IPC, POSIX AIO, kqueue, jail, Capsicum, cpuset/domainset, shared memory, timerfd, inotify, process descriptor, kexec, and extended error/sysctl facilities.
- Defines 495 `SYS_AUE_*` macros that map syscall names to BSM audit event constants, including `AUE_NULL` for unaudited or non-security-relevant operations.
- Undefines the internal padding helpers before leaving the header.

## Syscall Families Covered

- Process and credential operations: exit/fork/vfork/rfork, wait variants, get/set uid/gid/groups, setresuid/setresgid, process groups/sessions, `procctl`, `setcred`, and process descriptor calls.
- File and VFS operations: open/close/read/write, vector and positioned I/O, stat/statfs families, link/unlink/rename variants, mkdir/rmdir/mknod/mkfifo, chmod/chown/chflags, pathconf, filesystem handles, `copy_file_range`, `fspacectl`, `funlinkat`, and `close_range`.
- Filesystem-adjacent controls: mount/unmount/nmount, `quotactl`, NFS service/file-handle calls, extended attributes, ACL calls, MAC label calls, and shared-memory object calls.
- IPC and synchronization: SysV sem/msg/shm, POSIX semaphores, message queues, umtx, timerfd, and memory barriers.
- Networking: sockets, bind/connect/accept/listen/shutdown, send/receive variants, socketpair, `bindat`, `connectat`, SCTP compatibility entry points, and RPC TLS syscall hook.
- VM and memory: break, mmap/munmap/mprotect/madvise/mincore/minherit, mlock/munlock, and memory-locking AIO.
- Time and timers: get/set time of day, adjtime, NTP calls, POSIX clocks/timers, nanosleep variants, ffclock APIs, and CPU clock lookup.
- Security and policy: Capsicum, audit/auditon/auditctl, jail operations, login class, resource controls, MAC framework syscalls, and `issetugid`.
- System management: reboot, ktrace/utrace, sysctl/sysctlbyname, kernel environment, module/KLD calls, UUID generation, `getrandom`, `kcmp`, `exterrctl`, and `__specialfd`.

## Compatibility Blocks

- `COMPAT_43` provides old 4.3BSD syscall argument/prototype forms for legacy stat, signal, socket, mmap, truncate, hostname, rlimit, and directory APIs.
- `COMPAT_FREEBSD4` covers old statfs/domain/uname/sendfile/signal-context variants.
- `COMPAT_FREEBSD6` covers old offset-padding and old AIO/sigevent layouts for pread/pwrite/mmap/lseek/truncate/ftruncate and AIO list operations.
- `COMPAT_FREEBSD7` covers old SysV IPC control layouts.
- `COMPAT_FREEBSD10` covers old pipe and umtx lock/unlock entry points.
- `COMPAT_FREEBSD11` covers old device number, stat, dirent, kevent, statfs, fstatat, and mknodat layouts.
- `COMPAT_FREEBSD12`, `COMPAT_FREEBSD13`, and `COMPAT_FREEBSD14` cover renamed or layout-changed shm, closefrom, swapoff, and groups syscalls.

## Control Flow And Integration

- Each syscall implementation receives `struct thread *` plus a pointer to its generated argument structure.
- The argument structures are the ABI boundary between machine-dependent syscall argument fetch code and machine-independent syscall bodies.
- Generated `SYS_AUE_*` values are consumed by `sysent` initializers so audit classification follows the same syscall source as the prototypes.
- Compatibility blocks compile only when the corresponding ABI support is enabled, allowing old user binaries to keep their historical argument layouts.

## Dependencies

- Depends on generated syscall-number and syscall-table machinery outside this header.
- Uses many forward-declared or externally defined ABI structures such as file handles, ACLs, MAC labels, AIO control blocks, message queue attributes, jail descriptors, resource-control buffers, stat/statfs variants, and compatibility-only legacy structures.
- Integrates with `sysent.h` through `SYS_AUE_*` names and `struct *_args` names used by syscall table initializers.

## Risks And Invariants

- This file is generated; manual edits would be overwritten and can desynchronize prototypes, argument layouts, audit mappings, and syscall tables.
- Padding macros are ABI-critical. Incorrect padding changes how register-sized syscall arguments are interpreted on mixed-width or different-endian targets.
- The count and names of arg structures, prototypes, and audit mappings must remain synchronized; in this version each count is 495.
- Compatibility layouts are intentionally old and sometimes awkward; replacing them with native structures would break legacy binaries.
- Audit mappings are security-sensitive because they determine which audit event is recorded for each syscall.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sysproto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/systm.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/systm.h

## Scope

This broad kernel header declares many core FreeBSD kernel globals, boot/tuning state, low-level utility APIs, formatted output routines, memory/string primitives, user/kernel copy helpers, clock/profiling hooks, kernel environment helpers, sleep/wakeup APIs, unit-number allocation APIs, and deprecation diagnostics.

## APIs And Constants

- Declares boot and system globals: `cold`, `suspend_blocked`, `rebooting`, `version`, `compiler_version`, `copyright`, `kstack_pages`, `pagesizes`, `physmem`, `realmem`, `rootdevnames`, `boothowto`, `bootverbose`, `maxusers`, `ngroups_max`, `vm_guest`, and `maxphys`.
- Defines `enum VM_GUEST` values for recognized hypervisor/guest environments.
- Defines alignment/placement attributes `__read_mostly`, `__read_frequently`, and `__exclusive_cache_line`.
- Declares hash table helpers, CPU/cache/init routines, LinuxKPI current-state allocation hooks, critical-section entry/exit helpers, early printf hooks, and kernel printf/logging APIs.
- Declares memory/string functions and maps `bcopy`, `bzero`, `bcmp`, `memset`, `memcpy`, `memmove`, and `memcmp` to compiler builtins or sanitizer interceptors.
- Declares early memory functions, `copystr`, `copyin`, `copyinstr`, `copyout`, nofault variants, fetch/store user-word helpers, and compare-and-swap user helpers.
- Declares clock, profiling, eventtimer, kernel environment, cputicker, console/init/reboot/shutdown, sleep/wakeup, cdev naming, delay, root mount holdback, unit-number allocation, interrupt profiling, safe kernel memory read, and obsolete-code warning APIs.
- Provides no-op legacy `spl*()` interrupt-priority stubs.

## Control Flow And Behavior

- `critical_enter()` and `critical_exit()` use inline fast paths unless KBI/module/tracing constraints require function calls; the inline path increments/decrements `td_critnest`, uses interrupt fences, and invokes preemption handling when owed.
- `copystr` is a statement-expression wrapper over `strlcpy()` that returns `ENAMETOOLONG` when the destination buffer is too small and optionally reports copied length.
- Sleep macros translate tick-based timeouts to `sbintime_t` and call `_sleep()` or spin-sleep variants.
- `pause()` wraps `pause_sbt()` with hardclock timing, while `pause_sig()` adds `C_CATCH`.
- Root mount hold tokens allow subsystems to delay root mount completion until required devices or services are ready.
- `gone_in()` and `gone_in_dev()` emit a deprecation warning only once per call site, and can become compile-time assertions when obsolete code is disabled.

## Dependencies

- Includes core kernel headers for types, callouts, assertions, queues, fixed-width integers, atomics, CPU functions, parameters, per-CPU state, and KPI-lite thread state.
- Relies on machine-specific atomic/cpufunc/user-access implementations for many declared primitives.
- Used pervasively by kernel subsystems, including VFS, device drivers, networking, VM, scheduler, console, sysctl/environment, and boot code.

## Risks And Invariants

- This is a high-fanout kernel header; changes can affect almost every kernel translation unit.
- Critical-section accounting must stay balanced or preemption/interrupt invariants break.
- User-copy helpers are security boundaries; callers must check annotated results and respect nofault semantics.
- Sanitizer interception macros must not recurse into sanitizer runtimes incorrectly.
- `gone_in()` uses `__LINE__` to build per-call-site statics; moving or macro-wrapping call sites can change warning identity.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/systm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/taskqueue.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/taskqueue.h

## Scope

This kernel-only header declares FreeBSD taskqueue APIs: deferred task queues, timeout tasks, thread-backed queues, software-interrupt queues, fast-interrupt-compatible queues, callbacks, and global taskqueue declaration/definition macros.

## APIs And Constants

- Defines taskqueue callback types `TASKQUEUE_CALLBACK_TYPE_INIT` and `TASKQUEUE_CALLBACK_TYPE_SHUTDOWN`, plus callback count/name length constants.
- Defines enqueue flags `TASKQUEUE_FAIL_IF_PENDING` and `TASKQUEUE_FAIL_IF_CANCELING`.
- Declares `taskqueue_callback_fn` and `taskqueue_enqueue_fn`.
- Declares queue lifecycle APIs: `taskqueue_create()`, `taskqueue_create_fast()`, start-thread variants, `taskqueue_free()`, `taskqueue_block()`, `taskqueue_unblock()`, and callback registration.
- Declares task operations: enqueue, enqueue with flags, enqueue timeout by ticks or sbt, poll busy, cancel, cancel timeout, drain task, drain timeout, drain all, quiesce, run, and membership checks.
- Provides `TASK_INITIALIZER`, `TASK_INIT_FLAGS`, `TASK_INIT`, and `TIMEOUT_TASK_INIT`.
- Provides global queue macros `TASKQUEUE_DECLARE`, `TASKQUEUE_DEFINE`, `TASKQUEUE_DEFINE_THREAD`, `TASKQUEUE_FAST_DEFINE`, and `TASKQUEUE_FAST_DEFINE_THREAD`.
- Declares standard global queues: `taskqueue_swi_giant`, `taskqueue_swi`, `taskqueue_thread`, `taskqueue_fast`, and `taskqueue_bus`.

## Control Flow And Integration

- A taskqueue is created with an enqueue callback that schedules execution, commonly by waking a kernel thread or scheduling software interrupt processing.
- Thread-backed queues use `taskqueue_thread_enqueue()` and `taskqueue_thread_loop()`.
- `TASKQUEUE_DEFINE*` macros create global queue pointers and register SYSINIT initialization at taskqueue subsystem order.
- Fast taskqueues use spin-compatible locking and are intended for contexts where sleep mutexes are not legal.
- Timeout tasks bind a callout-style delayed trigger to a taskqueue.

## Dependencies

- Kernel-only; emits a preprocessor error outside `_KERNEL`.
- Depends on queue primitives, task definitions from `<sys/_task.h>`, cpuset types, kernel threads/processes, SYSINIT, priority constants, and callout/sbt timing types.

## Risks And Invariants

- Task priority is stored in 8 bits; `TIMEOUT_TASK_INIT` statically enforces priority range 0 through 255.
- Callers must drain or cancel tasks before freeing backing storage to avoid use-after-free.
- Fast queues must only use primitives legal in fast interrupt context.
- `TASKQUEUE_FAIL_IF_PENDING` and canceling flags alter enqueue semantics and must be chosen with races in mind.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/taskqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/terminal.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/terminal.h

## Scope

This header defines FreeBSD's terminal abstraction layered above TTY and console drivers. It provides packed character/color attributes, terminal class callbacks, terminal state, kernel console registration helpers, and APIs for terminal allocation, TTY creation, resizing, muting, and input.

## APIs And Constants

- Defines `term_char_t` as a 32-bit value containing a Unicode code point, formatting bits, foreground color, and background color.
- Defines extractors `TCHAR_CHARACTER()`, `TCHAR_FORMAT()`, `TCHAR_FGCOLOR()`, and `TCHAR_BGCOLOR()`.
- Defines color/format builders `TCOLOR_FG()`, `TCOLOR_BG()`, `TCOLOR_LIGHT()`, `TCOLOR_DARK()`, and `TFORMAT()`.
- Provides syscons-compatible foreground/background attribute macros, including normal and bright colors plus blink.
- Defines default normal and kernel console attributes through `TERMINAL_NORM_ATTR` and `TERMINAL_KERN_ATTR`.
- Defines callback typedefs for emulator drawing, input boundaries, parameters, cleanup, console probe/getc/grab/ungrab, open notification, ioctl, mmap, and bell handling.
- Defines `struct terminal_class` callback table and `struct terminal` runtime state.
- Under `_KERNEL`, declares `terminal_alloc()`, `terminal_maketty()`, cursor/window/mute/input APIs, `termcn_cnregister()`, `termcn_cnops`, and `TERMINAL_DECLARE_EARLY()`.

## Control Flow And Integration

- Console drivers provide a `terminal_class`; the terminal layer drives output through teken emulator callbacks rather than requiring each driver to implement escape-sequence handling.
- `struct terminal` binds driver softc, mutex, tty, teken emulator, current window size, flags, and console device.
- `TF_CONS` marks console devices that need console locking behavior.
- `TERMINAL_DECLARE_EARLY()` creates a statically initialized console terminal and matching `CONSOLE_DEVICE` for early console registration.
- Input helpers feed Unicode, raw bytes, or special key codes into the terminal/TTY layer.

## Dependencies

- Includes kernel parameters, lock/mutex definitions, console declarations, linker set support, tty ioctl structures, teken terminal emulator types, and syscons/teken option headers.
- Integrates with the TTY subsystem, kernel console framework, DDB/panic console paths, and framebuffer/text console drivers.

## Risks And Invariants

- `term_char_t` bit allocation is part of the terminal driver contract; changing it affects every renderer using stored cell values.
- Teken uses UTF-8/Unicode semantics; drivers should not reinterpret character bits as legacy bytes.
- Console paths can run in panic/debugger contexts, so callbacks and locks must respect those constraints.
- The early terminal declaration relies on static initialization only; fields not initialized there must tolerate zero defaults.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/terminal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/termios.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/termios.h

## Scope

This compatibility shim warns that including `<sys/termios.h>` is deprecated and then includes the public `<termios.h>` header.

## APIs And Constants

- Emits a GCC warning advising use of `<termios.h>` instead.
- Includes `<termios.h>` to preserve source compatibility.

## Control Flow And Integration

- There is no runtime behavior.
- The file exists to keep old include paths building while nudging users to the standards-facing header.

## Dependencies

- Depends entirely on `<termios.h>` for actual terminal I/O types, constants, and prototypes.

## Risks And Invariants

- Removing this shim would break legacy source that still includes `<sys/termios.h>`.
- The warning is guarded by `__GNUC__`, so non-GNU compilers may not emit the deprecation notice.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/termios.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/thr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/thr.h

## Scope

This header defines the low-level FreeBSD thread syscall user ABI, including thread creation flags, `struct thr_param`, and userland prototypes for the `thr_*` system call wrappers.

## APIs And Constants

- Defines thread creation flags `THR_SUSPENDED`, `THR_SYSTEM_SCOPE`, and `THR_C_RUNTIME`.
- Defines `struct thr_param` with entry function, argument, stack base/size, TLS base/size, child and parent TID pointers, flags, realtime priority pointer, and spare slots.
- Ensures `size_t` is declared from `<sys/_types.h>`.
- Outside `_KERNEL`, includes `<sys/ucontext.h>`, ensures `pid_t` is declared, and declares `thr_create()`, `thr_new()`, `thr_self()`, `thr_exit()`, `thr_kill()`, `thr_kill2()`, `thr_suspend()`, `thr_wake()`, and `thr_set_name()`.

## Control Flow And Integration

- `thr_new()` uses `struct thr_param` as an extensible syscall argument block whose `param_size` is passed separately in `sysproto.h`.
- `thr_create()` takes a full user context, while `thr_new()` takes explicit stack/TLS/entry fields.
- Child and parent TID pointers provide user-visible synchronization points for thread creation and exit.
- The realtime priority pointer allows thread creation with scheduling attributes.

## Dependencies

- Includes C declaration macros, internal type definitions, and scheduler priority structures.
- Userland prototypes depend on `ucontext_t`, `pid_t`, and `struct timespec`.
- Tied to generated syscall argument declarations in `sysproto.h` for `thr_create`, `thr_new`, and related thread syscalls.

## Risks And Invariants

- `struct thr_param` is a user/kernel ABI structure; field order and sizes are compatibility-sensitive.
- `param_size` must be validated by syscall code before reading optional or future fields.
- TID pointer handling crosses user/kernel memory boundaries and must be copied or written carefully by implementations.
- The spare fields are reserved for future ABI extension and should not be repurposed casually.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/thr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/tiio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/tiio.h

## Scope

This header defines user-visible ioctl data structures and request codes for Alteon/Tigon network adapter diagnostics, statistics, parameters, tracing, and firmware/register/memory access.

## APIs And Constants

- Defines `struct ti_stats`, a fixed-layout Tigon statistics block with MAC counters, MIB-II/RFC-derived interface counters, 64-bit high-capacity counters, host command counters, NIC events, ring manipulation counters, interrupt/coalescing counters, DMA attention counters, resource exhaustion counters, MAC RX/TX attention counters, collision histogram, profile slots, and padding to a 1024-byte block.
- Defines interface admin/oper status constants such as `IF_ADMIN_STATUS_UP`, `IF_OPER_STATUS_DOWN`, and related status values.
- Defines `struct tg_reg` for adapter register access and `struct tg_mem` for adapter memory access.
- Defines `ti_param_mask` flags for statistic tick, RX/TX coalescing ticks, RX/TX coalescing buffer descriptors, TX buffer ratio, and all supported parameters.
- Defines `struct ti_params` containing tunable coalescing/statistics parameters plus a mask of active fields.
- Defines `ti_trace_type` bit flags for trace categories and trace levels.
- Defines `struct ti_trace_buf` for trace buffer exchange.
- Defines FreeBSD driver ioctls `TIIOCGETSTATS`, `TIIOCGETPARAMS`, `TIIOCSETPARAMS`, `TIIOCSETTRACE`, and `TIIOCGETTRACE`.
- Defines Alteon-compatible ioctls `ALT_ATTACH`, `ALT_READ_TG_MEM`, `ALT_WRITE_TG_MEM`, `ALT_READ_TG_REG`, and `ALT_WRITE_TG_REG`.

## Control Flow And Integration

- Driver ioctl handlers use these structures to copy statistics, apply selected tunables, enable trace categories, return trace buffers, and perform diagnostic register/memory operations.
- The statistics structure embeds firmware/hardware-visible counters and marks most fields `volatile`, reflecting that values may be updated by device/firmware paths.
- `param_mask` lets userland set only selected tuning fields rather than replacing the whole parameter set.
- Alteon ioctl values preserve compatibility with vendor tooling while avoiding vendor ioctl numbers 1 through 6.

## Dependencies

- Includes `<sys/ioccom.h>` for `_IO`, `_IOR`, `_IOW`, and `_IOWR`.
- Uses kernel/public integer types, `caddr_t`, `u_long`, and ioctl encoding conventions.
- Tied to the Tigon/Alteon network driver implementation and its firmware statistics layout.

## Risks And Invariants

- `struct ti_stats` layout is externally visible and firmware-derived; field order, sizes, and total padded size must remain stable for ioctl consumers.
- Register and memory access ioctls are powerful diagnostics and must be permission-checked by driver code.
- Trace buffer pointers are user addresses and require careful copyin/copyout handling.
- `volatile` does not provide synchronization by itself; the driver must still snapshot or serialize where consistency matters.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/tiio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/tim_filter.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/tim_filter.h

## Scope

This header defines a compact time-window filter abstraction used in the kernel to track minimum or maximum values over recent time. It provides 64-bit and smaller 32-bit variants, structure layouts, filter type constants, and kernel function prototypes.

## APIs And Constants

- Defines `NUM_FILTER_ENTRIES` as 3, with comments tying the current size to amd64 cache-line considerations.
- Defines `struct filter_entry` with 64-bit value and update time, packed.
- Defines `struct filter_entry_small` with 32-bit value and update time.
- Defines `struct time_filter` with current time limit and three 64-bit entries; in kernel builds it is cache-line aligned.
- Defines `struct time_filter_small` with current time limit and three 32-bit entries.
- Defines filter type constants `FILTER_TYPE_MIN` and `FILTER_TYPE_MAX`.
- Under `_KERNEL`, declares setup, reset, clock-forward/tick, min/max apply, reduce/increase, and inline getter functions for both normal and small variants.

## Control Flow And Integration

- Callers initialize a filter with a type and time window, update its clock, and apply values through min or max update functions.
- The first entry is treated as the current filtered value by `get_filter_value()` and `get_filter_value_small()`.
- Duplicated normal/small APIs avoid polymorphism in kernel C and save memory where 32-bit values are sufficient.
- Reduce/increase helpers adjust the tracked values while preserving the time-window model.

## Dependencies

- Includes `<sys/types.h>` and `<machine/param.h>` for fixed-width types and `CACHE_LINE_SIZE`.
- Function implementations live outside this header and are only declared for kernel builds.

## Risks And Invariants

- The normal and small APIs are intentionally separate; passing the wrong structure type to the wrong function can corrupt memory or produce invalid results.
- `NUM_FILTER_ENTRIES` affects structure size, cache behavior, and algorithm expectations.
- Packed 64-bit entries can have alignment implications on some architectures, mitigated in part by cache-line alignment of the containing kernel structure.
- Time values are 32-bit, so callers must use the implementation's expected wraparound semantics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/tim_filter.h -->