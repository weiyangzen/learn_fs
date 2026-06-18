# sources/distributed-fs/ceph-client/arch/arc/kernel/troubleshoot.c

Purpose: formats ARC register, exception, VMA, executable path, and stack-trace diagnostics for oops and fault reporting.

Important APIs/functions: `show_regs()` is the generic register dump entry point. `show_kernel_fault_diag()` records the fault address, prints the fault text, dumps registers, and prints a stack trace for kernel-mode faults. Helpers print scratch and callee-saved registers, executable path, faulting VMA, and verbose ECR decoding.

Control flow: `show_regs()` temporarily enables preemption because some diagnostic helpers may sleep, prints task path and generic debug info, decodes ECR, optionally looks up the user VMA for `regs->ret`, then prints ECR/EFA/ERET/status bits and registers. It restores preemption-disabled state before returning.

State and persistence: writes `current->thread.fault_address` in `show_kernel_fault_diag()`. It reads `current->active_mm`, current task executable file, VMA metadata, `callee_reg`, and `pt_regs`. There is no durable owned state.

Dependencies and integration: depends on proc/file/mm helpers, `asm/arcregs.h`, scheduler debug, ARC status/ECR bit definitions, and `show_stacktrace()` from `stacktrace.c`.

Risks: diagnostics run in fragile exception contexts; sleeping helpers are guarded by explicit preemption enable/disable but still rely on caller context being acceptable. VMA lookup uses the current active mm and may not reflect the faulting task in unusual contexts. Formatting must match ARC register layout.

Test signals: forced user page faults, kernel oopses, instruction fetch faults, misaligned/protection faults, and verifying output includes ECR/EFA/ERET/status/registers/path/VMA where applicable.
