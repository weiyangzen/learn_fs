# sources/distributed-fs/ceph-client/drivers/clk/clk-bm1880.c


### Purpose
`clk-bm1880.c` is the Common Clock Framework provider for the Bitmain BM1880 SoC. It models the SoC's PLL block, system muxes, fixed gate clocks, divider clocks, and gate-plus-divider or gate-plus-mux composites, then exports a onecell provider indexed by `dt-bindings/clock/bm1880-clock.h`.

### Important APIs, Types, And Functions
The main state is `struct bm1880_clock_data`, carrying PLL and SYS MMIO bases plus `clk_hw_onecell_data`. Clock descriptions are split into `bm1880_pll_hw_clock`, `bm1880_div_hw_clock`, `bm1880_mux_clock`, `bm1880_gate_clock`, and `bm1880_composite_clock`, with static tables describing each SoC clock. Important callbacks are `bm1880_pll_recalc_rate()`, `bm1880_clk_div_recalc_rate()`, `bm1880_clk_div_determine_rate()`, and `bm1880_clk_div_set_rate()`. Registration helpers create PLLs, muxes, dividers, gates, and composites before `bm1880_clk_probe()` installs the OF provider.

### Control Flow, State, And Persistence
Probe maps two platform resources, allocates a flexible onecell array, initializes all slots to `ERR_PTR(-ENOENT)`, and registers clocks in dependency order: PLLs, standalone dividers, muxes, composites, then gates. PLL rates are read-only calculations from hardware register fields. Divider clocks use a shared spinlock and BM1880-specific behavior where an unprogrammed divider register can fall back to an `initval` before delegating math to generic divider helpers. Persistent state is the registered clock graph plus hardware register contents; managed allocation covers the provider data, but many clock objects are static or manually registered.

### Dependencies, Integration Points, Risks, And Test Signals
This driver depends on platform resources, OF compatible `bitmain,bm1880-clk`, CCF gate/mux/composite/divider helpers, BM1880 clock IDs, MMIO ordering, and consumers using onecell indices. Risks include unhandled return values in `bm1880_clk_probe()` for intermediate registration batches, incomplete unwind if a later batch fails after earlier batches succeed, critical/ignore-unused flags masking ownership bugs, and table/register mismatches for divider reset defaults. In this source snapshot there are duplicated initializer tokens in the BM1880 tables/macros, which is a build signal to verify before relying on the file. Test signals are provider registration, all DT clock IDs resolving, expected PLL rates from boot registers, rate changes updating divider fields under lock, no gating of CPU/DDR-critical clocks, and peripheral probe success for UART, eMMC/SD, USB, Ethernet, GPIO, and AXI clocks.
