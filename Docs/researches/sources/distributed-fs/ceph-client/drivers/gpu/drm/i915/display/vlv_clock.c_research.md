# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_clock.c

Purpose: provides Valleyview/Cherryview-style clock read helpers for HPLL VCO, hrawclk, czclk, cdclk, and GPLL reference clocks. The helpers read CCK sideband registers, convert hardware divider values to kHz, and cache selected stable frequencies in `intel_display`.

Important APIs/types/functions: exported functions are `vlv_clock_get_hpll_vco()`, `vlv_clock_get_hrawclk()`, `vlv_clock_get_czclk()`, `vlv_clock_get_cdclk()`, and `vlv_clock_get_gpll()`. The local helper `vlv_clock_get_cck()` performs common sideband read, divider extraction, in-progress warning, and frequency calculation. It uses `display->vlv_clock.hpll_freq` and `display->vlv_clock.czclk_freq` as caches.

Control flow: `vlv_clock_get_hpll_vco()` lazily reads `CCK_FUSE_REG`, indexes the VCO table `{800, 1600, 2000, 2400}` MHz, stores kHz in the display cache, and logs it. `vlv_clock_get_cck()` acquires CCK access, reads the requested register, releases access, warns if frequency status does not match the divider, and returns `DIV_ROUND_CLOSEST(ref_freq << 1, divider + 1)`. hrawclk, cdclk, and GPLL calls pass the appropriate CCK register and reference frequency; czclk is lazily cached after first read.

State and persistence behavior: HPLL and CZ clock values persist in `display->vlv_clock` once read. The file explicitly notes that this lazy caching is fragile because the first call must happen when the registers are readable; a future explicit initialization point would be safer. hrawclk, cdclk, and GPLL are read live each call.

Dependencies and integration points: depends on DRM logging, `intel_display_core.h`, `intel_display_types.h`, `vlv_sideband.h`, and the CCK sideband access helpers `vlv_cck_get()`, `vlv_cck_read()`, and `vlv_cck_put()`. These helpers feed display clock setup/readout paths for older VLV/CHV platforms.

Risks: wrong timing of the first lazy cached read can permanently cache zero or stale frequencies. Divider status mismatches mean a frequency change is in progress and the returned value may be transient. The HPLL table assumes fuse encoding stays in range. Callers on non-VLV platforms should rely on header stubs or avoid these functions.

Test signals: VLV/CHV boot logs for HPLL/CZ values, sideband read failure instrumentation, status-mismatch warning paths during clock changes, repeated calls proving cache stability, and comparing computed clock rates with BIOS/kernel display clock readouts.
