<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/vsyscall.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/vsyscall.h

Purpose: Declares kernel-to-vDSO vsyscall update hooks for RISC-V.

Important APIs/types/functions: Provides arch hooks used by generic vDSO data update code.

Control flow: Kernel timekeeping invokes hooks to update shared vvar/vsyscall data.

State and persistence: Shared vDSO data pages.

Dependencies and integration points: Generic vDSO, timekeeping, and vvar mapping.

Risks: Wrong update hooks produce stale or inconsistent vDSO results.

Test signals: vDSO clock tests and timekeeping update stress.

Source read size: 14 lines, 333 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/vsyscall.h -->
