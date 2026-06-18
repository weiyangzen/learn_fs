# sources/distributed-fs/ceph-client/include/linux/vtime.h

## Purpose
`vtime.h` declares virtual CPU time accounting hooks for user, kernel, idle, guest, softirq, and hardirq transitions. It abstracts native and generic virtual accounting configurations while preserving cheap stubs when accounting is disabled.

## Important APIs, Types, and Functions
Common APIs include `vtime_account_kernel()` and `vtime_account_idle()` under `CONFIG_VIRT_CPU_ACCOUNTING`. Generic accounting adds `vtime_user_enter/exit()`, `vtime_guest_enter/exit()`, and `vtime_init_idle()`. Native accounting adds `vtime_account_irq()`, `vtime_account_softirq()`, `vtime_account_hardirq()`, and `vtime_flush()`. Configuration helpers include `vtime_accounting_enabled*()` and `vtime_task_switch()`. Guest wrappers set or clear `PF_VCPU` and optionally account guest transitions. IRQ helpers include `irqtime_account_irq()`, `account_softirq_enter/exit()`, and `account_hardirq_enter/exit()`.

## Control Flow
Context switch code calls `vtime_task_switch()`. User/guest entry and exit hooks account elapsed time around context-tracking boundaries. IRQ entry helpers charge time to virtual or IRQ accounting with `SOFTIRQ_OFFSET` or `HARDIRQ_OFFSET`, and exit helpers settle softirq/hardirq state. When generic accounting is disabled on a CPU, guest wrappers still maintain `PF_VCPU`.

## State and Persistence
State is per-task and per-CPU scheduler/accounting state held outside this header. The header manipulates `current->flags` for guest mode and delegates cputime accumulation to implementation files. Counters persist only for process/kernel runtime accounting.

## Dependencies and Integration Points
Dependencies include context tracking state, scheduler task structures, `current`, IRQ accounting config, and `PF_VCPU`. Integration points include scheduler context switches, tickless accounting, KVM/guest execution, irq entry/exit, proc/task cputime readers, and idle task initialization.

## Risks
Missing entry/exit pairing corrupts cputime attribution. Config-dependent stubs can hide accounting on builds where virtual time is off. Generic accounting is tied to context tracking, so readers must handle CPUs where it is disabled. Guest wrappers must keep `PF_VCPU` correct for scheduler and accounting consumers.

## Test Signals
Signals include cputime accounting tests under native and generic configs, KVM guest time attribution, irq/softirq workload accounting, nohz_full/context-tracking tests, idle task initialization, and builds with virtual accounting disabled.
