
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen3-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen3-cpg.c

## Purpose
Implements R-Car Gen3 custom CPG clock registration for CPG-MSSR. It covers configurable PLL0/PLL2 clocks for CPU boost modes, adjustable Z/ZG clocks, SD/SDH and RPC helper integration, mode-pin and RCKCR-selected clocks, RCLK quirks, and fixed-factor PLL/core clocks.

## Important APIs, Types, And Functions
- `rcar_gen3_cpg_init()` stores PLL config, EXTALR clock index, mode pins, and SoC quirks.
- `rcar_gen3_cpg_clk_register()` maps `enum rcar_gen3_clk_types` to custom or fixed-factor CCF clocks.
- `struct cpg_pll_clk` and `cpg_pll_clk_ops` read/write PLL control registers and wait for PLLECR status.
- `struct cpg_z_clk` and `cpg_z_clk_ops` implement Z/Z2/ZG rate control through FRQCRC/FRQCRB fields and KICK polling.
- Uses shared helpers `cpg_sdh_clk_register()`, `cpg_sd_clk_register()`, `cpg_rpc_clk_register()`, `cpg_rpcd2_clk_register()`, and `cpg_reg_modify()`.

## Control Flow
SoC-specific Gen3 code calls `rcar_gen3_cpg_init()`. During CPG registration, each custom descriptor enters `rcar_gen3_cpg_clk_register()`, which resolves a parent, checks clock type, and returns a PLL, Z/ZG, helper-registered SD/RPC, or fixed-factor clock. RCLK may choose EXTALR based on mode pin MD28 or an R8A7796 ES1.0 quirk that writes RCKCR manually and registers a suspend/resume notifier. Mode-select clocks decode two parent/divider pairs packed into descriptor fields.

## State And Persistence
Static initdata holds PLL config, EXTALR index, mode pins, and quirks. Hardware state includes PLLECR/PLLxCR, FRQCRB/FRQCRC, RPCCKCR, RCKCR, and SDnCKCR registers. Z clocks cache `max_rate` at registration. Shared simple notifiers save RCKCR/SD/RPC registers across suspend/resume.

## Dependencies And Integration Points
Depends on `renesas-cpg-mssr.h`, `rcar-cpg-lib.h`, and `rcar-gen3-cpg.h`. Integrates with Linux CCF, PM notifier chains, SoC revision detection through `soc_device_match()`, cpufreq-style PLL/Z rate changes, SDHI, RPC, and RCLK external oscillator handling.

## Risks And Edge Cases
Config must be initialized before registration. PLL set-rate waits for status but does not explicitly set a kick bit, matching Gen3 hardware semantics. Z clock rate logic changes parent rate for boost modes and can return `-EBUSY`/`-ETIMEDOUT`. Packed high bits in `core->parent` and `core->div` are type-specific; wrong macros corrupt parent selection. R8A7796 ES1.0 RCKCR quirk writes hardware based on whether EXTALR has a nonzero rate.

## Test Signals
Build Gen3 SoC users and boot boards across normal and quirked revisions. Exercise cpufreq/boost transitions for PLL0/PLL2 and Z clocks, SDHI and RPC clocks, suspend/resume with RCKCR/SD/RPC state restoration, RCLK parent selection with and without EXTALR, and mode-pin-derived clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen3-cpg.c -->
