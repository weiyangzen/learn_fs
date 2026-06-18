# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic_helper.c

## Purpose
`drm_atomic_helper.c` is the central DRM/KMS helper implementation for atomic modeset checking, commit sequencing, plane updates, legacy API compatibility, suspend/resume state capture, and legacy page flips on top of the atomic core. It is shared Linux DRM infrastructure in this source tree, not Ceph-specific logic.

## Important APIs, Types, and Functions
Modeset validation is centered on `drm_atomic_helper_check_modeset()`, with internal routing helpers such as `handle_conflicting_encoders()`, `update_connector_routing()`, `set_best_encoder()`, `steal_encoder()`, `mode_valid()`, and `mode_fixup()`. Plane validation uses `drm_atomic_helper_check_plane_state()`, `drm_atomic_helper_check_crtc_primary_plane()`, `drm_atomic_helper_check_planes()`, and the top-level `drm_atomic_helper_check()`.

Commit APIs include `drm_atomic_helper_commit()`, `drm_atomic_helper_commit_tail()`, `drm_atomic_helper_commit_tail_rpm()`, modeset disable/enable helpers, `drm_atomic_helper_commit_planes()`, `drm_atomic_helper_prepare_planes()`, `drm_atomic_helper_cleanup_planes()`, `drm_atomic_helper_swap_state()`, and nonblocking tracking through `drm_atomic_helper_setup_commit()`, `drm_atomic_helper_wait_for_dependencies()`, `drm_atomic_helper_commit_hw_done()`, and `drm_atomic_helper_commit_cleanup_done()`. Legacy wrappers include plane update/disable, set_config, disable_all, shutdown, suspend/resume, and page-flip helpers.

## Control Flow
Validation compares old/new CRTC, connector, and plane states, marks mode/active/connector/plane changes, resolves encoders, pulls affected connectors/planes/bridges into the atomic state, runs connector/bridge/encoder/CRTC checks, optionally normalizes zpos, and runs plane and CRTC atomic checks.

The default commit path prepares commit tracking and framebuffer resources, waits on fences for blocking commits, swaps staged state into live DRM object pointers, then either queues `commit_work` for nonblocking commits or runs `commit_tail()` inline. The default tail disables old outputs, commits planes, enables new outputs, fakes vblank where needed, signals hardware done, waits for vblank completion, cleans old framebuffer resources, signals cleanup done, and releases the atomic state.

## State and Persistence Behavior
The file manipulates persistent object state pointers (`crtc->state`, `plane->state`, `connector->state`, colorop/private state) through `drm_atomic_helper_swap_state()`. Old states remain stored in the atomic state for cleanup. `struct drm_crtc_commit` tracks `flip_done`, `hw_done`, and `cleanup_done` across asynchronous work and is attached to CRTC, connector, and plane states. Framebuffer/writeback resources are prepared before the software swap and cleaned only after they are no longer displayed. Suspend duplicates current atomic state and expects the driver to keep that state valid until resume.

## Dependencies and Integration Points
This file integrates DRM atomic core, `drm_atomic_uapi.c`, `drm_atomic_state_helper.c`, blend/zpos helpers, bridge chains, connector/encoder/CRTC/plane helper callbacks, GEM framebuffer preparation, DMA fences, vblank and event delivery, writeback, self-refresh helpers, damage helpers, panic display locking, and modeset lock backoff. Drivers plug in through helper function tables and optional `drm_mode_config_helper_funcs` hooks.

## Risks
Sequencing mistakes can cause state use-after-free, missed events, permanent commit stalls, framebuffer lifetime bugs, or visible display corruption. Encoder routing and clone-mask handling are fragile because one encoder must not be assigned to conflicting connectors. Async commit support is intentionally narrow; widening it without matching ordering guarantees can overwrite synchronous state. Commit completion reference balancing is critical because later commits wait on prior `hw_done` and `cleanup_done`.

## Test Signals
Strong signals are IGT atomic modeset/plane/cursor/page-flip/writeback/suspend tests, multi-CRTC nonblocking stress, hot-unplug during atomic checks, legacy `SETCRTC` and page-flip compatibility, explicit and implicit fence waits, no `flip_done`/vblank/cleanup timeouts, and no KASAN/KCSAN/KFENCE reports during repeated commits and teardown.
