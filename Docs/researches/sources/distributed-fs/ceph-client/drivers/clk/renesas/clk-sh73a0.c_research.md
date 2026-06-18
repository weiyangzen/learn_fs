# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-sh73a0.c

Purpose: This file registers SH-Mobile AG5 (`sh73a0`) core CPG clocks including main, PLL, DSI PHY, Z, and DIV4-derived clocks.

Important APIs, types, and functions: It defines `struct sh73a0_cpg`, DIV4 and Z divider tables, `sh73a0_cpg_register_clock()`, and `sh73a0_cpg_clocks_init()`. It uses `clk_register_fixed_factor()` and `clk_register_divider_table()`.

Control flow: `CLK_OF_DECLARE()` binds `renesas,sh73a0-cpg-clocks`. Init counts outputs, allocates onecell data, maps CPG registers, writes known values to SDHI clock control registers, then registers each output name.

State and persistence: Hardware registers determine main parent, PLL enable/multiplier state, DSI PHY factors, and divider fields. The init writes to SD0/SD1/SD2 clock control registers persist as known SDHI defaults. A spinlock protects divider table changes.

Dependencies and integration: Depends on OF, CCF, IO mapping, spinlocks, and Renesas MSTP/DIV6 support selected by Kconfig. Consumers rely on DT output-name ordering.

Risks: PLL handling models configurable PLLs as fixed factors. Unsupported names fail. SDHI register writes are board-wide policy embedded in the provider. Allocation failure paths intentionally leak.

Test signals: Boot SH73A0, compare CPG rates and SDHI initial state with datasheet expectations, test DSI PHY clock derivation, inspect onecell provider outputs, and run MSTP module-clock attach tests.
