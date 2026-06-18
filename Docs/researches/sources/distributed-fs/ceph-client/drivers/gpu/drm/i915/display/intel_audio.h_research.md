# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_audio.h

## Purpose
`intel_audio.h` declares the public display-audio interface used by the i915 display modeset, CDCLK, and driver lifecycle code. It hides platform-specific audio register programming behind a small set of hooks implemented in `intel_audio.c`.

## Important APIs, Types, and Functions
The header forward-declares `intel_display`, `intel_encoder`, `intel_crtc_state`, and DRM connector state types. Exports include `intel_audio_hooks_init()`, `intel_audio_compute_config()`, codec enable/disable/get-config helpers, CDCLK pre/post hooks, `intel_audio_min_cdclk()`, and lifecycle functions `intel_audio_init()`, `intel_audio_register()`, and `intel_audio_deinit()`.

## Control Flow
Callers initialize hooks during display setup, compute audio state during atomic check, run enable/disable during modeset sequencing, query config during state readout, invoke CDCLK hooks around clock changes, and initialize/register/deinitialize the audio component during driver lifecycle.

## State and Persistence
The header owns no state. Its prototypes operate on `display`, `encoder`, connector state, and CRTC state objects whose audio fields are persisted by `intel_audio.c` in `display->audio` and `crtc_state->eld`.

## Dependencies and Integration Points
It includes only `linux/types.h` and uses forward declarations to avoid coupling users to audio internals. Integration points are i915 display init, atomic modeset, CDCLK management, and HDA/LPE audio registration.

## Risks
The API assumes callers use the functions at the correct modeset phase. Calling enable/disable out of order can violate hardware sequencing even though this header cannot express that contract. `intel_audio_min_cdclk()` must be included in CDCLK calculations whenever audio is active.

## Test Signals
Compile coverage catches signature drift. Runtime coverage comes from modeset tests with `has_audio`, CDCLK transition tests, and HDA/LPE bind/unbind tests that traverse the declared lifecycle API.
