# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/appletbdrm.c

## Purpose

`appletbdrm.c` is a USB DRM/KMS driver for Apple Touch Bar displays. It discovers bulk endpoints, speaks the Touch Bar request/response protocol, exposes a fixed non-desktop DRM connector, converts/flushes framebuffer damage to device-oriented frame messages, and clears the display on disable/shutdown.

## Important APIs, Types, and Functions

- Protocol structures: request/response headers, simple request, information response, frame payload, framebuffer request footer, framebuffer request, and update-complete response.
- `struct appletbdrm_device` embeds USB endpoint IDs, display dimensions, DRM device, fixed mode, connector, primary plane, CRTC, and encoder.
- `struct appletbdrm_plane_state` extends DRM shadow plane state with allocated USB request/response buffers and damage frame sizes.
- USB protocol helpers: `appletbdrm_send_request()`, `appletbdrm_read_response()`, `appletbdrm_send_msg()`, `appletbdrm_clear_display()`, `appletbdrm_signal_readiness()`, and `appletbdrm_get_information()`.
- Plane helpers: `appletbdrm_primary_plane_helper_atomic_check()` allocates a request sized for current damage clips; `appletbdrm_flush_damage()` fills frame records, converts XRGB8888 to BGR888 if needed, sends the USB bulk request, reads update completion, and checks the timestamp; reset/duplicate/destroy manage shadow state.
- `appletbdrm_setup_mode_config()` initializes one primary plane, one CRTC, one encoder, one USB connector, fixed mode, orientation, non-desktop property, and mode config funcs.
- USB lifecycle: `appletbdrm_probe()`, `appletbdrm_disconnect()`, and `appletbdrm_shutdown()`.

## Control Flow

USB probe finds bulk endpoints, allocates the DRM device, stores endpoint addresses, sets interface data, optionally sets the DMA device for buffer sharing, requests display information, sends readiness, sets up DRM mode config, registers the DRM device, and clears the display. Userspace commits damage to the primary plane; atomic check sizes and allocates protocol buffers based on damage clips, and atomic update flushes those damaged rectangles via USB bulk messages. Disable and shutdown clear or shut down display state so persistent Touch Bar contents are removed.

The device coordinate system swaps axes and inverts one axis. `appletbdrm_setup_mode_config()` creates the fixed DRM mode with width/height swapped, and `appletbdrm_flush_damage()` translates damage rectangles into device `begin_x`, `begin_y`, `width`, and `height`.

## State and Persistence Behavior

Device width/height and fixed mode persist after probe. Per-atomic plane state owns request/response allocations and frees them in `atomic_destroy_state()`. Display contents persist on the physical device across boots, so disable/shutdown paths explicitly clear or shut down scanout. USB device unplug is handled through `drm_dev_unplug()` and `drm_dev_enter()/exit()` guards around update/disable.

## Dependencies and Integration Points

The file depends on USB bulk APIs, DRM atomic/connector/CRTC/encoder helpers, damage helpers, SHMEM GEM, shadow-plane helpers, framebuffer format conversion helpers, fixed-mode helpers, and DRM device unplug protection. It matches USB vendor/product `05ac:8302` with audio-video interface class.

## Risks and Edge Cases

- In `appletbdrm_get_information()`, an early send failure returns without freeing `info`, leaking the allocation on that path.
- In atomic check, if response allocation fails after request allocation succeeds, the request is not freed until state destroy; this is acceptable if the failed state is destroyed but should be verified by DRM atomic cleanup paths.
- `appletbdrm_flush_damage()` calls `drm_gem_fb_end_cpu_access()` even when `begin_cpu_access` failed, due to the shared exit label.
- Timestamp comparison logs a mismatch but does not set `ret`, so the update can report success after a mismatch.
- Damage buffer sizing uses damage rectangles before intersection with `state->dst`; skipped rectangles can leave unused allocated frame space, which is safe but worth understanding.
- USB protocol fields are partly unknown constants; firmware changes can break assumptions about headers, footer, readiness, or expected pixel format.
- Probe registers the DRM device before `appletbdrm_clear_display()`; if clear fails, probe returns error after registration.

## Test Signals

Tests should cover endpoint discovery failure, information response validation for dimensions/bpp/pixel format, readiness-signal retry handling, fixed mode dimensions/orientation/non-desktop property, BGR888 and XRGB8888 damage flushes, multiple damage clips, zero-damage commits, timestamp mismatch handling, unplug during update, disable clear display, shutdown clearing persistent content, and error-path leak detection with KASAN/KMEMLEAK.
