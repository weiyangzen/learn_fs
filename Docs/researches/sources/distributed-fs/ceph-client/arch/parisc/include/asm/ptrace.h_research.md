# sources/distributed-fs/ceph-client/arch/parisc/include/asm/ptrace.h

Purpose: defines PA-RISC ptrace/register inspection helpers used by tracing, profiling, and stack unwinding.

Important APIs/types/functions: provides `task_regs`, `user_mode`, `user_space`, `instruction_pointer`, `instruction_pointer_set`, `regs_return_value`, `regs_get_register`, `regs_query_register_offset/name`, `kernel_stack_pointer`, and stack helpers.

Control flow: ptrace, perf, kprobes, and exception code inspect or modify saved `pt_regs` fields through these helpers.

State and persistence: operates on saved task/trap register frames. Dependencies and integration: depends on `assembly.h`, uapi ptrace layout, and generic tracing/debug code.

Risks and test signals: IA queue low privilege bits make instruction-pointer masking important. Test ptrace, single-step/block-step, perf callchains, and kernel/user mode detection.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
