
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen3-cpg.h -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen3-cpg.h

## Purpose
Declares R-Car Gen3 custom clock types, descriptor-construction macros, PLL configuration, key register offsets, and the Gen3 CPG registration/init functions.

## Important APIs, Types, And Functions
- `enum rcar_gen3_clk_types` defines main, PLL0-4, SDH/SD, R, MDSEL, Z/ZG, OSC, RCKSEL, RPCSRC variants, RPC, RPCD2, and a SoC-specific base.
- Macros such as `DEF_GEN3_SDH`, `DEF_GEN3_SD`, `DEF_GEN3_MDSEL`, `DEF_GEN3_PE`, `DEF_GEN3_OSC`, `DEF_GEN3_RCKSEL`, `DEF_GEN3_Z`, `DEF_FIXED_RPCSRC_E3`, and `DEF_FIXED_RPCSRC_D3` pack descriptor fields for `rcar_gen3_cpg_clk_register()`.
- `struct rcar_gen3_cpg_pll_config` carries extal, PLL1, PLL3, and oscillator predivider data.
- Declares `rcar_gen3_cpg_clk_register()` and `rcar_gen3_cpg_init()`.

## Control Flow
Gen3 SoC descriptor files use the macros to populate `struct cpg_core_clk` arrays. The CPG-MSSR core calls the declared registration callback after `rcar_gen3_cpg_init()` caches SoC-specific mode/config values.

## State And Persistence
The header stores no runtime state. It defines packed fields that later become parent indices, divider values, mode-bit offsets, or register offsets consumed by the C implementation.

## Dependencies And Integration Points
Depends on the CPG-MSSR descriptor format and CCF-facing registration callback signature. It exposes `CPG_RPCCKCR` and `CPG_RCKCR` offsets to SoC files that need them.

## Risks And Edge Cases
Several macros pack two parent IDs or dividers into one integer; parent IDs must fit 16-bit fields. Enum order must stay compatible with existing descriptors. `DEF_GEN3_PE` hardcodes mode bit 12 semantics. Wrong `osc_prediv` or mode-bit packing causes silent rate errors.

## Test Signals
Compile all Gen3 SoC descriptor files and verify each custom type reaches the expected case in `rcar_gen3_cpg_clk_register()`. Runtime signals include correct SD/RPC/R/Z/PLL rates and mode-dependent parent selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen3-cpg.h -->
