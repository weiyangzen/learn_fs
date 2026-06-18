<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/suspend_entry.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/suspend_entry.S

Purpose: Provides the low-level RISC-V suspend entry/resume assembly that saves callee-saved registers, switches to the resume path, and restores execution after firmware returns.

Important APIs/types/functions: Defines assembly entry points used by `cpu_suspend()` and the resume path, including register save/restore sequences for `struct suspend_context`.

Control flow: The entry stores stack pointer, return address, and callee-saved registers into the suspend context, calls the supplied finisher, and on resume restores the saved registers and returns to C with the firmware result.

State and persistence: Persists integer register state in the caller-provided suspend context. CSR state is handled by `suspend.c`.

Dependencies and integration points: Paired tightly with C structure offsets from generated asm headers, SBI suspend finishers, and CPU context save/restore rules.

Risks: Offset drift or missing register saves corrupts resumed kernel execution. The code runs with low-level context assumptions where stack and MMU state may be constrained.

Test signals: Suspend/resume cycles with register corruption checks, objdump offset review after structure changes, and RV32/RV64 build coverage.

Source read size: 93 lines, 2489 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/suspend_entry.S -->
