# Research: sources/distributed-fs/ceph-client/include/linux/panic.h

Purpose: `panic.h` exports the kernel panic/oops/taint public interface. It declares panic entry points, panic synchronization state, panic policy knobs, and taint flag definitions used across crash handling and diagnostics.

Important APIs/types/functions: core calls are `panic()`, `vpanic()`, `nmi_panic()`, `check_panic_on_warn()`, `oops_enter()`, `oops_exit()`, `oops_may_print()`, `panic_try_start()`, `panic_reset()`, `panic_in_progress()`, `panic_on_this_cpu()`, `panic_on_other_cpu()`, `set_arch_panic_timeout()`, `add_taint()`, `test_taint()`, `get_taint()`, `print_tainted()`, and `print_tainted_verbose()`. State includes `panic_cpu`, `panic_redirect_cpu`, `panic_timeout`, `panic_print`, `panic_on_oops`, `panic_on_warn`, `panic_on_taint`, and `crash_kexec_post_notifiers`.

Control flow and state: panic paths claim a global panic CPU, optionally redirect execution to a configured CPU, print diagnostics, run configured crash behavior, and never return. Taint state accumulates bit flags such as proprietary modules, warnings, bad pages, livepatch, or test taints; it persists in kernel memory for the boot lifetime and influences diagnostics and policy.

Dependencies and integration points: depends on compiler attributes, stdarg/types, atomics, pt_regs, crash-kexec, sysctl, watchdog/oops paths, stack protector failure, and architecture init code.

Risks and test signals: risks include double-panic races, unsafe NMI context behavior, incorrect taint indexing, and misconfigured timeout defaults. Tests rely on fault injection, WARN/oops paths, panic-on-warn/oops sysctls, taint reporting, crash-kexec notifier ordering, and architecture panic timeout checks.
