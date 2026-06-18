# sources/distributed-fs/ceph-client/drivers/clk/sprd/sc9860-clk.c

## Purpose
Describes and registers the full Spreadtrum SC9860 clock topology: PMU gates, PLLs, AP clocks, always-on prediv clocks, AP/AON gates, secure MCU clocks, AGCP audio gates, GPU/VSP/CAM/DISP clocks and gates, and AP APB gates.

## Important APIs, Types, And Functions
The platform driver entry is `sc9860_clk_probe`. It uses `sprd_sc9860_clk_ids` match data to select one `sprd_clk_desc`, then calls `sprd_clk_regmap_init` and `sprd_clk_probe`. The file instantiates hundreds of static CCF objects through `CLK_FIXED_FACTOR`, `SPRD_SC_GATE_CLK`, `SPRD_GATE_CLK`, `SPRD_PLL_WITH_ITABLE_*`, `SPRD_MUX_CLK`, `SPRD_COMP_CLK`, and `SPRD_DIV_CLK`.

## Control Flow
Each compatible string maps to a descriptor for a separate register block, with comments recording physical base regions. Probe is generic: match compatible, initialize regmap for that block, then register the descriptor's onecell clock array. Parent dependencies cross descriptors by clock name, so PLL and fixed-factor clocks feed AP/AON/peripheral muxes and gates when all matching DT nodes probe.

## State And Persistence
Static descriptors hold clock metadata and onecell indexes from dt-bindings. Runtime state is regmap pointers installed into each `sprd_clk_common`, registered CCF clocks, and hardware register values changed by mux/divider/gate/PLL ops.

## Dependencies And Integration Points
Depends on Spreadtrum common helpers, dt-binding IDs for SC9860, CCF fixed-factor helpers, platform driver matching, and DT nodes with compatible strings such as `sprd,sc9860-pll`, `sprd,sc9860-aon-gate`, `sprd,sc9860-cam-gate`, and `sprd,sc9860-apapb-gate`. Consumers acquire clocks by phandle indexes.

## Risks And Edge Cases
Large static tables create high risk of mismatched ID indexes, wrong parent names, register offsets, or bit masks. Many gates use `CLK_IGNORE_UNUSED` to protect boot-critical clocks; removing one can break console, timers, or always-on infrastructure. Sparse mux table `mcu_table` must match hardware encoding. Cross-block probe ordering relies on CCF deferred resolution of parent names.

## Test Signals
Build with `CONFIG_SPRD_SC9860_CLK`, boot on SC9860 DT, and verify no provider registration errors. Check `clk_summary` for PLL children and domain clocks, exercise UART/I2C/SPI/SDIO/eMMC/GPU/VSP/CAM/DISP consumers, and confirm set/clear gate register writes through debug or hardware functionality.
