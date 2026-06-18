# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-pll.c

Purpose: legacy 32-bit SoCFPGA PLL helper and clock-manager base mapper.

Important APIs/types/functions: global `clk_mgr_base_addr`; `clk_pll_recalc_rate()`; `clk_pll_get_parent()`; `__socfpga_pll_init()`; `socfpga_pll_init()`.

Control flow: maps `"altr,clk-mgr"`, builds a PLL clock from DT register/parent data, registers it, publishes a simple provider, and leaves the global base for legacy gate/peripheral helpers.

State and persistence behavior: global clock-manager base; per-PLL register pointer and external-enable bit; hardware bypass/source/divider registers.

Dependencies/integration points: OF clock manager compatible, shared `clk.h`, CCF, and old SoCFPGA DT clock nodes.

Risks: only `MAINPLL_BYPASS` is consulted although more bypass bits are defined; missing clock-manager mapping panics; DT parent order and offsets must match hardware.

Test signals: legacy SoCFPGA boot, PLL rate checks with bypass, dependent helper registration, and clock-provider log inspection.
