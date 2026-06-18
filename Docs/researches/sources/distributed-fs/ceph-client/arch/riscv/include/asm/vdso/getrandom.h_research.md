<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/getrandom.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/getrandom.h

Purpose: Provides RISC-V vDSO getrandom architecture hooks.

Important APIs/types/functions: Defines arch-specific getrandom state sizes, opaque data hooks, and syscall fallback integration.

Control flow: vDSO getrandom uses shared random state when available and falls back to the syscall on slow/error paths.

State and persistence: Shared vDSO random state and per-call buffer/counter state.

Dependencies and integration points: Generic vDSO getrandom, random subsystem, syscall ABI, and vvar mapping.

Risks: ABI/layout mistakes can return weak random data or break fallback.

Test signals: vDSO getrandom selftests, fork/thread races, and fallback syscall tests.

Source read size: 30 lines, 752 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/getrandom.h -->
