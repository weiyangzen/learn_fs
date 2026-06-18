<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/getrandom.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/getrandom.c

Purpose: Includes generic vDSO getrandom implementation for RISC-V.

Important APIs/types/functions: Pulls in `../../../../lib/vdso/getrandom.c`, which defines the vDSO getrandom fast path around VVAR random state.

Control flow: Runtime flow is supplied by the shared implementation: try vDSO random state and fall back to the syscall when unavailable or reseed is needed.

State and persistence: Uses generic vDSO/VVAR random state, not local state in this wrapper.

Dependencies and integration points: Built when `CONFIG_VDSO_GETRANDOM` is enabled and paired with RISC-V ChaCha assembly in `vgetrandom-chacha.S`.

Risks: Architecture wrapper must compile with vDSO restrictions and expose the expected arch ChaCha helper.

Test signals: vDSO getrandom selftests, entropy reseed fallback, and symbol export checks.

Source read size: 10 lines, 336 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/getrandom.c -->
