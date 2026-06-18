# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_audio.c

## Purpose
`intel_audio.c` implements the display side of HDMI/DP high-definition audio for i915. It participates in modeset sequencing by programming codec-facing audio registers after the transcoder/link is active and before the transcoder/port is disabled, keeps ELD state for the HDA/LPE audio drivers, and exposes the i915 audio component ops consumed by `snd_hda_intel`.

## Important APIs, Types, and Functions
- `struct intel_audio_funcs` is the platform dispatch table for codec enable, disable, and state readout.
- `intel_audio_compute_config()` copies connector ELD into `crtc_state->eld`, validates that ELD exists, and writes AV sync delay into the ELD payload.
- `intel_audio_codec_enable()` and `intel_audio_codec_disable()` are the public modeset hooks. They call platform-specific register programming, update `display->audio.state[cpu_transcoder]`, notify HDA through `pin_eld_notify`, and notify LPE audio.
- `g4x_*`, `ibx_*`, and `hsw_*` paths cover G4X, PCH/VLV/CPT/IBX, and HSW+ register models.
- `hsw_audio_config_update()`, `hsw_hdmi_audio_config_update()`, and `hsw_dp_audio_config_update()` program N/CTS handling and timestamp behavior. HDMI may use fixed N values from HDMI tables keyed by sample rate, port clock, and pipe bpp.
- `intel_audio_cdclk_change_pre/post()` handles display version 13+ audio timestamp CDCLK M/N programming around CDCLK changes.
- Component ops include `get_power`, `put_power`, `codec_wake_override`, `get_cdclk_freq`, `sync_audio_rate`, and `get_eld`.

## Control Flow
Hook setup starts in `intel_audio_hooks_init()`, selecting G4X, IBX/PCH/VLV, or HSW functions based on platform. During atomic check, `intel_audio_compute_config()` snapshots ELD into the CRTC state. During enable, the selected backend programs ELD valid/output-enable/timestamp registers, then common code records `encoder` and ELD in `display->audio.state`, calls HDA `pin_eld_notify`, and calls LPE notification. Disable runs in the reverse modeset phase, invalidates ELD/presence, waits vblanks where required, clears state, and notifies audio consumers that ELD is gone.

HDA component binding is separate: `intel_audio_init()` chooses LPE or component mode, `intel_audio_register()` registers an audio component if LPE is absent, and component bind/unbind installs or removes the ops pointer under modeset locks.

## State and Persistence
Persistent driver state lives in `display->audio`: the per-transcoder `intel_audio_state` with active encoder and ELD bytes, `component`, `component_registered`, `freq_cntrl`, and `power_refcount`. `display->audio.mutex` protects shared ELD/audio state. Hardware-visible state is in audio registers, ELD valid bits, output enable bits, N/CTS controls, SDP split controls, and CDCLK timestamp registers. No disk persistence exists.

## Dependencies and Integration Points
This file integrates DRM ELD helpers, i915 atomic/modeset state, display register helpers (`intel_de_read/write/rmw`), CDCLK global state, display workarounds, LPE audio, Linux component framework, and `drm_audio_component_ops`. It depends on `intel_audio_regs.h` for register fields and on display platform predicates such as `DISPLAY_VER()`, `HAS_DDI()`, `HAS_DP20()`, and PCH/platform checks.

## Risks
Ordering is critical: enable must happen after link training/transcoder enable, and disable must happen before disabling the port/transcoder. Incorrect ELD state or missing notification can leave HDA with stale sink capabilities. N/CTS programming depends on the HDA-reported sample rate; absent or unmatched rates fall back to automatic N. Workarounds such as DSC hblank programming and min-hblank chicken bits are platform-specific and can cause regressions if applied too broadly. Power refcount mismatches during component unbind are explicitly logged.

## Test Signals
Useful signals include KMS debug messages for ELD size, N/CTS choice, pixel clock fallback, audio component bind failures, CDCLK M/N values, and invalid port/transcoder lookups. Exercise HDMI and DP audio across modesets, MST/non-MST, suspend/resume, CDCLK changes, LPE versus HDA component paths, high link-rate DP with audio CDCLK restrictions, and DSC 4K+ DP cases.
