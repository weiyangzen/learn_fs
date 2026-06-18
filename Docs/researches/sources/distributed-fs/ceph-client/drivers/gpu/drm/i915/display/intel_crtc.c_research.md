# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc.c

## Purpose
Implements i915 CRTC allocation, initialization, vblank handling, pipe update timing, event delivery, pipe lookup, bandwidth helpers, and CRTC state reset. It is the bridge between DRM CRTC core callbacks and generation-specific i915 display hardware.

## Important APIs and functions
Public APIs include `intel_crtc_init()`, `intel_crtc_state_alloc()`, `intel_crtc_state_reset()`, `intel_crtc_for_pipe()`, `intel_first_crtc()`, vblank on/off/counter/wait helpers, `intel_pipe_update_start()`, `intel_pipe_update_end()`, `intel_wait_for_vblank_workers()`, event helpers, change-detection helpers, scanline/usec converters, and bandwidth helpers. Internal code defines DRM CRTC function tables per generation, CRTC allocation/free/destroy, pipe-list insertion, pipe reordering for discrete graphics, vblank work initialization, and vblank work execution.

## Control flow
`intel_crtc_init()` logs available pipes and creates each CRTC through `__intel_crtc_init()`. That path allocates state, creates primary/sprite/cursor planes, selects a DRM CRTC func table by platform, initializes DRM CRTC with planes, attaches scaling/color/DRRS/CRC/debug/QoS properties, and inserts the CRTC into the pipe list. Atomic fast updates call `intel_pipe_update_start()` to lock PSR, prepare events/work, initialize cursor vblank work, compute vblank evasion, get vblank refs, wait out the unsafe window, and disable IRQs. `intel_pipe_update_end()` schedules LUT/cursor vblank work or arms the event, sends DSI frame updates and VRR/PSR pushes, reenables IRQs, and detects missed vblank deadlines.

## State and persistence behavior
CRTC persistent software state includes `pipe`, `pipe_head`, `config`, `plane_ids_mask`, `num_scalers`, vblank PM QoS request, debug timing fields, vblank PSR notification flag, and the embedded DRM CRTC state. Hardware-facing state includes vblank counters, active pipe/transcoder state, and plane data-rate accounting.

## Dependencies and integration points
The file integrates with DRM atomic helpers, vblank core, pipe CRC, color management, PSR/VRR/DRRS/DSI, cursor and plane code, FIFO underrun reporting, debugfs, display IRQs, and platform runtime info. Encoder code calls its vblank helpers during enable/disable and detection.

## Risks and test signals
Risks include vblank event leaks, missed vblank evasion causing atomic update failure, IRQs left disabled on error paths, incorrect pipe ordering, stale PM QoS after vblank work, and bandwidth underestimation. Test signals include IGT kms_flip/atomic/vblank/CRC tests, PSR/VRR commits, legacy cursor updates, DSI command mode commits, hotplug/modeset stress, and debug logs for atomic update failure.
