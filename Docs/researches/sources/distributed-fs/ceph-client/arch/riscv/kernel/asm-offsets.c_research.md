<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/asm-offsets.c

Purpose: Generates assembler-visible offsets and constants for RISC-V task, trap, suspend, KVM, FPU, stacktrace, ftrace, and SBI structures.

Important APIs/types/functions: Emits `OFFSET()` and `DEFINE()` values for `task_struct`, `thread_info`, `pt_regs`, suspend/hibernate structs, `kvm_vcpu_arch`, `kvm_cpu_context`, `kvm_cpu_trap`, FPU state, stack frames, ftrace regs, and SBI FWFT constants.

Control flow: Kbuild compiles this C file in offset-generation mode; emitted constants are included by low-level assembly.

State and persistence: No runtime state, but generated constants encode structure layout contracts consumed by assembly.

Dependencies and integration points: Depends on scheduler, ptrace, KVM host structs, suspend, stacktrace, ftrace, SBI, and config options like SCS, USER_CFI, KVM, and dynamic ftrace.

Risks: Missing or stale offsets cause silent register corruption in entry, context switch, KVM, hibernation, or tracing assembly.

Test signals: Full config matrix builds, objdump/asm-offset checks after struct changes, KVM boot, suspend/hibernate, ftrace, and SCS/user-CFI builds.

Source read size: 542 lines, 22929 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/asm-offsets.c -->
