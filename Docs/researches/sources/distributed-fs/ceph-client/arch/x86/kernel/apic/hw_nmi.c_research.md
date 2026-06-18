# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/hw_nmi.c

## Purpose
This file provides APIC-backed hardware NMI watchdog support and architecture backtrace triggering. It bridges generic NMI watchdog/backtrace code to x86 APIC NMI IPI delivery.

## Important APIs, Types, And Functions
When `CONFIG_HARDLOCKUP_DETECTOR_PERF` is enabled, `hw_nmi_get_sample_period(watchdog_thresh)` computes a perf NMI sample period from `cpu_khz`. When architecture backtrace triggering is enabled, `arch_trigger_cpumask_backtrace(mask, exclude_cpu)` invokes `nmi_trigger_cpumask_backtrace()` using `nmi_raise_cpu_backtrace()`, which sends `NMI_VECTOR` to the requested CPUs via `__apic_send_IPI_mask()`. `nmi_cpu_backtrace_handler()` delegates to `nmi_cpu_backtrace()` and is registered as an `NMI_LOCAL` handler at early init.

## Control Flow
Backtrace requests from generic NMI code enter `arch_trigger_cpumask_backtrace()`, which supplies the APIC NMI raiser callback. Incoming local NMIs run the registered handler and either report a CPU backtrace or return `NMI_DONE`.

## State And Persistence
This file owns no persistent state beyond NMI handler registration. It reads `cpu_khz` and uses the APIC IPI path for delivery.

## Dependencies And Integration Points
It depends on generic NMI watchdog APIs, notifier/NMI registration, APIC IPI helpers, kprobe safety annotations, and CPU masks. It integrates with hard-lockup detection, sysrq-style CPU backtraces, panic diagnostics, and APIC NMI delivery policy.

## Risks
NMI delivery is non-maskable and can run in fragile contexts. Incorrect cpumask handling can target wrong CPUs or miss backtraces. The sample-period calculation depends on a valid `cpu_khz`; stale or inaccurate CPU frequency affects watchdog cadence.

## Test Signals
Use hardlockup watchdog enablement, triggered CPU backtraces, panic-time NMI backtraces, and logs from `nmi_cpu_backtrace()` as signals. Validate that excluded CPUs are not targeted and that APIC NMI IPIs reach all requested online CPUs.
