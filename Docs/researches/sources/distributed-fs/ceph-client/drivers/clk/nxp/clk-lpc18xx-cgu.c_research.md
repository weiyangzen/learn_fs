# sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc18xx-cgu.c

Purpose: Implements the LPC18xx/LPC43xx Clock Generation Unit. It registers source clocks, PLLs, intermediate dividers, and base clocks used by CCU branch clocks and other consumers.

Important APIs, types, and functions: Source and base clock names are indexed by dt-binding IDs. `struct lpc18xx_cgu_src_clk_div`, `struct lpc18xx_cgu_base_clk`, and `struct lpc18xx_cgu_pll_clk` describe composite clocks. PLL0 helper functions encode/decode the special MDEC multiplier and bandwidth fields. `lpc18xx_pll0_set_rate()`, `lpc18xx_pll0_recalc_rate()`, and `lpc18xx_pll1_recalc_rate()` implement PLL rate behavior.

Control flow: `lpc18xx_cgu_init()` maps CGU registers, registers fixed IRC and external oscillator gate, registers PLL0USB/PLL0AUDIO/PLL1, registers IDIVA-E dividers, registers all base clocks, and exposes a one-cell provider for base clocks.

State and persistence: Static arrays store descriptors and base clock pointers. MMIO registers hold mux, divider, gate, and PLL state. PLL0 set-rate powers down the PLL, writes multiplier and pre/post dividers, powers up, polls lock with retries, then enables output.

Dependencies and integration points: Depends on `dt-bindings/clock/lpc18xx-cgu.h`, external oscillator parent from DT, CCF mux/divider/gate/composite ops, and CCU branch clocks consuming base clock names.

Risks: `lpc18xx_pll0_determine_rate()` and `set_rate()` appear to reject `parent_rate < rate`, which is unusual for a multiplying PLL and should be verified against hardware intent. PLL0 supports only pre/post divider values of 1. Gate `is_enabled()` recursively checks parents to avoid reporting enabled clocks whose source is off. Base clock table contains reserved holes returning `-ENOENT`.

Test signals: Verify one-cell base clocks for all non-reserved IDs. Test PLL0 rate changes on USB/audio PLLs, including lock timeout paths. Ensure CCU can consume registered base names and `clk_summary` traversal does not access disabled clock domains unsafely.
