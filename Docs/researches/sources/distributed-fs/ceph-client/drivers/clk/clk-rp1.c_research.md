<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-rp1.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-rp1.c

### Purpose
`clk-rp1.c` implements the Raspberry Pi RP1 PCIe multifunction chip clock controller. It exposes PLL cores, primary PLL outputs, phase outputs, secondary dividers, peripheral clocks, general-purpose outputs, video clocks, and variable external sources through a single onecell provider.

### Important APIs, Types, And Functions
Core types are `struct rp1_clockman`, `struct rp1_clk_desc`, `struct rp1_pll_core_data`, `struct rp1_pll_data`, `struct rp1_pll_ph_data`, `struct rp1_pll_divider_data`, and `struct rp1_clock_data`. Operation groups are `rp1_pll_core_ops`, `rp1_pll_ops`, `rp1_pll_ph_ops`, `rp1_pll_divider_ops`, `rp1_clk_ops`, and `rp1_varsrc_ops`. Registration helpers are `rp1_register_pll()`, `rp1_register_pll_divider()`, `rp1_register_clock()`, descriptor macros, `clk_desc_array`, and `rp1_clk_probe()`.

### Control Flow, State, And Persistence
Probe allocates `rp1_clockman`, maps MMIO, creates a lockless regmap guarded externally by `regs_lock`, iterates `clk_desc_array`, registers each descriptor, caches special audio/I2S/xosc pointers, and adds a onecell OF provider. PLL core ops program feedback dividers and poll lock; PLL output ops choose primary dividers; phase and secondary-divider ops enable/reset and divide PLL outputs. Peripheral clock ops choose parent selectors, integer/fractional dividers, and GPCLK output-enable bits. `cached_rate` stores audio coordination rates and varsrc rates for externally managed MIPI DSI byte clocks.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `dt-bindings/clock/raspberrypi,rp1-clocks.h`, platform MMIO, regmap, CCF parent propagation, and downstream RP1 Ethernet, UART, PWM, audio, SDIO, ADC, MIPI, DPI, VEC, and GPCLK consumers. Risks include descriptor/table drift against binding IDs, lockless regmap requiring every write sequence to hold `regs_lock`, complex audio/I2S cached-rate coupling, parent selector gaps using AUX source conventions, no explicit unwind for failed individual descriptor registration, and rate calculations near hardware max limits. Test signals include every binding ID present in `clk_summary`, PLL lock timeout coverage, parent switching with `CLK_SET_RATE_NO_REPARENT` clocks, GPCLK OE bit toggles, audio/I2S exact-rate requests, varsrc updates from display drivers, and probe failure on bad MMIO/regmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-rp1.c -->
