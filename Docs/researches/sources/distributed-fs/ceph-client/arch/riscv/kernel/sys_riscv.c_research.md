<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sys_riscv.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/sys_riscv.c

Purpose: Implements RISC-V-specific syscalls for `mmap`, `mmap2`, instruction-cache flushing, and the architecture no-syscall wrapper.

Important APIs/types/functions: Provides `riscv_sys_mmap()`, `SYSCALL_DEFINE6(mmap)`, `SYSCALL_DEFINE6(mmap2)`, `SYSCALL_DEFINE3(riscv_flush_icache)`, and `__riscv_sys_ni_syscall()`.

Control flow: `mmap` and `mmap2` normalize page offsets and delegate to `ksys_mmap_pgoff()` after alignment checks. `riscv_flush_icache` validates flags and calls `flush_icache_mm()` for the current mm over the requested range.

State and persistence: Affects VMAs through generic mmap and updates instruction-cache visibility for the current address space; no local persistent state.

Dependencies and integration points: Used by syscall table, vDSO `__vdso_flush_icache`, JIT/self-modifying-code userspace, and generic MM.

Risks: Offset overflow or misalignment must be rejected. I-cache flushing semantics are ABI-visible for JITs and cross-thread execution.

Test signals: mmap/mmap2 ABI tests on RV32/RV64, invalid offset cases, JIT icache flush across threads, and seccomp/syscall-table coverage.

Source read size: 85 lines, 2906 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sys_riscv.c -->
