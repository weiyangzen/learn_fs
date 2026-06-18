# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pfit.c

Purpose: computes, validates, programs, disables, and reads back panel fitter/scaler state for GMCH-era and PCH/CPU panel fitters.

Important functions: `intel_pfit_compute_config()`, `intel_pfit_mode_valid()`, `ilk_pfit_enable()/disable()/get_config()`, `i9xx_pfit_enable()/disable()/get_config()`. Helpers compute PCH destination windows, source-size/scaling/timing/cloning validity, GMCH centering/aspect/fullscreen scaling, programmed ratios, and legacy timing limits.

Control flow: `intel_pfit_compute_config()` dispatches to GMCH or PCH. PCH fitting compares pipe source to fixed adjusted mode, computes destination window from connector scaling mode, sets `crtc_state->pch_pfit`, and for pre-SKL validates centered window, source size, max downscaling, timings, and no cloning. GMCH fitting modifies adjusted CRTC timings for centered/aspect modes where needed, computes PFIT control/ratio/border bits, rejects unsupported downscaling, and stores `gmch_pfit` fields. Enable paths program PF/PFIT registers only when state says fitting is enabled; disable paths clear them with required pipe-disabled assertions for GMCH.

State and persistence: mutates `intel_crtc_state` fields `pch_pfit` and `gmch_pfit`, sometimes modifies adjusted mode timings, and writes PFIT/PF window/control/ratio/border registers during enable/disable. Readout populates those fields from hardware registers.

Dependencies/integration: uses connector scaling mode, DRM rect/mode helpers, display version/platform checks, LVDS border registers, PCH/CPU pfit registers, SKL scaler mode validation, and transcoder-disabled asserts.

Risks/test signals: risks include off-by-one centering, interlace alignment, downscale limits, cloning rejection, DISPLAY_VER-specific max source sizes, IVB/HSW pipe selection readout, and modifying adjusted mode for GMCH. Test all scaling modes, native/no-fit, aspect pillar/letter, centered modes, YCbCr420 pfit use, interlaced modes, cloned outputs, pre-965/965+/ILK/IVB/HSW/SKL+ platforms, and pfit readout after BIOS-enabled panels.
