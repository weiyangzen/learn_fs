# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_mw.h

## Purpose

`malidp_mw.h` is the small internal header for Mali-DP memory-write/writeback support. It declares the connector initialization and atomic commit hooks used by the top-level driver.

## Important APIs, Types, And Functions

The two declarations are `malidp_mw_connector_init(struct drm_device *drm)` and `malidp_mw_atomic_commit(struct drm_device *drm, struct drm_atomic_state *old_state)`. The implementation-specific connector state and helpers remain private to `malidp_mw.c`.

## Control Flow

This header has no direct control flow. `malidp_drv.c` calls `malidp_mw_connector_init()` during mode-config initialization after CRTC setup. The custom atomic commit tail calls `malidp_mw_atomic_commit()` after display-plane register programming and before modeset enables/config-valid completion.

## State And Persistence Behavior

The header stores no state. It defines the cross-file contract through which writeback connector state and hardware memory-write state are managed by the implementation and the top-level commit path.

## Dependencies And Integration Points

The declarations require DRM device and atomic-state types from the including C files. The header integrates `malidp_drv.c` with `malidp_mw.c` and indirectly with hardware callbacks and SE IRQ completion logic.

## Risks And Edge Cases

Because this is the only public contract for writeback in the Mali-DP driver, signature or ordering changes must be coordinated with the commit tail. Passing `old_state` to `malidp_mw_atomic_commit()` is misleading because the implementation reads current connector state from `mw_conn->base.state`; future changes should preserve the current commit ordering assumptions.

## Test Signals

Build coverage with writeback enabled, connector creation on variants with `enable_memwrite`, and atomic commit tests with and without writeback jobs validate this header contract.
