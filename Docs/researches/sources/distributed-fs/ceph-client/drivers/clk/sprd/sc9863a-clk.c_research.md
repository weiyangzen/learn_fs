# sources/distributed-fs/ceph-client/drivers/clk/sprd/sc9863a-clk.c

## Purpose
Defines the Spreadtrum SC9863A clock providers and platform driver, covering PMU PLL gates, PLL/MPLL/RPLL/DPLL blocks, AON clocks, AP clocks, AHB/APB gates, multimedia gates, camera sensor gates, and AP APB gates.

## Important APIs, Types, And Functions
`sc9863a_clk_probe` is the platform probe. `sprd_sc9863a_clk_ids` maps compatible strings to descriptors. The file uses parent-data-aware macros (`SPRD_*_DATA`, `SPRD_*_HW`, `SPRD_*_FW_NAME`) in addition to fixed-factor and PLL macros, allowing direct `clk_hw` parent references and firmware-name parents.

## Control Flow
Each DT clock node probes independently, selects its descriptor, initializes the regmap, and registers the descriptor's onecell clocks. The topology starts with PLL gates and PLLs, derives fixed-factor PLL outputs, then provides AON/AP muxes, composites, dividers, and gates for CPU, buses, storage, display, GPU, multimedia, camera, timers, serial, SPI, I2C, and audio domains.

## State And Persistence
Static clock objects and onecell arrays encode all IDs and register fields. Runtime state is the assigned regmap, CCF registration records, OF providers, and hardware state in set/clear and configuration registers.

## Dependencies And Integration Points
Depends on dt-bindings for SC9863A, Spreadtrum common helper modules, regmap/syscon/MMIO access, CCF parent data APIs, and DT compatibles such as `sprd,sc9863a-aon-clk`, `sprd,sc9863a-ap-clk`, `sprd,sc9863a-mm-gate`, and `sprd,sc9863a-apapb-gate`.

## Risks And Edge Cases
This table mixes parent strings, firmware names, and direct `clk_hw` parent references; using the wrong macro can break parent lookup. Some fixed-factor `dpll1-*` children are parented from `dpll0.common.hw`, which should be checked against hardware intent. Critical gates use `CLK_IGNORE_UNUSED`, including console-related UART1 and always-on infrastructure. `SPRD_GATE_NON_AON` camera sensor gates depend on parent state checks to avoid unsafe reads.

## Test Signals
Boot SC9863A with all clock nodes present and inspect provider registration logs. Validate PLL and fixed-factor rates in `clk_summary`, confirm console UART remains enabled, test I2C/SPI/SDIO/eMMC/display/GPU/camera/audio consumers, and verify non-AON gate reads do not fault when the multimedia parent is disabled.
