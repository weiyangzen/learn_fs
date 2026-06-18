# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/Makefile

## Purpose

`rz-du/Makefile` wires the RZ/G2L Display Unit and MIPI DSI source files into kernel objects.

## Important APIs, Types, and Functions

It builds `rzg2l-du-drm.o` from `rzg2l_du_crtc.o`, `rzg2l_du_drv.o`, `rzg2l_du_encoder.o`, and `rzg2l_du_kms.o`, conditionally adds `rzg2l_du_vsp.o` under `CONFIG_VIDEO_RENESAS_VSP1`, and builds `rzg2l_mipi_dsi.o` under `CONFIG_DRM_RZG2L_MIPI_DSI`.

## Control Flow

Kbuild uses the config symbols from `Kconfig` to select the DU aggregate object and optional DSI bridge module.

## State and Persistence Behavior

No runtime state exists. The Makefile defines link composition and module boundaries.

## Dependencies and Integration Points

It integrates with kernel Kbuild and the local Kconfig symbols.

## Risks and Edge Cases

Because `DRM_RZG2L_DU` depends on VSP1, omitting `rzg2l_du_vsp.o` would normally not happen for valid configs; compile-test combinations should still cover the conditional object.

## Test Signals

Run kernel builds for enabled, module, disabled, and MIPI DSI combinations.
