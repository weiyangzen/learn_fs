<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/soc.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/soc.c

Purpose: Runs early SoC-specific initialization hooks for RISC-V platforms.

Important APIs/types/functions: Provides `soc_early_init()`.

Control flow: Iterates registered `riscv_soc_early_init` callbacks from linker tables and calls each during early boot.

State and persistence: No local state; platform callbacks may initialize SoC-global state.

Dependencies and integration points: Depends on linker-table symbols and platform code that registers early SoC hooks.

Risks: Hook ordering and early-boot constraints are strict; callbacks run before many kernel subsystems are available.

Test signals: Boot platforms with registered SoC hooks and verify early errata/workaround state is installed before CPU feature and driver use.

Source read size: 28 lines, 738 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/soc.c -->
