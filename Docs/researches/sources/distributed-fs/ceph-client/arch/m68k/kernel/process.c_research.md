# sources/distributed-fs/ceph-client/arch/m68k/kernel/process.c

## Purpose

`process.c` implements architecture-specific process, idle, restart, fork, register dump, FPU core dump, and wait-channel behavior for m68k.

## Important APIs, Types, and Functions

Key functions are `arch_cpu_idle()`, `machine_restart()`, `machine_halt()`, `machine_power_off()`, `show_regs()`, `flush_thread()`, `m68k_clone()`, `m68k_clone3()`, `copy_thread()`, `elf_core_copy_task_fpregs()`, and `__get_wchan()`. It exports `pm_power_off` and references return stubs `ret_from_fork` and `ret_from_kernel_thread`.

## Control Flow

Idle executes the m68k `stop` instruction with Atari-specific interrupt masking when required. Restart/halt delegate to machine hooks and then spin. `m68k_clone()` builds `kernel_clone_args` from pt_regs because m68k syscall arguments live in registers/stack in an architecture-specific arrangement; `m68k_clone3()` forwards to generic `sys_clone3()`. `copy_thread()` lays out a `fork_frame` at the top of the child kernel stack, either initializing a kernel-thread frame or copying the parent's switch stack and pt_regs, setting child return value `d0 = 0`, child USP, TLS, and optional FPU state. Core dump support saves or converts FPU state depending on emulator, ColdFire, or classic FPU.

## State and Persistence Behavior

The file mutates `task_struct->thread` fields such as `ksp`, `esp0`, `usp`, `fc`, FPU arrays, and thread-info TLS. It also interacts with machine hooks `mach_reset` and `mach_halt`. No file-system persistence exists.

## Dependencies and Integration Points

It depends on scheduler task stack layout, `struct switch_stack`, `struct pt_regs`, FPU feature macros, generic `kernel_clone()`, reboot hooks, and signal/ptrace expectations for saved register layout. `process.h` declares the clone wrappers used by syscall entry code.

## Risks and Edge Cases

Fork frame layout must stay synchronized with entry assembly, ptrace register offsets, and signal stack manipulation. FPU save/restore differs by emulator, ColdFire, 060, and 020/030/040; a wrong format check can corrupt user FPU context or core dumps. `__get_wchan()` assumes frame-pointer chains and stack bounds, so compiler or ABI changes can reduce reliability.

## Test Signals

Exercise `fork`, `clone`, `clone3`, kernel threads, TLS setup, core dumps with and without FPU use, and restart/halt/poweroff hooks. `show_regs()` output after forced traps should match the low-level pt_regs layout.
