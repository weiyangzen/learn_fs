<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/flush_icache.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/flush_icache.S

Purpose: Provides the vDSO implementation of `__vdso_flush_icache`.

Important APIs/types/functions: Defines `__vdso_flush_icache`.

Control flow: Loads the RISC-V flush-icache syscall number and executes `ecall`, returning the kernel result to userspace.

State and persistence: No local state; it affects instruction-cache coherency through the syscall.

Dependencies and integration points: Exported through vDSO symbol versioning and wraps `riscv_flush_icache` in `sys_riscv.c`.

Risks: Register argument preservation and syscall number must match ABI.

Test signals: Userspace JIT cache flush via vDSO and fallback syscall equivalence.

Source read size: 26 lines, 474 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/flush_icache.S -->
