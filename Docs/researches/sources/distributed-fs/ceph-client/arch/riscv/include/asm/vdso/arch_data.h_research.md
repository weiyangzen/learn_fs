<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/arch_data.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/arch_data.h

Purpose: Defines RISC-V architecture-specific data embedded in vDSO data pages.

Important APIs/types/functions: Provides arch data structures/fields consumed by vDSO code.

Control flow: Kernel updates data, vDSO reads it locklessly with generic vDSO sequencing.

State and persistence: Persistent shared vvar data visible to user space.

Dependencies and integration points: Used by vDSO gettimeofday/getrandom/processor helpers and generic vDSO data definitions.

Risks: Layout changes are user ABI sensitive for the vDSO image.

Test signals: vDSO ABI/selftests and clock/getrandom correctness tests.

Source read size: 23 lines, 638 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/arch_data.h -->
