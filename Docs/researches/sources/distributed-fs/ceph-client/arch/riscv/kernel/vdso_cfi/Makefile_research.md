<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso_cfi/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso_cfi/Makefile

Purpose: Builds the CFI-protected RISC-V vDSO variant by reusing the normal vDSO sources with altered object/output names.

Important APIs/types/functions: Sets `VDSO_CFI_BUILD := 1`, points `src` at the normal vDSO directory, mirrors C and assembly sources, and includes the normal vDSO Makefile.

Control flow: Kbuild re-enters the vDSO rules with CFI suffixes and source/object mappings.

State and persistence: Build-time only; produces `vdso-cfi` artifacts.

Dependencies and integration points: Depends on the normal vDSO Makefile and `vdso-cfi.S` embed wrapper.

Risks: Source mirroring must stay in lockstep with normal vDSO or CFI builds miss symbols.

Test signals: Build with vDSO CFI enabled, generated offset headers with CFI suffix, and runtime CFI vDSO mapping.

Source read size: 28 lines, 1048 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso_cfi/Makefile -->
