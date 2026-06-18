# sources/distributed-fs/ceph-client/drivers/clk/pistachio/Makefile

Purpose: Builds the Pistachio clock support objects.

Important APIs, types, and functions: Always adds `clk.o`, `clk-pll.o`, and `clk-pistachio.o` when the directory is entered.

Control flow: Kbuild links the provider helper, PLL implementation, and SoC descriptor/topology file together.

State and persistence: Build composition only.

Dependencies and integration points: Depends on parent Kbuild selecting this directory under `COMMON_CLK_PISTACHIO`. All three objects are required because the SoC topology calls helper and PLL registration functions.

Risks: There is no conditional split for subcontrollers; any build issue in one object affects the whole Pistachio clock driver.

Test signals: Build with `COMMON_CLK_PISTACHIO=y` and verify no unresolved symbols around `pistachio_clk_register_*`.
