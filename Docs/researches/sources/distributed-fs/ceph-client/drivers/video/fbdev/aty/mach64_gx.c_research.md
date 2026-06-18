# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_gx.c

## Purpose

`mach64_gx.c` implements DAC and external clock-chip support for older Mach64 GX/CX adapters. It provides `aty_dac_ops` and `aty_pll_ops` instances for IBM RGB514, ATI 68860-B, AT&T 21C498, ATI 18818/ICS2595, STG1703, Chrontel 8398, AT&T 20C408, and fallback unsupported devices.

## Important APIs, Types, and Functions

Important helper routines are `aty_dac_waste4()` for DAC counter synchronization, `aty_StrobeClock()` for clock-control strobing, `aty_st_514()` for indexed IBM RGB514 writes, and `aty_ICS2595_put1bit()` for serial clock programming. DAC callbacks include `aty_set_dac_514()`, `aty_set_dac_ATI68860_B()`, `aty_set_dac_ATT21C498()`, and `aty_set_dac_unsupported()`. PLL callbacks include `aty_var_to_pll_514()`, `aty_set_pll_514()`, `aty_var_to_pll_18818()`, `aty_set_pll18818()`, `aty_var_to_pll_1703()`, `aty_set_pll_1703()`, `aty_var_to_pll_8398()`, `aty_set_pll_8398()`, `aty_var_to_pll_408()`, and `aty_set_pll_408()`.

## Control Flow

The base driver selects one of these ops during GX initialization based on detected DAC and clock subtype. Mode validation calls the selected `var_to_pll` function, which converts a fbdev pixel-clock period into the target chip's encoded divider/programming word. For IBM RGB514 the code uses a fixed table of known modes. For ICS2595, STG1703, Chrontel 8398, and AT&T 20C408 it computes divider fields within chip-specific min/max frequency constraints. Mode setting then calls the DAC setter to configure pixel format and memory/DAC control bits, followed by the PLL setter to write the encoded clock word through DAC-indexed or serial control sequences.

Each DAC setter chooses register values based on bpp and sometimes acceleration mode or dot clock. The 68860 and unsupported paths write Mach64 `BUS_CNTL` and `DAC_CNTL` defaults. Clock setters temporarily force extended display enable where needed, program the external clock chip, clear DAC counters, and restore CRTC/display control state.

## State and Persistence Behavior

The file stores no long-lived software state beyond constants and callback tables. PLL choices are stored in `union aty_pll`, mainly `pll_514` or `pll_18818` fields, and then persisted in external DAC/clock hardware registers. `period_in_ps` is retained for many `pll_to_var` callbacks instead of recomputing from programmed bits, so reporting reflects requested timing rather than a full hardware readback.

## Dependencies and Integration Points

This file integrates with `atyfb_base.c` through `struct aty_dac_ops` and `struct aty_pll_ops`. It uses `struct atyfb_par` for MMIO bases, `clk_wr_offset`, reference clock period, VRAM size, and accessors. It depends heavily on `<video/mach64.h>` register and bit definitions and on delay helpers for hardware settle times.

## Risks and Edge Cases

Older DAC/clock programming is based on tables, approximations, and legacy magic values. Some callbacks clamp frequencies instead of failing, while others return `-EINVAL`; mode behavior differs by chip. Several `pll_to_var` callbacks simply return the requested period, not a calculated effective clock. Unsupported DAC/PLL ops are dummy or generic register writes, so display may be unreliable on unimplemented hardware. The serial ICS2595 programming sequence and DAC counter synchronization are timing-sensitive. Bpp handling varies by DAC, and 24/32-bpp modes share settings on some chips.

## Test Signals

Test with real or emulated GX/CX adapters using each supported DAC/clock combination where possible. Validate 8, 15, 16, 24, and 32 bpp mode set, accelerated versus unaccelerated DAC setup, pixel-clock boundary values, invalid high/low clocks, restoration of CRTC extended display state, and repeated mode switches. Static review should focus on integer divider search bounds and cases where frequency clamping may hide invalid modes.
