# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_crtc.c

## Purpose
This file implements legacy ATOMBIOS CRTC and PLL programming helpers for display modes. It translates DRM mode, connector, encoder, spread-spectrum, deep-color, and PLL state into versioned ATOM command-table parameter blocks executed through `amdgpu_atom_execute_table()`.

## Important APIs, types, and functions
Basic CRTC helpers are `amdgpu_atombios_crtc_overscan_setup()`, `amdgpu_atombios_crtc_scaler_setup()`, `amdgpu_atombios_crtc_lock()`, `amdgpu_atombios_crtc_enable()`, `amdgpu_atombios_crtc_blank()`, `amdgpu_atombios_crtc_powergate()`, `amdgpu_atombios_crtc_powergate_init()`, and `amdgpu_atombios_crtc_set_dtd_timing()`.

PLL and clock helpers include `amdgpu_atombios_crtc_program_ss()`, `amdgpu_atombios_crtc_adjust_pll()`, `amdgpu_atombios_crtc_set_disp_eng_pll()`, `amdgpu_atombios_crtc_set_dce_clock()`, `is_pixel_clock_source_from_pll()`, `amdgpu_atombios_crtc_program_pll()`, `amdgpu_atombios_crtc_prepare_pll()`, and `amdgpu_atombios_crtc_set_pll()`. Several unions wrap ATOM parameter revisions for spread spectrum, adjusted display PLL, set pixel clock, and set DCE clock.

## Control flow
The simple helpers zero a parameter structure, fill CRTC id or state fields, and execute a named command table. Overscan computes borders according to RMX center/aspect/full behavior. DTD timing converts DRM CRTC timing fields and sync flags into ATOM timing parameters.

PLL preparation sets default bpc and spread-spectrum state, reads monitor bpc and connector DP clock, selects spread-spectrum type by encoder mode, then calls `amdgpu_atombios_crtc_adjust_pll()`. The adjust path applies HDMI deep-color clock scaling, handles DVO/TV/LCD flags, calls versioned `AdjustDisplayPll`, and stores returned reference/post dividers in the CRTC. `amdgpu_atombios_crtc_set_pll()` computes PLL dividers, disables spread spectrum if needed, programs the versioned `SetPixelClock` table, computes SS amount/step, and re-enables spread spectrum.

## State and persistence behavior
The file mutates display hardware through ATOM command tables and updates software state in `amdgpu_crtc`: bpc, `ss_enabled`, spread-spectrum parameters, PLL flags/reference/post dividers, and adjusted clock. It also updates selected `adev->clock.ppll[]` fields before computing dividers. No standalone persistent storage is created.

## Dependencies
It depends on DRM CRTC/display mode types, AMDGPU CRTC/encoder/connector structures, ATOM interpreter APIs, ATOM command parameter definitions, connector helpers, encoder mode helpers, PLL compute code, and ATOMBIOS spread-spectrum helpers.

## Integration points
Legacy display modesetting calls these helpers when setting up scaler/overscan/timing, enabling or blanking CRTCs, power-gating display pipes, and programming display PLLs. DP helpers feed `dp_clock` into PLL adjustment. Encoder helpers provide encoder mode and transmitter identity.

## Risks and edge cases
Every command table has multiple firmware revisions; unsupported revisions only log and return, leaving hardware unchanged. HDMI deep-color clock conversion and ATOM v5/v6/v7 parameter semantics are easy to regress. Spread spectrum is skipped when another active CRTC shares the PLL, so PLL ownership tracking must be correct. Connector/private pointers are assumed present in several paths. Arithmetic uses kHz/10 kHz/100 Hz conversions that must match ATOM expectations. External spread-spectrum handling differs by PLL id and encoder mode.

## Test signals
Validation should cover all supported ATOM table revisions, HDMI 8/10/12/16 bpc clocks, DP/eDP/LVDS/DVI spread-spectrum selection, shared PLL disable-skip behavior, RMX overscan/scaler modes, invalid/missing command tables, and pixel-clock divider results compared against known BIOS traces.
