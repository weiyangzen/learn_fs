
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen2-cpg.h -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen2-cpg.h

## Purpose
Defines the public Gen2 CPG interface used by R-Car Gen2 SoC descriptor files and the CPG-MSSR core callback.

## Important APIs, Types, And Functions
- `enum rcar_gen2_clk_types` assigns custom clock type IDs for main, PLL0/1/3, Z, LB, ADSP, SDH, SD0, SD1, QSPI, and RCAN clocks.
- `struct rcar_gen2_cpg_pll_config` carries extal divider and PLL multipliers, with `pll0_mult` allowed to be zero when PLL0CR should be read.
- Declares `rcar_gen2_cpg_clk_register()` and `rcar_gen2_cpg_init()`.

## Control Flow
SoC-specific code uses the enum values in `DEF_BASE()`/core clock descriptors, calls `rcar_gen2_cpg_init()` with mode and PLL data, and points CPG-MSSR at `rcar_gen2_cpg_clk_register()` for custom type registration.

## State And Persistence
The header itself stores no state. It defines the configuration structure whose values are cached by `rcar-gen2-cpg.c` during init.

## Dependencies And Integration Points
Depends on `CLK_TYPE_CUSTOM`, `struct cpg_core_clk`, `struct cpg_mssr_info`, and `struct cpg_mssr_pub` from the CPG-MSSR infrastructure. It is included by Gen2 SoC clock descriptor files.

## Risks And Edge Cases
Enum ordering starts at `CLK_TYPE_CUSTOM`; changing it can break descriptor interpretation. `pll0_mult == 0` is a meaningful sentinel. SoC files must pass a valid mode word and PLL config before registration.

## Test Signals
Build all Gen2 SoC users. Runtime validation comes from correct rate registration for every enum type and successful boot on boards using PLL0CR-derived and fixed PLL0 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen2-cpg.h -->
