
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen4-cpg.h -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen4-cpg.h

## Purpose
Declares R-Car Gen4 custom clock types, descriptor macros, PLL configuration, selected CPG register offsets, and the Gen4 CPG registration/init functions.

## Important APIs, Types, And Functions
- `enum rcar_gen4_clk_types` defines main, PLL fixed/variable fractional types, SDSRC, SDH/SD, MDSEL, Z, OSC, RPCSRC, RPC, RPCD2, and SoC-specific base.
- Macros `DEF_GEN4_SDH`, `DEF_GEN4_SD`, `DEF_GEN4_MDSEL`, `DEF_GEN4_OSC`, `DEF_GEN4_PLL_F8_25`, `DEF_GEN4_PLL_V8_25`, `DEF_GEN4_PLL_F9_24`, `DEF_GEN4_PLL_V9_24`, and `DEF_GEN4_Z` build `cpg_core_clk` descriptors.
- `struct rcar_gen4_cpg_pll_config` carries extal, PLL1, PLL5, and oscillator predivider config.
- Exposes register offsets for SD0, CANFD, MSIOF, CSI, and DSI external clock controls.
- Declares `rcar_gen4_cpg_clk_register()` and `rcar_gen4_cpg_init()`.

## Control Flow
Gen4 SoC-specific descriptor files include this header to assign custom types and packed fields. The CPG-MSSR core calls the declared registration callback after SoC init provides PLL/mode data.

## State And Persistence
The header itself has no runtime state. It defines the compact descriptor encoding consumed by `rcar-gen4-cpg.c`, including PLL indexes in `.offset`, mode pins in `.offset`, and parent/divider pairs packed into 16-bit halves.

## Dependencies And Integration Points
Depends on CPG-MSSR descriptor macros and Linux CCF types. It is the interface between Gen4 SoC clock tables and the shared Gen4 implementation.

## Risks And Edge Cases
Enum stability is required for existing descriptors. Packed parent and divider fields must fit their bit widths. The variable 9.24 macro exists even though the implementation currently treats it as fixed. Register offsets exposed here must match the generation's CPG map.

## Test Signals
Compile all Gen4 SoC descriptor users. Runtime validation is indirect through successful registration and correct rates for PLL, Z, SD, RPC, MDSEL, OSC, and external-clock control descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen4-cpg.h -->
