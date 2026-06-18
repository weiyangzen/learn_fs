
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen2-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen2-cpg.c

## Purpose
Implements R-Car Gen2 custom CPG clock registration for `renesas-cpg-mssr`. It handles mode-pin-derived fixed factors, PLL configuration, an adjustable CPU Z clock, ADSP/RCAN composite clocks, and SDHI divider quirks.

## Important APIs, Types, And Functions
- `rcar_gen2_cpg_init()` stores the SoC PLL config, PLL0 divider, mode pins, and SoC quirks.
- `rcar_gen2_cpg_clk_register()` is the backend callback that maps `enum rcar_gen2_clk_types` to CCF clocks.
- `struct cpg_z_clk` plus `cpg_z_clk_ops` implements adjustable Z rate with FRQCRC fields and FRQCRB KICK polling.
- `cpg_rcan_clk_register()` creates a divide-by-6 plus gate composite clock.
- `cpg_adsp_clk_register()` creates a divider-table plus gate composite clock.
- SDH/SD divider tables model Gen2 SDHI register encodings, with an `SD_SKIP_FIRST` quirk for `r8a77470`.

## Control Flow
SoC-specific Gen2 code calls `rcar_gen2_cpg_init()` before the CPG-MSSR core registers clocks. For each custom core clock, the backend calls `rcar_gen2_cpg_clk_register()`, which resolves the parent from `pub->clks`, checks the clock type, and either returns a fixed-factor clock, a custom Z clock, a composite ADSP/RCAN clock, or an SD divider-table clock. Z rate changes write FRQCRC, set FRQCRB KICK, and spin until hardware clears KICK or times out.

## State And Persistence
Static initdata stores PLL config, PLL0 divider, mode pins, and quirk bits. Hardware state is in FRQCRB, FRQCRC, SDCKCR, PLL0CR, ADSPCKCR, and RCANCKCR. `cpg_lock` serializes composite gate/divider and SD divider accesses. No persistent software state survives beyond registered CCF objects.

## Dependencies And Integration Points
Depends on `renesas-cpg-mssr.h` for core descriptor types and `rcar-gen2-cpg.h` for enum/config definitions. It integrates with SoC files that define `cpg_core_clk` descriptors and call `rcar_gen2_cpg_init()`. It uses `soc_device_match()` for quirks and Linux CCF fixed-factor, divider, gate, composite, and custom `clk_hw` APIs.

## Risks And Edge Cases
The code assumes `rcar_gen2_cpg_init()` ran before registration; otherwise config pointers are invalid. PLL0 may be fixed from config or read from PLL0CR, so wrong `pll0_mult` use can misclock CPUs. Z clock KICK polling can return `-EBUSY` or `-ETIMEDOUT`. SD divider quirks are SoC revision specific. `cpg_z_clk_set_rate()` uses integer truncation and clamps multipliers to 1..32.

## Test Signals
Compile Gen2 SoC CPG drivers and boot representative Gen2 boards. Check CPU Z clock cpufreq/rate changes, SDHI rates especially on `r8a77470`, ADSP and RCAN gates, PLL-derived fixed rates from mode pins, and timeout-free KICK completion under rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen2-cpg.c -->
