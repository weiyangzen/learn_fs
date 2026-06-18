<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/bugs.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/bugs.c

Purpose: Provides the RISC-V architecture bug-check initialization hook.

Important APIs/types/functions: Implements `check_bugs()`.

Control flow: Called during boot after CPU feature setup; currently delegates to `riscv_check_elf_hwcap()` when MMU support is enabled.

State and persistence: Persistent effects are any CPU/hwcap validation warnings or adjustments performed by delegated helpers.

Dependencies and integration points: Integrates with generic init bug checking and RISC-V ELF hwcap/cpufeature code.

Risks: Too little validation can expose incorrect HWCAPs; too much validation can reject working systems.

Test signals: Boot logs across extension sets, HWCAP/getauxval tests, MMU and NOMMU builds.

Source read size: 60 lines, 1401 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/bugs.c -->
