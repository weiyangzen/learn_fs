# sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa.c

Purpose: Provides common PXA clock infrastructure for CKEN peripheral clocks, DT one-cell publishing, turbo switching, core PLL changes, and frequency selection.

Important APIs, types, and functions: `struct pxa_clk` combines low-power and high-power fixed factors with a gate. `clk_pxa_cken_init()` registers CKEN composite clocks. `clkdev_pxa_register()` populates the global one-cell array and clkdev aliases. `pxa2xx_core_turbo_switch()` toggles CLKCFG turbo state through ARM coprocessor p14. `pxa2xx_cpll_change()` safely updates CCCR and SDRAM refresh timing. `pxa2xx_determine_rate()` selects exact or closest supported frequency entries.

Control flow: SoC files define CKEN descriptors and call `clk_pxa_cken_init()`. Rate recalc chooses low-power or high-power fixed factor based on `is_in_low_power()`. Core PLL changes disable IRQs, preset MDREFR for safe SDRAM refresh, write CCCR, execute aligned coprocessor FCS sequence, post-update MDREFR, and restore IRQs.

State and persistence: Global `pxa_clocks[]` backs the DT one-cell provider. `pxa_clk_lock` protects CKEN gates. Frequency state persists in CCCR, CLKCFG, and MDREFR hardware registers.

Dependencies and integration points: Depends on PXA SMEMC helpers, ARM-specific p14 instructions, CCF, clkdev, and dt-binding clock IDs. SoC-specific files provide frequency tables and MDREFR DRI calculators.

Risks: The inline assembly is architecture-specific and timing-sensitive. Incorrect MDREFR preset/postset handling can corrupt SDRAM timing during frequency changes. CKEN composite clocks pass the same `struct clk_hw` as mux and rate hardware, requiring care if CCF internals change.

Test signals: Frequency transition tests should validate SDRAM remains stable and rates update in `clk_summary`. CKEN enable/disable should toggle expected bits under lock. DT consumers should resolve IDs through `clk_pxa_dt_common_init()`.
