# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_cmm.h

## Purpose

`rcar_cmm.h` defines the DU-facing CMM API and configuration structure. It also provides no-op or error-returning stubs when CMM support is not compiled.

## Important APIs, Types, and Functions

- `CM2_LUT_SIZE` defines the required 256-entry 1D LUT size.
- `struct rcar_cmm_config` carries an optional `drm_color_lut` table; NULL disables LUT processing.
- Real APIs under `CONFIG_DRM_RCAR_CMM`: `rcar_cmm_init()`, `rcar_cmm_enable()`, `rcar_cmm_disable()`, and `rcar_cmm_setup()`.
- Stub APIs return `-ENODEV` for init, success for enable/setup, and no-op for disable.

## Control Flow

DU code can call the same functions regardless of configuration. In disabled builds, `rcar_cmm_init()` tells KMS setup that support is unavailable, while runtime calls become harmless stubs.

## State and Persistence Behavior

The header stores no state. The config object describes one requested CMM state update.

## Dependencies and Integration Points

- Forward declares `struct device` and `struct drm_color_lut`.
- Consumed by CMM implementation, CRTC color-management setup, and KMS CMM discovery.

## Risks and Edge Cases

- Stub `rcar_cmm_enable()` returning success means callers must only call runtime setup when they actually associated a real CMM device.
- The API contract that setup requires prior enable is documented in the C file, not enforced by type or state.

## Test Signals

- Build tests should cover CMM enabled and disabled configurations.
- CRTC gamma tests should reject non-`CM2_LUT_SIZE` LUT blobs before calling setup.
