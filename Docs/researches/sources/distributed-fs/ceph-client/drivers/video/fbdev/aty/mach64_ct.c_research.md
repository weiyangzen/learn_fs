# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_ct.c

## Purpose

`mach64_ct.c` supplies PLL, clock, and DSP FIFO programming for integrated Mach64 CT/VT/GT/LT-family chips. It implements the `aty_pll_ops` and `aty_dac_ops` entries used by `atyfb_base.c` when `M64F_INTEGRATED` devices are detected.

## Important APIs, Types, and Functions

The external register helpers are `aty_ld_pll_ct()` and the internal `aty_st_pll_ct()`. The main PLL callbacks are `aty_var_to_pll_ct()`, `aty_pll_to_var_ct()`, `aty_set_pll_ct()`, `aty_get_pll_ct()`, `aty_init_pll_ct()`, and `aty_resume_pll_ct()`, collected in `aty_pll_ct`. `aty_dac_ct` is a dummy DAC op because integrated CT-family output setup is mostly handled elsewhere. `aty_dsp_gt()` calculates `DSP_CONFIG` and `DSP_ON_OFF` for GTB-DSP chips, while `aty_valid_pll_ct()` validates and derives VCLK feedback/post-dividers. `aty_postdividers[]` maps encoded post-divider values to real divisors.

## Control Flow

Mode validation calls `aty_var_to_pll_ct()`, which derives a VCLK divider set from the requested pixel-clock period and, for GTB-DSP chips, computes FIFO thresholds using memory clock, pixel clock, bpp, RAM type, FIFO size, and optional LCD scaling state. `aty_pll_to_var_ct()` converts the chosen PLL fields back into a fbdev pixel-clock period.

`aty_set_pll_ct()` temporarily disables LCD output when required, strobes the selected clock, enables accelerator display if needed, resets VCLK, writes post-divider, extended divider, feedback divider, PLL general control, and VCLK control registers, waits for lock, restores display mode, then programs DLL and DSP registers for GTB-DSP chips. `aty_get_pll_ct()` snapshots current PLL registers for restore. `aty_init_pll_ct()` derives base memory-clock and FIFO timing state from current PLL and `MEM_CNTL`, applies RAM-type latency rules, honors BIOS DSP loop latency when present, and either leaves existing memory clocks alone or computes new MCLK/XCLK/SCLK values from driver limits. `aty_resume_pll_ct()` restores reference, general, memory, extended, and optional SCLK state in the required order.

## State and Persistence Behavior

All durable driver state is stored in `par->pll.ct` and `par->pll_limits`. `aty_init_pll_ct()` populates fields such as `pll_ref_div`, `mclk_fb_div`, post-dividers, FIFO size, loop latency, XCLK delays, and feature flags. `aty_set_pll_ct()` persists mode state in hardware PLL/DSP registers until the next mode set, suspend/resume, or driver removal. There is no disk persistence, but bad PLL programming can leave display hardware unusable until reset or restore.

## Dependencies and Integration Points

The file depends on `atyfb_base.c` for chip feature flags, memory type, LCD dimensions, and clock limits. It writes Mach64 PLL registers through indexed `CLOCK_CNTL_ADDR/DATA` and normal MMIO for DSP registers. LCD support uses `aty_ld_lcd()` and `aty_st_lcd()` from the base file. PowerMac-specific clock handling checks `machine_is(powermac)`.

## Risks and Edge Cases

Clock arithmetic uses integer periods and dividers with tight range checks. Out-of-range pixel, memory, or chip clocks return `-EINVAL`, which rejects mode setting. FIFO/DSP calculations are sensitive to RAM type, FIFO size, LCD scaling, and bpp; mistakes can produce underflow or display corruption. The code carries comments about SCLK ordering because disabling SCLK before it is used can crash systems. The `pll->ct.xres` LCD scaling adjustment must be reset by the caller's pixel-clock path. Some paths preserve existing memory clocks when `par->mclk_per == 0`, making behavior depend on firmware initialization.

## Test Signals

Coverage should include CT, VT, GT, LT, XL, and Mobility variants; GTB-DSP and non-DSP chips; DRAM, EDO, SDRAM, SGRAM, WRAM, and SDRAM32 memory types; default and user-overridden `pll`, `mclk`, and `xclk`; 14.31818 MHz and 29.498928 MHz reference clocks; LCD scaling mode changes; suspend/resume restore; and invalid pixel-clock requests. Hardware validation should watch for FIFO underruns, PLL lock delays, and display corruption during rapid mode changes.
