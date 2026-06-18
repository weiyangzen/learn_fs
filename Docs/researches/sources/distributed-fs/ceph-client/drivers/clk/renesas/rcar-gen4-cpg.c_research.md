
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen4-cpg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen4-cpg.c

## Purpose
Implements R-Car Gen4 custom CPG clock registration for CPG-MSSR. It extends Gen3 patterns with Gen4 register offsets, fractional 8.25 and 9.24 PLL handling, Gen4 Z clock register selection, SD/RPC helper integration, SDSRC decoding, and mode-pin/oscillator fixed-factor clocks.

## Important APIs, Types, And Functions
- `rcar_gen4_cpg_init()` stores Gen4 PLL config, EXTALR index, and mode pins.
- `rcar_gen4_cpg_clk_register()` dispatches `enum rcar_gen4_clk_types` to fixed-factor, PLL, Z, SD/RPC, SDSRC, MDSEL, or OSC registration.
- `struct cpg_pll_clk` plus `cpg_pll_f8_25_clk_ops`, `cpg_pll_v8_25_clk_ops`, and `cpg_pll_f9_24_clk_ops` implement fractional PLL rate calculation and selected variable set-rate support.
- `struct cpg_z_clk` and `cpg_z_clk_ops` implement Z0/Z1/ZG rate control across FRQCRC0, FRQCRC1, and FRQCRB fields.
- Uses shared helpers `cpg_reg_modify()`, `cpg_sdh_clk_register()`, `cpg_sd_clk_register()`, `cpg_rpc_clk_register()`, and `cpg_rpcd2_clk_register()`.

## Control Flow
Gen4 SoC code calls `rcar_gen4_cpg_init()` and CPG-MSSR invokes `rcar_gen4_cpg_clk_register()` for custom clocks. Fixed PLL types use config multipliers/dividers or read `CPG_PLLxCR_STC`. Fractional PLLs register custom CCF clocks with recalc-only or recalc/determine/set ops. Variable 8.25 set-rate writes NI/NF fields, sets `CPG_PLLxCR0_KICK`, and polls PLLECR status. Z clocks select the correct FRQCR register based on packed offset and poll FRQCRB KICK after changes.

## State And Persistence
Static initdata stores the Gen4 config/mode. Hardware state is in PLLECR, PLLxCR0/CR1, FRQCRB/FRQCRC0/FRQCRC1, SD0CKCR1, RPCCKCR, SD registers, and mode-pin-dependent state. Z clocks cache `max_rate`. Shared notifiers from `rcar-cpg-lib` persist selected SD/RPC registers across suspend/resume.

## Dependencies And Integration Points
Depends on `renesas-cpg-mssr.h`, `rcar-gen4-cpg.h`, and `rcar-cpg-lib.h`. Integrates with Gen4 SoC descriptor files, cpufreq/boost paths, SDHI, RPC, CANFD/MSIOF/CSI/DSI external-clock register offsets exposed by the header, and Linux CCF fractional-rate APIs.

## Risks And Edge Cases
Variable fractional 9.24 PLL is explicitly not supported and falls through to fixed 9.24 behavior. Fractional rate math must avoid overflow and must match hardware NI/NF interpretation. `readl_poll_timeout()` waits on PLLECR status after KICK; wrong PLL index mapping in `CPG_PLLECR_PLLST()` will cause false timeouts. Z offsets outside 0..95 return `-EINVAL`. The `cpg_clk_extalr` init value is stored but not currently used in this implementation.

## Test Signals
Build Gen4 SoC users. On target boards, test PLL recalc against measured rates, variable 8.25 rate changes, Z clock rate changes and KICK timeout handling, SDHI/RPC clocks and suspend/resume, SDSRC-derived rates, and mode-pin-selected clocks. Confirm unsupported variable 9.24 users do not expect set-rate support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-gen4-cpg.c -->
