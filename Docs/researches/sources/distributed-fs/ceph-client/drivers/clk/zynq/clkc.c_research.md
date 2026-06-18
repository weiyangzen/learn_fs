<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynq/clkc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/zynq/clkc.c

## Purpose

`zynq/clkc.c` is the early Zynq-7000 PS clock-controller setup for SLCR clocks. It registers PLL muxes, CPU clocks, DDR/DCI clocks, FPGA fabric clocks, peripheral clocks, GEM/CAN/debug special muxes, APER gates, and the onecell DT provider.

## Important APIs, Types, And Functions

Global `zynq_clkc_base` points into SLCR. `enum zynq_clk` defines provider indices. `zynq_clk_register_fclk()` builds mux/div0/div1/gate chains for four FPGA clocks and optionally enables them from `fclk-enable`. `zynq_clk_register_periph_clk()` builds common mux/div/gate chains for LQSPI, SMC, PCAP, SDIO, UART, and SPI. `zynq_clk_setup()` registers all clocks from DT names. `zynq_clock_init()` locates `xlnx,ps7-clkc` and computes the SLCR base from the parent node data.

## Control Flow

`zynq_clock_init()` establishes `zynq_clkc_base`; `CLK_OF_DECLARE()` invokes `zynq_clk_setup()` for the clock node. Setup reads every `clock-output-names` entry, registers `ps_clk`, three PLLs plus bypass muxes, CPU fixed factors/gates, SWDT external mux, DDR/DCI clocks, four FCLKs, standard peripheral clocks, GEM EMIO muxes, CAN MIO muxes, debug mux/gates preserving bootloader-enabled state, and APER gates. It BUGs on missing names or failed clock registrations.

## State And Persistence Behavior

Clock state persists in SLCR registers. Static `clks[]`, `ps_clk`, and `clk_data` hold provider state permanently. Some critical CPU/DDR/DCI/debug clocks are prepared/enabled to preserve boot state.

## Dependencies And Integration Points

It depends on OF address data from the SLCR parent, Zynq PLL helper, CCF mux/divider/gate/fixed-factor APIs, DT properties `clock-output-names`, `ps-clk-frequency`, `fclk-enable`, and optional EMIO/MIO clock names.

## Risks And Test Signals

Risks include deliberate `BUG()` on DT omissions, many unchecked intermediate registration failures, dynamic parent arrays filled with dummy names, and dependence on SLCR parent `data`. Test full Zynq boot, all provider indices, FCLK enable bits, GEM/CAN EMIO/MIO parent choices, debug-clock preservation, and `clk_summary` rates after bootloader handoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynq/clkc.c -->
