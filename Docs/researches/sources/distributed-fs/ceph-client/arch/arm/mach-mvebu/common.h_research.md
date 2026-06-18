# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/common.h

Purpose: Shared MVEBU platform declarations.

Important APIs/types/functions: Declares `mvebu_restart()`, `mvebu_cpu_reset_deassert()`, `mvebu_pmsu_set_cpu_boot_addr()`, and related PM/SMP helpers depending on config.

Control flow: No runtime flow.

State and persistence: No owned state; exposes platform hooks.

Dependencies and integration points: Used by board, SMP, PM, and CPU reset files.

Risks: Prototype mismatches can break platform hook linkage.

Test signals: Compile all MVEBU variants with SMP/PM/restart options.
