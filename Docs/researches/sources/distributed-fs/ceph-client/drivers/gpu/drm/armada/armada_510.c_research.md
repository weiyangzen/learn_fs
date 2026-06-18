# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_510.c

## Purpose

`armada_510.c` implements Armada 510/Dove variant-specific CRTC support. It discovers variant clocks, initializes SPU hardware defaults, selects a pixel clock source/divider, and provides enable/disable hooks for the generic Armada CRTC code.

## Important APIs, Types, And Functions

The exported object is `armada510_ops`, a `struct armada_variant`. Private state is `struct armada510_variant_data`, storing up to four clocks and the selected clock. Important functions are `armada510_crtc_init()`, `armada510_crtc_compute_clock()`, `armada510_crtc_disable()`, and `armada510_crtc_enable()`. `armada510_clocking` defines HDMI clock tolerance and divider limits.

## Control Flow

CRTC creation calls `init()`, which allocates variant state, obtains clocks by DT `clock-names` or a legacy `ext_ref_clk1`, lowers the DMA watermark, disables SRAM wait state, and initializes the SPU advanced hardware cursor/blend register. Mode fixup calls `compute_clock()` with `sclk == NULL` to validate support. Mode setting calls it again with an output pointer, which enables a candidate clock, optionally sets rate and SCLK selector/divider, stores the selected clock, swaps the active CRTC clock, and disables the temporary reference. Enable prepares the selected clock if not already active; disable unprepares the active clock.

## State And Persistence Behavior

`variant_data` persists per CRTC and stores discovered clocks plus `sel_clk`. `dcrtc->clk` tracks the currently prepared clock. SPU register initialization persists until later register writes or reset. The selected SCLK register value is queued by generic mode-setting code and written to hardware.

## Dependencies And Integration Points

The file depends on Linux clk and OF helpers, Armada CRTC/private/hardware headers, and generic `armada_crtc_select_clock()`. It is referenced by the LCD platform match table for `marvell,dove-lcd` and platform IDs.

## Risks And Edge Cases

Clock discovery returns `-EPROBE_DEFER` for missing named clocks. `strnstr` is not involved here; matching is by exact clock-name strings. `clk_prepare_enable()` is used during clock computation and must be balanced. The compute function assumes setting the selected clock in the second call cannot fail in a way not seen during validation. The SRAM wait-state/watermark workaround is variant-specific and could affect bandwidth stability.

## Test Signals

Tests should cover DT clock-name permutations, legacy non-DT clock path, mode validation around HDMI tolerance limits, SCLK selector programming for each source, clock enable/disable across modesets and DPMS, high-bandwidth jitter regressions, and probe deferral when clocks are unavailable.
