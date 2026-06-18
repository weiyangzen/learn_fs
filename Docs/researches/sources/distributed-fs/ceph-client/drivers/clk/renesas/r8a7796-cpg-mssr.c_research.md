<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7796-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7796-cpg-mssr.c

## Purpose
`r8a7796-cpg-mssr.c` provides the R-Car M3-W/M3-W+ Gen3 CPG/MSSR clock data. It supplies the standard Gen3 PLL/S/SD/RPC/div6 core clocks and a module gate table for M3-W peripherals, with a small revision-compatible fixup for M3-W+.

## Important APIs, Types, and Functions
Important symbols are `r8a7796_core_clks[]`, mutable `r8a7796_mod_clks[]`, `r8a7796_crit_mod_clks[]`, `r8a77961_mod_nullify[]`, `cpg_pll_configs[]`, `r8a7796_cpg_mssr_init()`, and `r8a7796_cpg_mssr_info`. The file uses `<linux/of.h>`, `of_device_is_compatible()`, and `mssr_mod_nullify()` to remove module `617` (`FCPCI0`) for `"renesas,r8a77961-cpg-mssr"`.

## Control Flow, State, and Persistence
Init reads CPG mode pins, decodes the four Gen3 PLL mode bits, validates nonzero `extal_div`, applies the M3-W+ nullification fixup when the compatible is `r8a77961`, and then calls `rcar_gen3_cpg_init()`. The module clock table is `__initdata` instead of `const` because the nullify step mutates it during init. After boot, state exists in the common clock framework and hardware registers.

## Dependencies and Integration Points
The file depends on `dt-bindings/clock/r8a7796-cpg-mssr.h`, OF matching, Gen3 CPG code, common CPG/MSSR support, and reset-mode-pin access. It is used by both `CONFIG_CLK_R8A77960` and `CONFIG_CLK_R8A77961` match entries in `renesas-cpg-mssr.c`. Consumers include SDHI, PCIe, USB, display/video/capture, audio, Ethernet AVB, CAN, RPC, I2C, timers, GPIO, DMA, watchdog, and GIC blocks.

## Risks and Test Signals
Risks include forgetting that the module table is mutated for M3-W+, mismatching the M3-W/M3-W+ DT compatible, or changing PLL/SD/RPC parents copied from H3. Test both compatibles, confirm FCPCI0 is absent/null on M3-W+, validate clk summary rates, exercise SDHI/RPC/PCIe/USB/display/video/audio/Ethernet, and check RWDT/GIC critical clocks under unused-clock pruning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7796-cpg-mssr.c -->
