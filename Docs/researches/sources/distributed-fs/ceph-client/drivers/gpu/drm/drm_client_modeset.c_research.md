# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client_modeset.c

## Purpose
`drm_client_modeset.c` selects and commits display configurations for in-kernel DRM clients. It chooses connectors, modes, CRTCs, tile offsets, rotations, DPMS state, and vblank waits for fbdev-like clients.

## Important APIs, Types, And Functions
Public APIs are `drm_client_modeset_create()`, `drm_client_modeset_free()`, `drm_client_modeset_probe()`, `drm_client_rotation()`, `drm_client_modeset_check()`, `drm_client_modeset_commit_locked()`, `drm_client_modeset_commit()`, `drm_client_modeset_dpms()`, and `drm_client_modeset_wait_for_vblank()`. Important internals handle command-line/preferred/first/tiled mode selection, firmware config reuse, clone targeting, recursive CRTC assignment, atomic commit, and legacy commit.

## Control Flow
Creation allocates a sentinel-terminated modeset array and connector slots per CRTC. Probe enumerates connectors, fills modes, computes enabled connectors, tries firmware state for atomic drivers, then falls back to clone or preferred target selection and recursive CRTC scoring. The chosen modes are duplicated into `client->modesets` under `modeset_mutex`.

Atomic commit obtains all plane states, resets rotation, disables non-primary planes, applies supported primary-plane rotation, calls `__drm_atomic_helper_set_config()`, optionally forces inactive CRTCs for DPMS off, and retries on `-EDEADLK`. Legacy commit locks all modesets, disables non-primary planes, resets rotation properties, clears cursors, and calls `drm_mode_set_config_internal()`.

## State And Persistence
The persistent state is `client->modesets`: CRTC, duplicated mode, connector references, FB pointer, and x/y offsets. `modeset_mutex` serializes updates. Temporary connector/mode/CRTC arrays are freed after probing.

## Dependencies And Integration Points
It integrates with connector mode enumeration, command-line mode parsing, tiled monitor metadata, CRTC/encoder masks, atomic helpers, DRM master internal acquire/release, DPMS properties, plane rotation, legacy cursor/config functions, and vblank APIs.

## Risks And Edge Cases
Recursive CRTC picking can grow with connector count. Clone support is intentionally limited. Tiled fallback behavior is subtle when only some tiles are present. Atomic commits disable non-primary planes and require correct master exclusion. Rotation currently rejects 90/270 degree use even when panel orientation requests it. Deadlock retry handling is essential.

## Test Signals
KUnit coverage is included via `tests/drm_client_modeset_test.c` when enabled. Add tests for command-line/preferred/first/tiled modes, firmware fallback, clone limits, CRTC scoring, atomic `-EDEADLK` retry, DPMS on/off, vblank `-EBUSY`, and rotation masks.
