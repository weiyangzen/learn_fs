<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/ptrace.h

Purpose: Defines the kernel trap register frame and helper accessors used by RISC-V ptrace, syscall, tracing, profiling, and exception code.

Important APIs/types/functions: Important items are `struct pt_regs`, `user_mode()`, `instruction_pointer()`, `user_stack_pointer()`, `frame_pointer()`, `regs_return_value()`, `regs_set_return_value()`, `regs_get_register()`, `regs_get_kernel_argument()`, and `regs_irqs_disabled()`.

Control flow: Helpers read and write saved register fields directly. Register-offset validation prevents out-of-range inspection, and argument helpers expose a0-a7 for tracing.

State and persistence: `pt_regs` persists the architectural trap frame: EPC, integer registers, status, bad address, cause, and original syscall a0.

Dependencies and integration points: Consumed by entry.S, traps, syscall tracing, ftrace, kprobes/uprobes, perf, signal handling, and KVM offset generation.

Risks: Layout or status interpretation changes must match assembly and UAPI register ABI or debugging, signals, and syscall restart break.

Test signals: Ptrace regset tests, signal frame tests, syscall tracing/seccomp, ftrace/perf/kprobe tests, and asm-offset validation.

Source read size: 185 lines, 4416 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/ptrace.h -->
