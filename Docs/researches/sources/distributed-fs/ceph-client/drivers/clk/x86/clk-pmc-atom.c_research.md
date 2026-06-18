<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-pmc-atom.c -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/clk-pmc-atom.c

## Purpose

`clk-pmc-atom.c` exposes Intel Atom PMC platform clocks for BayTrail and CherryTrail SoCs. It provides fixed parent clocks plus six PMC-controlled platform clocks with mux and gate control.

## Important APIs, Types, And Functions

`struct clk_plt` models a PMC clock-control register and clkdev lookup. Helpers translate register frequency/gate fields to parent/enabled state. CCF ops set/get parent, force enable/disable, and determine rate through mux logic. Registration helpers create fixed-rate parents, per-clock PMC clocks, and aliases `mclk` and `ether_clk`.

## Control Flow

The built-in `clk-pmc-atom` platform driver gets `pmc_clk_data`, registers all parent fixed-rate clocks, registers `PMC_CLK_NUM` platform clocks, creates aliases, and stores driver data. Remove drops aliases, unregisters platform clocks, and unregisters parents.

## State And Persistence Behavior

Parent and gate state persists in PMC registers. Firmware-enabled clocks can be marked critical at registration when `pmc_data->critical` is set. Runtime lookup structures are explicitly dropped on remove.

## Dependencies And Integration Points

It depends on platform data from `pmc_atom`, CCF, clkdev aliases, raw MMIO, and spinlocks. Consumers use named lookups such as `mclk` and `ether_clk`.

## Risks And Test Signals

Risks include direct indexing for aliases `clks[3]` and `clks[4]`, cleanup corner cases if later clock registration fails, and preserving firmware-critical state. Test parent switching between XTAL/PLL, gate modes, critical clock handling, remove cleanup, and Ethernet/camera audio consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-pmc-atom.c -->
