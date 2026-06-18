# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_clocks.c

Purpose: reads, initializes, and controls legacy Radeon clock information, including PLL defaults, current engine/memory clocks, generic/Open Firmware fallbacks, legacy engine clock programming, and legacy clock gating.

Important APIs/functions: `radeon_legacy_get_engine_clock` and `radeon_legacy_get_memory_clock` compute current SCLK/MCLK from PLL registers. `radeon_get_clock_info` selects AtomBIOS, COMBIOS, Open Firmware, or generic fallback clock data and fills `rdev->clock` PLL ranges and `rdev->pm.current_*`. `radeon_legacy_set_engine_clock` programs the legacy SPLL for a requested engine clock via `calc_eng_mem_clock`. `radeon_legacy_set_clock_gating` toggles dynamic clocking/force-on bits across pre-AVIVO, R300, RS400/RS480, RV350+, and single-CRTC variants.

Control flow: clock info initialization first attempts firmware-specific clock discovery (`radeon_atom_get_clock_info` or `radeon_combios_get_clock_info`), then Open Firmware, then hard-coded generic defaults. It normalizes invalid reference dividers, sets PLL min/max/post-div constraints for pixel, display, system, and memory PLLs, and falls back to live register-derived clocks if default SCLK/MCLK are missing. Legacy engine-clock setting computes feedback/post dividers, switches to crystal input, sleeps/resets SPLL, programs feedback and gain, restarts PLL, selects post divider, and returns to normal clock input. Clock gating uses ASIC-family branches to clear or set force-on and dynamic-stop bits with required delays.

State and persistence: mutates `rdev->clock` PLL descriptors, default clocks, max pixel clock, display PLL data, and `rdev->pm.current_sclk/current_mclk`. Register programming changes hardware PLL and clock gating state. Open Firmware reads are transient. There is no filesystem persistence.

Dependencies and integration: uses DRM device-private Radeon state, AtomBIOS and COMBIOS clock readers, optional Open Firmware device tree properties, Radeon ASIC family predicates, low-level PLL/MMIO register macros, and PM hooks that later query or change clocks.

Risks: incorrect PLL divider calculations or reference frequencies can produce unstable clocks. Generic fallback values are approximate and may not match a board. Clock gating has many family/revision workarounds; changing force-on masks can cause hangs, especially around memory clocks and older VBIOS quirks. Busy delays make sequencing sensitive. Open Firmware property units are converted by division and assume expected firmware conventions.

Test signals: boot logs for firmware, OF, or generic clock source selection; validation of default/current SCLK/MCLK on legacy ASICs; modeset and PM transition tests after clock info initialization; stress tests with clock gating enabled/disabled; GPU hang monitoring after legacy engine clock changes; hardware register traces for family-specific gating paths.
