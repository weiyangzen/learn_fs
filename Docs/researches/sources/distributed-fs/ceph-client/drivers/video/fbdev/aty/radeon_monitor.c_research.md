# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_monitor.c

## Purpose

`radeon_monitor.c` discovers attached Radeon displays, extracts flat-panel timing information, builds the primary head mode list, selects a default `fb_var_screeninfo`, and implements mode matching for `radeonfb_check_var()`. It bridges platform firmware, BIOS tables, EDID/DDC, manual `monitor_layout`, DAC load detection, and fbdev mode database helpers so `radeon_base.c` can program a valid CRTC/LVDS/TMDS mode.

## Important APIs, Types, And Functions

The file exports `radeon_probe_screens()`, `radeon_check_modes()`, and `radeon_match_mode()`. It maintains a default 640x480x8 `radeonfb_default_var`. Firmware helpers under PPC/SPARC include `radeon_parse_montype_prop()` and `radeon_probe_OF_head()`, which inspect OF `display-type` and EDID properties. BIOS helpers include `radeon_get_panel_info_BIOS()` for LVDS timing and divider tables and `radeon_parse_connector_info()` for debug connector table decoding. Hardware probing includes `radeon_crt_is_connected()`, which temporarily changes DAC/VCLK/CRTC registers to use the DAC comparator for load detection.

Mode-selection helpers are `radeon_parse_monitor_layout()`, `radeon_fixup_panel_info()`, `radeon_var_to_panel_info()`, `radeon_videomode_to_var()`, optional pSeries `is_powerblade()`, `radeon_compare_modes()`, and `radeon_match_mode()`.

## Control Flow

`radeon_probe_screens()` first parses connector info for diagnostics. If `monitor_layout` is supplied, it maps strings `CRT`, `TMDS`, and `LVDS` to monitor types and optionally probes EDID without changing the requested layout. If the first monitor is absent, it promotes monitor 2 or assumes CRT. Without a manual layout, the function auto-detects. Single-head cards try OF, then DVI/VGA/CRT2 DDC, then assume CRT. Dual-head cards first inspect BIOS connector data to detect reversed DAC or TMDS wiring, then probe head 1 via OF, DVI DDC, CRT2 DDC, mobility LVDS scratch/register hints, and CRT DAC load. Head 2 is probed via OF, VGA DDC, CRT2 DDC if unused, and the opposite DAC load path. If only head 2 is found, it is promoted to head 1. Reversed TMDS handling swaps monitor state to keep internal TMDS primary. If `ignore_edid` is set, EDID buffers are freed after type detection.

`radeon_check_modes()` initializes `info->var` and `info->modelist`, then for LCD primary displays tries BIOS panel info first. If BIOS dividers are not locked and EDID exists, it parses EDID detailed timing into panel info when it is at least as large as current panel dimensions. PPC may force firmware PLL dividers for mobility LCD panels. With valid panel info, it constructs a default native panel mode. It then converts EDID monspecs to a modelist and stores `rinfo->mon1_modedb`. If panel info is still missing, it guesses panel size from `FP_HORZ_STRETCH` and `FP_VERT_STRETCH`, tries to find a matching mode, or falls back to CRT behavior. User `mode_option`, pSeries hardcoded fallback, and EDID preferred timing are applied before the chosen mode is added to `info->modelist`.

`radeon_match_mode()` copies the requested var, selects EDID modedb or built-in VESA modes, validates direct TEST/NOW requests, and for FIND-style activation chooses the closest mode that is at least as large. Flat-panel scalers allow fallback from native EDID modes to VESA modes and may accept unmatched modes for RMX scaling; CRTs reject unmatched modes.

## State And Persistence

The file mutates monitor and mode fields in `struct radeonfb_info`: `mon1_type`, `mon2_type`, `mon1_EDID`, `mon2_EDID`, `mon1_modedb`, `mon1_dbsize`, `reversed_DAC`, `reversed_TMDS`, and `panel_info`. It also fills `fb_info->var`, `fb_info->monspecs`, and `fb_info->modelist`. EDID buffers are allocated by OF duplication or I2C DDC and later owned by the base driver. Panel info is volatile runtime state reconstructed at probe; no persistent configuration is written.

## Dependencies And Integration Points

The file depends on `radeonfb.h`, fbdev EDID/mode helpers, optional OF APIs, optional Radeon I2C probing, and Radeon register definitions. `radeon_base.c` calls it during PCI probe before saving mode state and registering the framebuffer. `radeonfb_set_par()` later consumes `panel_info`, monitor types, reversed output hints, and mode lists to compute CRTC/flat-panel registers.

## Risks

Detection is heuristic-heavy. OF can label DFP as LCD, BIOS connector tables are parsed mostly for hints, and DDC can be absent or routed through alternate GPIOs. Manual `monitor_layout` parsing uses fixed four-character buffers, truncating longer tokens. DAC load detection temporarily rewrites display and clock registers; missed restoration would affect active output. BIOS panel parsing trusts offsets under `fp_bios_start` and only bounds the power delay. `radeon_match_mode()` intentionally accepts some RMX modes without strict validation, which can permit timings that user space requested but hardware or panel scaling handles poorly. `ignore_edid` frees EDID and loses mode database quality.

## Test Signals

Good signals include monitor detection logs for single and dual head cards, reversed DAC/TMDS cases, manual `monitor_layout` combinations, `ignore_edid`, DDC-present and DDC-absent panels, mobility non-DDC LVDS detection, BIOS panel timing extraction, EDID preferred timing selection, pSeries fallback, `fb_find_mode()` with `mode_option`, and `fbset` requests using `FB_ACTIVATE_TEST`, `NOW`, and `FIND`. Regression testing should verify that `info->modelist` is never empty after probe and that EDID allocations are freed on remove.
