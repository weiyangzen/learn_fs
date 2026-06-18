# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vblank.h

Purpose: declares the vblank, scanline, timing, and evasion interfaces used by i915 display modeset and DRM vblank integration.

Important types and APIs: `struct intel_vblank_evade_ctx` stores the target CRTC, min/max unsafe scanline range, vblank start, and VLV/CHV DSI workaround flag. Timing helpers expose interlace-aware `intel_mode_vdisplay()`, `intel_mode_vblank_start()`, `intel_mode_vblank_end()`, `intel_mode_vtotal()`, and `intel_mode_vblank_delay()`. Runtime APIs include vblank counter readers, timestamp helper, scanline getter, scanline moving/stopped waits, active timing updates, scanline offset calculation, pre-commit state selection, and vblank length.

Control flow and integration: atomic commit code initializes and executes vblank evasion before sensitive register writes. DRM vblank core calls the counter and timestamp helpers. Modeset code updates active timings after mode or VRR state changes. Encoder-specific code can force scanline-counter flags that affect the implementation.

State and persistence: no direct state in the header, but it exposes operations that mutate CRTC timing state and depend on active hardware counters. The evasion context is short-lived per commit.

Risks and tests: callers must enable vblank interrupts before `intel_vblank_evade()`, as documented. Prototype or semantic changes can affect page flips, timestamping, VRR, and atomic update correctness. Test signals include build coverage for all users, vblank timestamp tests, VRR mode changes, atomic commit stress, and scanline wait behavior on enable/disable.
