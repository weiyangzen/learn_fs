# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/Makefile

## Purpose

The R-Car DU Makefile defines the main `rcar-du-drm` composite object and optional companion objects for CMM, HDMI, LVDS, MIPI DSI, VSP, and writeback.

## Important APIs, Types, and Functions

- `rcar-du-drm-y` consists of `rcar_du_crtc.o`, `rcar_du_drv.o`, `rcar_du_encoder.o`, `rcar_du_group.o`, `rcar_du_kms.o`, and `rcar_du_plane.o`.
- `rcar-du-drm-$(CONFIG_DRM_RCAR_VSP)` adds `rcar_du_vsp.o`.
- `rcar-du-drm-$(CONFIG_DRM_RCAR_WRITEBACK)` adds `rcar_du_writeback.o`.
- Separate module/built-in objects are gated for `rcar_cmm.o`, `rcar_dw_hdmi.o`, `rcar_lvds.o`, and `rcar_mipi_dsi.o`.

## Control Flow

Kbuild combines core DU objects into one driver when `CONFIG_DRM_RCAR_DU` is enabled and conditionally extends it with VSP/writeback support. Companion hardware blocks build as separate objects/modules under their own symbols.

## State and Persistence Behavior

No runtime state. It controls link composition and module boundaries.

## Dependencies and Integration Points

Works with Kconfig symbols in the same directory. The object split matches source-level responsibilities: platform driver, KMS setup, CRTCs, groups, planes, encoders, VSP/writeback, and bridge-specific companion drivers.

## Risks and Edge Cases

If a source file uses symbols from optional objects without Kconfig guards or stubs, link failures can occur in partial configurations.

## Test Signals

Build coverage should verify each optional symbol toggles the expected object and that `rcar-du-drm` links with and without VSP/writeback support.
