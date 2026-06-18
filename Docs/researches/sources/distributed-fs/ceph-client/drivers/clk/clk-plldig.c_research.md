<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-plldig.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-plldig.c

### Purpose
`clk-plldig.c` drives the NXP LS1028A display PLLDIG block used for display output pixel clocks. It exposes a single `dpclk` clock with rate calculation and programming around a fixed or DT-specified VCO frequency.

### Important APIs, Types, And Functions
`struct clk_plldig` stores `clk_hw`, MMIO base, and VCO frequency. Clock ops include `plldig_enable()`, `plldig_disable()`, `plldig_is_enabled()`, `plldig_recalc_rate()`, `plldig_determine_rate()`, and `plldig_set_rate()`. `plldig_init()` programs multiplier and optional fractional divider from parent rate and `fsl,vco-hz`; `plldig_clk_probe()` maps resources and registers the OF provider.

### Control Flow, State, And Persistence
Probe registers `dpclk`, adds the provider, validates optional VCO range, then initializes PLLDV and PLLFD. Enable sets SSCG bypass mode; disable clears it. Rate changes clamp the requested PHI1 output range, choose an RFDPHI1 divider from VCO to target, update the divider field, wait briefly, and poll PLL lock. Persistent state is hardware registers plus cached `vco_freq`.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include platform MMIO resources, one parent clock, `readl_poll_timeout_atomic()`, and DT compatible `fsl,ls1028a-plldig`. Risks include provider being registered before `plldig_init()` failure, confusing bypass-bit checks across PLLFM versus PLLDV fields, parent-rate zero assumptions, and lock polling in atomic timeout context. Test signals include VCO property boundary tests, successful lock after `set_rate`, rate clamping to 27-600 MHz, display pipeline pixel-clock requests, and failure injection for missing parent/MMIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-plldig.c -->
