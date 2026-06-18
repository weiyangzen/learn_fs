# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_writeback.h

## Purpose

`rcar_du_writeback.h` exposes the small writeback integration surface between R-Car DU CRTC/VSP code and the optional DRM writeback implementation.

## Important APIs, Types, and Functions

It declares `rcar_du_writeback_init()`, `rcar_du_writeback_setup()`, and `rcar_du_writeback_complete()` when `CONFIG_DRM_RCAR_WRITEBACK` is enabled. Stubs return `-ENXIO` for init and no-op for setup/completion otherwise.

## Control Flow

CRTC setup can call init while building KMS objects. VSP atomic flush passes a `vsp1_du_writeback_config` to setup, and the VSP completion callback calls complete.

## State and Persistence Behavior

The header owns no state. It defines whether writeback is active at build time and controls the fallback behavior when writeback support is absent.

## Dependencies and Integration Points

It forward-declares R-Car DU and VSP config structures and includes DRM plane definitions. It integrates with `rcar_du_vsp.c` and CRTC initialization code.

## Risks and Edge Cases

Callers must tolerate `-ENXIO` when writeback is disabled. Setup and completion stubs silently drop work, so code must not queue writeback jobs unless init succeeded.

## Test Signals

Compile both with and without `CONFIG_DRM_RCAR_WRITEBACK`, and verify connector presence only when support is enabled.
