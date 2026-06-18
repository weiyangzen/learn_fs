# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-pll-a10.c

Purpose: Arria10 PLL helper and clock-manager base mapper.

Important APIs/types/functions: global `clk_mgr_a10_base_addr`; `clk_pll_recalc_rate()`; `clk_pll_get_parent()`; `__socfpga_pll_init()`; `socfpga_a10_pll_init()`.

Control flow: maps `"altr,clk-mgr"`, creates a PLL clock from DT register/parents/name, registers it, and publishes a simple provider. The global base is then used by Arria10 gate/peripheral helpers.

State and persistence behavior: global mapped clock-manager base; per-PLL register pointer and bit index; hardware VCO/source registers persist state.

Dependencies/integration points: OF clock-manager node, shared `clk.h`, CCF, and Arria10 helper files.

Risks: missing base mapping triggers `BUG_ON`; parent collection uses a fixed maximum; misspelled `SOCFGPA_MAX_PARENTS` is harmless but notable.

Test signals: Arria10 boot, PLL parent/rate validation, dependent helper init ordering, and malformed DT checks.
