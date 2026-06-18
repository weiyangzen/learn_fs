<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/process.c

## Purpose
Implements OpenRISC machine restart/halt/poweroff, idle, thread creation, process start, context switch integration, register dumps, and ELF core register export.

## Important APIs, Types, And Functions
Defines `current_thread_info_set[NR_CPUS]`, `machine_restart()`, `machine_halt()`, `machine_power_off()`, `arch_cpu_idle()`, `flush_thread()`, `show_regs()`, `copy_thread()`, `start_thread()`, `__switch_to()`, `dump_elf_thread()`, and `__get_wchan()`.

## Control Flow
`copy_thread()` builds user and kernel `pt_regs` frames on the new task stack and points `ksp` at the kernel frame. `start_thread()` clears registers and sets user PC/SP/SR. `__switch_to()` disables IRQs, saves/restores FPU, updates `current_thread_info_set`, calls assembly `_switch`, then restores IRQs.

## State And Persistence
Maintains per-CPU current-thread pointer, per-task saved kernel stack pointer, FPU state, and task register frames. Restart/poweroff may issue simulator `l.nop` commands.

## Dependencies And Integration Points
Depends on scheduler, task stacks, FPU helpers, OpenRISC SPRs, `entry.S` `_switch`/`ret_from_fork`, and signal/core dump ABI.

## Risks
Stack frame layout must match `entry.S`. `__get_wchan()` is unimplemented. Poweroff/restart fallbacks are simulator-specific and may not work on real hardware without sys-off handlers.

## Test Signals
Fork/clone/kernel-thread tests, exec register setup, context-switch/FPU stress, reboot/poweroff on simulator and board platforms, and core dump register validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/process.c -->
