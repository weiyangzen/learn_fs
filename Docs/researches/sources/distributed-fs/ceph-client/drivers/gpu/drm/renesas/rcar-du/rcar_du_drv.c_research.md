# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_drv.c

## Purpose

`rcar_du_drv.c` is the R-Car DU DRM platform driver. It provides SoC-specific capability tables, OF matching, DRM driver operations, suspend/resume integration, probe/remove/shutdown flow, DMA mask setup, and device registration.

## Important APIs, Types, and Functions

- Static `struct rcar_du_device_info` instances describe each supported Renesas SoC generation, features, quirks, channels, output routes, LVDS count, VSP RPF count, DPLL mask, and LVDS/DSI dot-clock masks.
- `rcar_du_of_table` maps compatible strings to those info structures.
- `rcar_du_output_name()` converts output enum values to debug strings.
- `rcar_du_driver` is the DRM driver with GEM, modeset, atomic, dumb-buffer, PRIME import, fbdev DMA, fops, and metadata callbacks.
- `rcar_du_pm_suspend()` and `rcar_du_pm_resume()` call DRM mode-config suspend/resume helpers.
- `rcar_du_probe()` allocates `struct rcar_du_device`, maps MMIO, chooses DMA mask width, initializes modeset, registers DRM, and starts client setup.
- `rcar_du_remove()` unregisters DRM, shuts down atomic state, and finalizes polling; `rcar_du_shutdown()` performs atomic shutdown.

## Control Flow

Probe exits early when firmware-only DRM drivers are requested. Otherwise it allocates a managed DRM device, stores OF match data, maps registers, coerces DMA mask to 40 bits when VSP sources handle memory access or 32 bits for direct DU scanout, initializes KMS objects, registers the DRM device, logs success, and enables generic client setup. Errors after modeset init clean up KMS polling.

Remove unregisters first so userspace cannot submit new work, then shuts down atomic state and polling. PM suspend/resume defers to DRM helpers to suspend active modesets and restore them.

## State and Persistence Behavior

SoC capability tables are immutable. Per-device persistent state lives in `struct rcar_du_device`, allocated as part of the DRM device. Probe records MMIO base, route policy, bridge pointers, CRTC/group/CMM/VSP arrays, properties, and runtime routing defaults through KMS init. DRM registration persists userspace-visible device state until remove.

## Dependencies and Integration Points

- Integrates Linux platform/OF/DMA/PM/module APIs with DRM core, GEM DMA helpers, fbdev DMA helpers, atomic helpers, probe helpers, and managed DRM allocation.
- Calls `rcar_du_modeset_init()` from `rcar_du_kms.c`.
- SoC tables are consumed by KMS, CRTC, group, plane, encoder, VSP, CMM, and bridge-specific code.

## Risks and Edge Cases

- SoC route tables are the source of truth for possible CRTCs and DT port mapping; mistakes lead to missing connectors or invalid routing.
- DMA mask selection assumes VSP-backed DU never performs memory access; mixed paths must preserve that invariant.
- Some route comments mention unsupported outputs such as TCON/analog, so DTs exposing them may be skipped or unsupported.
- Probe deferral handling intentionally avoids `dev_err_probe()` in one path to preserve recorded deferral reason; changing error logging could obscure real probe dependencies.

## Test Signals

- OF probe tests should cover every compatible and route table with representative DT endpoints.
- Build/runtime tests should cover direct scanout versus VSP-backed DMA masks.
- Suspend/resume and shutdown tests should ensure active displays are quiesced and restored without stale scanout.
- Connector enumeration should match expected outputs for each SoC info table.
