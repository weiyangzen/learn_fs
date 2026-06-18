<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso.h

Purpose: Declares RISC-V vDSO image symbols, data page layout hooks, and mapping helpers.

Important APIs/types/functions: Exports vDSO start/end symbols, `vdso_data`, `riscv_vdso_*` declarations, and vDSO install/setup helpers.

Control flow: Architecture setup maps vDSO pages into user processes and updates shared data used by user-space fast paths.

State and persistence: Persistent state includes vDSO text image, shared vvar/vdso data, and per-mm mappings.

Dependencies and integration points: Integrates with timekeeping, signal return trampolines, ELF auxv, alternatives, and compat vDSO.

Risks: Mapping or data layout mismatches break user-space time/syscall helper ABI.

Test signals: vDSO selftests, clock_gettime/getcpu/getrandom tests, ASLR/mmap inspection, compat vDSO, and alternatives applied to vDSO.

Source read size: 52 lines, 1378 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso.h -->
