# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-r8a73a4.c

Purpose: This legacy CPG provider registers core clocks for the Renesas R-Mobile APE6 (`r8a73a4`) SoC.

Important APIs, types, and functions: The file defines `struct r8a73a4_cpg`, DIV4 clock tables, PLL register offsets, `r8a73a4_cpg_register_clock()`, and `r8a73a4_cpg_clocks_init()`. It registers fixed-factor clocks and divider-table clocks through CCF helpers.

Control flow: `CLK_OF_DECLARE()` binds `renesas,r8a73a4-cpg-clocks`. Init counts `clock-output-names`, allocates onecell data, maps the CPG registers, then iterates names and dispatches each through the string-based clock registration function.

State and persistence: Hardware CPG registers select the main clock parent/divider, PLL multipliers/dividers, Z/Z2 ratios, and DIV4 settings. The driver stores a spinlock for divider writes and an allocated onecell clock array for provider lookup.

Dependencies and integration: Depends on OF, CCF, IO mapping, spinlocks, and legacy Renesas clock declarations. It selects `CLK_RENESAS_CPG_MSTP` and `CLK_RENESAS_DIV6` via Kconfig for related module clocks.

Risks: Unknown clock names return `-EINVAL`, so DT output names must match the string dispatcher. Several PLL enable bits are noted as TODO/XXX and PLLs are modeled as fixed-factor clocks. Allocation failures intentionally leak partial state because early boot cannot recover cleanly.

Test signals: Boot an R8A73A4 DT, confirm all listed output names register, compare PLL and divider rates to hardware registers, test DIV4 rate changes, and ensure BSC/`zb_clk` integration with MSTP PM domain works.
