# sources/distributed-fs/ceph-client/arch/alpha/kernel/process.c

## Purpose
`process.c` implements Alpha-specific process lifecycle hooks: idle support, restart/halt/poweroff, SRM-aware shutdown cleanup, register display, exec-thread setup, thread cloning, ELF core register export, floating-point core export, and wait-channel lookup.

## Important APIs, Types, And Functions
- `pm_power_off` defaults to `machine_power_off` and is exported.
- `arch_cpu_idle()` and `arch_cpu_idle_dead()` use `wtint()` on `CONFIG_ALPHA_WTINT` systems.
- `struct halt_info` carries reboot mode and optional restart command across `on_each_cpu()`.
- `common_shutdown_1()` is the low-level per-CPU shutdown handler.
- `machine_restart()`, `machine_halt()`, and `machine_power_off()` all call `common_shutdown()`.
- `show_regs()` delegates to `dik_show_regs()`.
- `start_thread()` sets user PC, user PS, and user stack pointer for exec.
- `flush_thread()` resets FPU exception state and TLS/UNIQUE.
- `copy_thread()` builds child kernel stacks for fork and kernel threads.
- `dump_elf_thread()`, `dump_elf_task()`, and `elf_core_copy_task_fpregs()` export register state for ELF core dumps.
- `thread_saved_pc()` and `__get_wchan()` derive blocked-thread wait PCs from Alpha switch stack frames.

## Control Flow
Shutdown is broadcast to all CPUs. Secondaries clear HWRPB flags, mark themselves not present/possible, and halt. The boot CPU records warm/cold bootstrap or halt flags in its HWRPB per-CPU structure, waits for other CPUs to disappear, restores SRM console/video/PCI/HAE state when booted from SRM, invokes `alpha_mv.kill_arch()`, optionally stops SRM paging, and halts. Non-SRM halt/poweroff may return to a loop because MILO cannot reliably honor HWRPB halt state.

`copy_thread()` handles two paths. Kernel threads get zeroed child frames, `ret_from_kernel_thread`, function pointer/argument in saved registers, HAE cache, zeroed FP state, and no user stack. User clones inherit register and switch-stack state, set child return registers for fork semantics, optionally set TLS from `CLONE_SETTLS`, and arrange return through `ret_from_fork`.

## State And Persistence
Shutdown mutates HWRPB per-CPU flags, CPU masks, HAE state, and possibly PCI configuration visible to SRM. Thread setup mutates `thread_info` PCB fields, FPU save area, stack frames, and TLS/UNIQUE. Core dump helpers read stack and thread state without persistence.

## Dependencies And Integration Points
The file depends on HWRPB layout, Alpha PAL/halt primitives, SRM status from `setup.c`, machine-vector `kill_arch` and `hae_cache`, PCI SRM restore from `pci_impl.h`, SMP CPU masks, `ret_from_fork`/`ret_from_kernel_thread` assembly entries, FPU helpers, and ELF core infrastructure.

## Risks
- Shutdown paths manipulate interrupt and console state in unusual contexts, including hardirq SysRq paths.
- `__get_wchan()` depends on fragile stack-frame layout and schedule frame offsets.
- Incorrect fork register semantics can break OSF/1-compatible ABI expectations around `r20`.
- SRM restore and HAE restore order matters for firmware reboot reliability.

## Test Signals
- Reboot/halt/poweroff under SRM and non-SRM boot paths.
- SMP shutdown confirms secondaries halt and CPU masks drain.
- Fork, clone with `CLONE_SETTLS`, kernel thread creation, and exec smoke tests.
- ELF core dumps contain expected integer, UNIQUE, user stack, and FP register data.
- `ps`/wait-channel reporting remains stable under blocked tasks.
