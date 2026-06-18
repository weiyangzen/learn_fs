# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_drv.h

## Purpose

`rcar_du_drv.h` defines the main R-Car DU device model, SoC capability descriptors, output identifiers, feature/quirk flags, MMIO helpers, and cross-file driver utility APIs.

## Important APIs, Types, and Functions

- Feature flags describe per-CRTC IRQs/clocks, VSP1 sources, interlaced support, TVM sync, and no-blending variants.
- `enum rcar_du_output` lists DPAD, DSI, HDMI, LVDS, TCON, and max output identifiers.
- `struct rcar_du_output_routing` maps an output to possible CRTCs and DT port number.
- `struct rcar_du_device_info` is immutable SoC metadata consumed throughout the driver.
- `struct rcar_du_cmm` stores associated CMM device and PM device link.
- `struct rcar_du_device` embeds the DRM device and stores MMIO, CRTC/group/CMM/VSP arrays, LVDS/DSI bridge pointers, shared properties, and runtime output routing selections.
- Inline helpers include `to_rcar_du_device()`, `rcar_du_has()`, `rcar_du_needs()`, `rcar_du_read()`, and `rcar_du_write()`.

## Control Flow

The header has no runtime flow, but its structures define how probe, modeset init, atomic commit, CRTC, group, encoder, and plane code share device-wide state.

## State and Persistence Behavior

`struct rcar_du_device` is the persistent per-device state for the whole DRM driver. Runtime routing fields such as `dpad0_source`, `dpad1_source`, and `vspd1_sink` are updated by atomic/KMS paths and consumed by group register programming.

## Dependencies and Integration Points

- Includes DRM device and local CMM/CRTC/group/VSP headers.
- Used by nearly every R-Car DU source file.

## Risks and Edge Cases

- Arrays are sized by maximum hardware limits; SoC tables and `num_crtcs` must never exceed those limits.
- Runtime routing fields are shared across atomic commit and group setup paths; invalid defaults can program impossible DPAD/VSP routes.
- The inline MMIO helpers perform no bounds checking.

## Test Signals

- Compile-time and probe tests should validate each SoC table fits `RCAR_DU_MAX_*` capacities.
- Atomic routing tests should inspect `dpad0_source`, `dpad1_source`, and `vspd1_sink` changes across connector combinations.
