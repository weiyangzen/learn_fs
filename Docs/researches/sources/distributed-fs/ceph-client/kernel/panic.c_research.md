<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/panic.c -->
# sources/distributed-fs/ceph-client/kernel/panic.c

Purpose: Implements kernel panic/oops/warning handling, panic sysctls and boot parameters, panic notifier dispatch, taint tracking, warning count limits, all-CPU backtrace triggering, crash-kexec handoff, and stack protector failure panic.

Important APIs/types/functions: exported symbols include `panic_timeout`, `panic_notifier_list`, `panic_blink`, `panic_try_start()`, `panic_reset()`, `panic_in_progress()`, `panic_on_this_cpu()`, `panic_on_other_cpu()`, `nmi_panic()`, `vpanic()`, `panic()`, `test_taint()`, `add_taint()`, `warn_slowpath_fmt()` or `__warn_printk()`, and `__stack_chk_fail()`. Other key helpers are `check_panic_on_warn()`, `panic_other_cpus_shutdown()`, `print_tainted()`, `oops_enter()`, `oops_exit()`, and `__warn()`.

Control flow: sysctls expose panic timeout, taint, oops behavior, warning limit, panic sys info, and deprecated `panic_print`. `vpanic()` disables interrupts/preemption, optionally redirects panic to a configured CPU for crash dump, claims `panic_cpu`, prints the panic message and stack, lets kgdb run, optionally executes crash kexec before notifiers, shuts down other CPUs, runs panic notifiers, prints configured system info, dumps kmsg, optionally kexecs after notifiers, flushes consoles, waits/reboots according to `panic_timeout`, or loops forever while blinking/touching watchdogs. Warnings print context, check panic-on-warn/warn-limit, taint, and emit trace events.

State and persistence: Global runtime state includes `panic_cpu`, `panic_redirect_cpu`, `panic_on_oops`, `panic_on_warn`, `panic_on_taint`, `panic_timeout`, `panic_print`, `warn_count`, `tainted_mask`, and pause-on-oops counters. Sysfs exposes `warn_count`; debugfs can reset WARN_ONCE state. State persists only until reboot except taint visibility in proc/sysfs while running.

Dependencies/integration: Integrates with notifier chains, kexec/crash dump, printk/nbcon consoles, kmsg dumpers, kgdb, sysctl/sysfs/debugfs, lockdep, ftrace/tracing, sysrq/reboot, SMP stop/backtrace facilities, watchdogs, and architecture weak hooks for CPU stopping and panic redirection.

Risks: Panic paths run in broken contexts, so lock ordering, console ownership, notifier side effects, and crash-kexec timing are safety-critical. `crash_kexec_post_notifiers` improves diagnostics but can reduce dump reliability. `panic_force_cpu` depends on target CPU online state and async IPI/NMI delivery. Taint buffer sizing must track `TAINT_FLAGS_COUNT`. Warning-limit behavior can panic on expected noisy warnings if configured.

Test signals: boot parameters (`panic`, `oops=panic`, `panic_on_taint`, `panic_force_cpu`), sysctl writes and permissions, warning count limit, taint additions and verbose string formatting, panic notifier ordering, crash-kexec before/after notifiers, console replay, SMP/NMI panic contention, pause-on-oops coordination, WARN_ONCE reset debugfs, and stack protector failure panic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/panic.c -->
