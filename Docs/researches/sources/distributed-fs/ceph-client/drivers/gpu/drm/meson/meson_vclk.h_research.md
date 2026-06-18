# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vclk.h

Purpose: Declares the Meson video-clock programming and validation API used by encoder code.

Important APIs, types, and functions: Defines target IDs `MESON_VCLK_TARGET_CVBS`, `MESON_VCLK_TARGET_HDMI`, and `MESON_VCLK_TARGET_DMT`, plus `MESON_VCLK_CVBS` as 27 MHz. Exports `meson_vclk_dmt_supported_freq()`, `meson_vclk_vic_supported_freq()`, and `meson_vclk_setup()`.

Control flow: HDMI mode validation calls the supported-frequency helpers before accepting modes. CVBS and HDMI atomic-enable paths call `meson_vclk_setup()` with a target and computed clock frequencies. The implementation chooses fixed CVBS, table-driven HDMI VIC, or generic DMT programming.

State and persistence: The header has no state. The implementation writes persistent HHI PLL/divider/gate state.

Dependencies and integration points: Includes `<drm/drm_modes.h>` for `enum drm_mode_status` and forward declares `struct meson_drm`. It is consumed by HDMI and CVBS encoders and potentially any future Meson encoder needing VCLK programming.

Risks: Callers must pass frequencies in Hz and a coherent set of PHY/VCLK/VENC/DAC values; wrong units or mismatched divisors can produce invalid clock programming. The `target` is an untyped unsigned int, so invalid values are only handled by falling into HDMI logic.

Test signals: Compile coverage for encoder callers and runtime validation that CVBS/HDMI modes call the expected target with accepted frequencies.
