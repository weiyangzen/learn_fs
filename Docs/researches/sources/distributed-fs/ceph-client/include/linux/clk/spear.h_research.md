# sources/distributed-fs/ceph-client/include/linux/clk/spear.h

Purpose: This header declares early clock initialization entry points for ST SPEAr SoC families.

Important APIs/types/functions: APIs are `spear3xx_clk_init`, `spear6xx_clk_init`, `spear1310_clk_init`, and `spear1340_clk_init`, each guarded by the relevant `CONFIG_ARCH_*` or machine option with no-op fallback stubs.

Control flow: Architecture setup passes mapped miscellaneous, SoC config, or RAS register bases to the matching init function. The implementation registers clocks and programs family-specific setup.

State and persistence behavior: State is hardware register configuration and CCF registration. Disabled-family builds intentionally compile calls into no-ops.

Dependencies and integration points: The header integrates SPEAr platform init, early boot MMIO mapping, and CCF provider setup.

Risks: Passing the wrong base pointer or compiling with the wrong family option can leave required clocks unregistered. The `__init` lifecycle means pointers and functions are intended for boot-time only.

Test signals: Family-specific boot tests, clock tree inspection, peripheral probe success, and compile coverage for each guarded configuration are the useful checks.
