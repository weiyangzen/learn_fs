# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_kms.h

## Purpose

`tidss_kms.h` exposes the single KMS initialization entry point used by the TIDSS platform driver.

## Important APIs, Types, and Functions

- Forward declares `struct tidss_device`.
- Declares `int tidss_modeset_init(struct tidss_device *tidss)`.

## Control Flow

`tidss_drv.c` calls `tidss_modeset_init()` after DISPC and OLDI initialization and before IRQ installation and DRM registration. The implementation creates mode config, CRTCs, planes, encoders, connectors, and vblank state.

## State and Persistence Behavior

The header has no state. A successful call populates persistent KMS arrays inside `struct tidss_device` and mode-config state inside the embedded DRM device.

## Dependencies and Integration Points

It is the boundary between platform-driver probe and TIDSS KMS object construction.

## Risks and Edge Cases

- The declaration hides that DISPC and OLDI must already be initialized.
- Callers must handle `-EPROBE_DEFER` without treating it as a hard device failure.

## Test Signals

Probe tests should verify successful and deferred `tidss_modeset_init()` behavior, and build tests should catch signature drift between the header and implementation.
