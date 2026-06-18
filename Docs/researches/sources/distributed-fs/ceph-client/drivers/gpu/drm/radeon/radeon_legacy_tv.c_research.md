<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_tv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_tv.c

## Purpose

`radeon_legacy_tv.c` programs the integrated legacy TV-out block. It contains NTSC/PAL timing constants, TV PLL settings, horizontal/vertical code timing tables, restart/position/size calculations, FIFO writes for timing microcode, full TV mode programming, and helper hooks that let legacy CRTC PLL/timing setup use TV-specific values.

## Important APIs, Types, and Functions

- `struct radeon_tv_mode_constants`: captures per-standard/per-reference-clock CRTC and TV timing values.
- `available_tv_modes[]`, `hor_timing_NTSC/PAL[]`, and `vert_timing_NTSC/PAL[]`: hard-coded timing presets for 800x600 TV output.
- `radeon_legacy_tv_get_std_mode()`: selects NTSC/PAL and 27 MHz/14 MHz constants based on TV standard and active CRTC PLL reference.
- `radeon_wait_pll_lock()`: polls PLL test counters after TV PLL programming.
- `radeon_legacy_tv_write_fifo()`, `radeon_get_htiming_tables_addr()`, `radeon_get_vtiming_tables_addr()`, and `radeon_restore_tv_timing_tables()`: write horizontal/vertical TV timing code tables into the hardware FIFO.
- `radeon_legacy_tv_init_restarts()` and `radeon_legacy_write_tv_restarts()`: compute and program frame/vertical/horizontal restart positions from user TV position/size controls.
- `radeon_legacy_tv_mode_set()`: full TV block programming sequence, including master control, DAC, TV PLL, scaler/filter/modulator registers, timing tables, restart registers, and gain settings.
- `radeon_legacy_tv_adjust_crtc_reg()`, `radeon_legacy_tv_adjust_pll1()`, and `radeon_legacy_tv_adjust_pll2()`: adjust CRTC timing and PLL parameters for TV output.

## Control Flow

TV mode setting starts by selecting a standard mode based on the encoder's `tv_std` and active CRTC PLL reference. It computes master control, modulator levels, RGB source selection, vertical scaler increments, flicker-removal filter parameters, TV timing control, DAC standard/adjustment bits, and TV PLL dividers. It copies standard timing code arrays into the encoder's persistent `tv` cache, computes restart values and horizontal-size increments, then programs hardware in a reset-oriented sequence: assert TV/CRT/FIFO resets, power down DAC blanking, program and lock TV PLL, program HV/scaler/filter registers, write restarts, restore timing tables via FIFO, program standard/modulator/pre-DAC/gain registers, and finally enable the TV master/DAC.

The CRTC helpers are called from `radeon_legacy_crtc.c` when a CRTC is driving TV output. They override horizontal/vertical CRTC totals and sync starts to match the selected TV mode, and they replace PPLL/P2PLL divider values and pixel-clock source bits with the TV-specific values.

## State and Persistence Behavior

Persistent per-encoder TV state lives in `struct radeon_encoder_tv_dac`: selected standard, supported standards, user h/v position and h size, adjustment values, and cached `struct radeon_tv_regs` timing/restart tables. Hardware state persists in TV master, PLL, scaler, DAC, modulator, FIFO timing, restart, and gain registers until another TV modeset or suspend/resume restore.

## Dependencies and Integration Points

This file depends on Radeon register macros, `struct radeon_encoder_tv_dac` and TV standard enums from `radeon_mode.h`, active CRTC state, legacy encoder TV DAC setup, and legacy CRTC timing/PLL programming. It is invoked only through the legacy TV DAC path in `radeon_legacy_encoders.c` and the TV adjustment hooks in `radeon_legacy_crtc.c`.

## Risks and Edge Cases

- Timing tables and magic constants are hardware-specific; small arithmetic or table changes can break analog TV output.
- FIFO write acknowledgement loops have finite counters but no explicit failure reporting, so programming failure can be silent.
- `radeon_legacy_tv_init_restarts()` uses signed arithmetic and casts back to unsigned fields; extreme position/size values need clamping by callers/properties.
- `SLOPE_limit` lookup assumes flicker-removal values fall within the table; if not, index `i` can reach `ARRAY_SIZE(SLOPE_limit)` and then index adjacent arrays out of bounds.
- Only a small fixed mode set is represented here, centered on 800x600 constants.
- TV PLL lock polling is heuristic and may be sensitive to reference-clock or silicon differences.

## Test Signals

Hardware validation should cover NTSC, NTSC-J, PAL, PAL-M, PAL-60, SCART PAL where supported, both 27 MHz and 14 MHz references, CRTC0 and CRTC1 TV routing, h/v position and h-size property changes, composite and S-video outputs, suspend/resume, repeated modesets, PLL lock stability, and visual timing checks for overscan/flicker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_tv.c -->
