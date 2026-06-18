# Group Research: FreeBSD sys/kern descriptor, devctl, dtrace, dump, environment, and eventtimer files

Scope source: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_descrip.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_descrip.c

Read completely: 5703 lines.

## Purpose
Implements FreeBSD's core file descriptor, open-file, process directory, descriptor capability, and descriptor-reporting machinery.

## Main Elements
- Maintains per-process `struct filedesc` descriptor tables using descriptor arrays plus bitmaps, with small static `NDFILE` storage and dynamic growth through `fdgrowtable()`.
- Implements descriptor syscalls and helpers: `getdtablesize`, `dup`, `dup2`, `fcntl`, `close`, `close_range`, `fstat`, `fpathconf`, and `flock`.
- Handles descriptor allocation/install/free paths via `fdalloc()`, `falloc_caps()`, `_falloc_noinstall()`, `finstall_refed()`, `_finstall()`, `fdfree()`, `closefp()`, `closef()`, and `_fdrop()`.
- Supports Capsicum descriptor rights through `struct filecaps`, including copying, moving, validation, ioctl/fcntl rights, and lockless sequence-counter validation.
- Provides lockless and locked file lookup paths: `fget_unlocked_seq()`, `fget_unlocked_flags()`, `fget_cap()`, `fget_mmap()`, `fget_fcntl()`, `fgetvp_*()`, and remote-process variants.
- Manages process descriptor table sharing and copying for fork/rfork/exec through `fdinit()`, `fdcopy()`, `fdshare()`, `fdunshare()`, `fdescfree()`, `fdcloseexec()`, and POSIX lock cleanup for shared descriptor tables.
- Manages process working/root/jail/alternate directory state through `struct pwddesc` and `struct pwd`, including `pwd_chdir()`, `pwd_chroot()`, `pwd_chroot_chdir()`, `pwd_altroot()`, `pwd_ensure_dirs()`, and `mountcheckdirs()`.
- Implements setugid descriptor safety, standard fd repair through `/dev/null`, and chroot open-directory refusal policy.
- Provides async I/O ownership helpers `fsetown()`, `fgetown()`, `funsetown()`, and `funsetownlst()` around `sigio`.
- Exports descriptor state for sysctl/procstat via `kern_proc_filedesc_out()`, `kern_proc_cwd_out()`, `sysctl_kern_file`, and kinfo packing.
- Defines fallback `badfileops`, `path_fileops` for `O_PATH`-style vnode descriptors, invalid file operation helpers, DDB file inspectors, global maxfiles sysctls, UMA zones, and `/dev/fd/{0,1,2}` alias device setup.

## Dependencies And Integration
Tightly integrated with VFS/vnodes, Capsicum, proc/session locking, kqueue, audit, ktrace, jails, RACCT, MAC-visible consumers through vnode operations, sysctl, DDB, UMA, and device aliases for `/dev/fd`, `stdin`, `stdout`, and `stderr`.

## Risk Notes
This is high-risk shared kernel infrastructure. Correctness depends on precise lock ordering, descriptor sequence counters, reference-count acquisition from lockless paths, file table growth lifetime rules, capability-right validation, close/drop races, POSIX advisory lock cleanup across shared descriptor tables, and root/current-directory vnode reference handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_descrip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_devctl.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_devctl.c

Read completely: 611 lines.

## Purpose
Implements the `/dev/devctl` kernel event channel used to report device attach, detach, nomatch, and generic notification events to userland.

## Main Elements
- Creates an eternal character device named `devctl` with open, close, read, ioctl, poll, and kqueue filter operations.
- Enforces a single-reader model with `devsoftc.inuse`.
- Maintains a bounded STAILQ event queue backed by a UMA zone, with reserve allocation and oldest-event stealing under memory pressure.
- Registers eventhandlers for `device_attach`, `device_detach`, and `device_nomatch`, converting them into textual devctl records.
- Implements blocking/nonblocking reads, `FIONBIO`, `FIOASYNC`, `FIOSETOWN`, `FIOGETOWN`, poll/select wakeups, kqueue read readiness, and SIGIO notification.
- Exposes tunables/sysctls `hw.bus.devctl_queue` and `hw.bus.devctl_nomatch_enabled`.
- Provides `devctl_notify()` for structured `!system=... subsystem=... type=...` notifications.
- Provides `devctl_safe_quote_sb()` and an optional notify hook through `devctl_set_notify_hook()` / `devctl_unset_notify_hook()`.

## Dependencies And Integration
Integrated with the newbus device tree, eventhandler framework, UMA, character devices, select/poll/kqueue, SIGIO ownership helpers from descriptor code, and optional external notification hooks.

## Risk Notes
Queue disabling destroys the UMA zone and must be serialized with producers. Event loss is possible when queue memory is exhausted. The protocol is string-based, so malformed or overflowing sbuf output is dropped.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_devctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_dtrace.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_dtrace.c

Read completely: 104 lines.

## Purpose
Provides base kernel hooks and per-process/per-thread storage allocation required for loadable DTrace kernel modules.

## Main Elements
- Declares the `kdtrace_hooks` feature.
- Exposes trap and probe hook globals: `dtrace_trap_func`, `dtrace_doubletrap_func`, `dtrace_pid_probe_ptr`, and `dtrace_return_probe_ptr`.
- Exposes syscall tracing state through `systrace_enabled` and `systrace_probe_func`.
- Defines fixed DTrace storage sizes: `KDTRACE_PROC_SIZE` and `KDTRACE_THREAD_SIZE`.
- Implements process/thread constructors and destructors that allocate and free `p_dtrace` and `td_dtrace` from `M_KDTRACE`.

## Dependencies And Integration
Used by machine-dependent trap handlers, syscall tracing, process/thread lifecycle code, and DTrace modules loaded after boot.

## Risk Notes
The fixed storage sizes form an ABI-like contract with DTrace consumers. Hook globals are intentionally nullable and must be checked/managed by provider modules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_dtrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_dump.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_dump.c

Read completely: 533 lines.

## Purpose
Implements generic kernel crash dump writing, full-memory ELF core dump generation, buffered dump I/O helpers, and optional minidump/live-dump plumbing.

## Main Elements
- Builds generic physical memory dump maps from `dump_avail` through `dumpsys_gen_pa_init()` and iterates them with `dumpsys_gen_pa_next()`.
- Provides weak/generic machine hooks for cache writeback, chunk unmap, and auxiliary headers.
- Implements block-buffered dump helpers: `dumpsys_buf_seek()`, `dumpsys_buf_write()`, and `dumpsys_buf_flush()`.
- Dumps physical memory ranges in chunks via `dumpsys_cb_dumpdata()`, respecting dumper max I/O size, watchdog patting, progress output, and console Ctrl-C abort.
- Builds full ELF core headers in `dumpsys_generic()`, including ELF header, `PT_LOAD` program headers, auxiliary headers, page-aligned segment offsets, dump start/finish headers, and common failure messages.
- When `MINIDUMP_PAGE_TRACKING` is enabled, tracks minidump progress and implements `minidumpsys()` for panic dumps and best-effort live dumps.
- Live dumps snapshot the message buffer and page dump bitset, but intentionally do not snapshot all mutable kernel state.

## Dependencies And Integration
Depends on dumperinfo backends, VM physical page metadata, machine dump hooks, ELF definitions, watchdog, console input, message buffer code, and architecture-specific `cpu_minidumpsys()`.

## Risk Notes
Dump paths run in failure or live diagnostic contexts, so they avoid complex recovery. Live dumps are explicitly best-effort and may contain inconsistent kernel state. Buffered writes must preserve block alignment and flush ordering.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_environment.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_environment.c

Read completely: 1162 lines.

## Purpose
Implements the kernel environment system: early static/loader environment ingestion, dynamic kernel environment storage, `kenv(2)`, kernel getenv/setenv APIs, tunable fetch helpers, and typed parsers.

## Main Elements
- Tracks early loader/MD environment in `md_envp` and config-generated static environment in `kern_envp`.
- Initializes static environment policy in `init_static_kenv()`, including `loader_env.disabled`, `static_env.disabled`, and `static_hints.disabled`.
- Converts early environments into dynamic `kenvp` storage in `init_dynamic_kenv()`, with duplicate variable suffixing and sanitization unless early preservation is enabled.
- Implements `sys_kenv()` for dump, loader/static dump, get, set, and unset operations with privilege and MAC checks.
- Provides `kern_getenv()`, `freeenv()`, `testenv()`, `kern_setenv()`, and `kern_unsetenv()`.
- Uses `kenv_lock` and `kenv_acquire()` / `kenv_release()` for safe in-place reads of dynamic variables.
- Parses strings, integer arrays, signed/unsigned integers, quads, booleans, and size suffixes through `getenv_string()`, `getenv_array()`, `getenv_quad()`, `getenv_bool()`, and typed wrappers.
- Exposes `getenv_is_true()` and `getenv_is_false()`.
- Implements `tunable_*_init()` helpers for SYSINIT-driven tunable fetches.

## Dependencies And Integration
Integrated with boot loader/environment handoff, config static environment/hints, SYSINIT ordering, UMA, MAC framework checks, privilege checks, eventhandlers for set/unset, and kernel tunable macros.

## Risk Notes
Early static environment pointers may be invalid across MD relocation, so initialization order matters. Dynamic environment capacity and per-value length are bounded. Duplicate handling mutates early strings temporarily and may sanitize source buffers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_environment.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_et.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_et.c

Read completely: 263 lines.

## Purpose
Implements the generic event timer registry and control helpers used by platform timer drivers and CPU timer-selection code.

## Main Elements
- Maintains a global quality-sorted SLIST of registered `struct eventtimer` instances protected by `et_eventtimers_mtx`.
- `et_register()` validates timer start support, prints timer quality/frequency, creates per-timer sysctl nodes, and inserts by descending quality.
- `et_deregister()` invokes an optional deregister callback, removes the timer, and tears down sysctls.
- `et_change_frequency()` delegates active timer frequency changes to `cpu_et_frequency()`.
- `et_find()` searches inactive timers by name, quality, and required flag bits.
- `et_init()` marks a timer active and installs event/deregister callbacks and callback argument.
- `et_start()` validates active state, one-shot/periodic capability constraints, clamps first/period values to min/max, and calls the hardware start method.
- `et_stop()`, `et_ban()`, and `et_free()` stop, disable capabilities, and deactivate timers.
- Exposes `kern.eventtimer.choice` sysctl showing available timers and qualities.

## Dependencies And Integration
Used by machine/platform event timer drivers and CPU timer management. Exposes timer metadata under `kern.eventtimer.et.<name>` sysctls.

## Risk Notes
Timer registration ordering controls default selection. Start-time validation catches capability mismatches with assertions, so incorrect driver flags can panic debug kernels or misconfigure timer behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_et.c -->