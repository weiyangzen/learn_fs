# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-j721e.h

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-j721e.h

## Purpose

This header exposes the TI J721E Cadence DSI wrapper ops to the generic Cadence DSI core.

## Important APIs, Types, And Functions

It includes `cdns-dsi-core.h` and declares `extern const struct cdns_dsi_platform_ops dsi_ti_j721e_ops`.

## Control Flow

There is no executable flow. The core OF match table references `dsi_ti_j721e_ops` when the J721E wrapper is built, which lets the core call wrapper `init`, `enable`, and `disable` callbacks.

## State And Persistence Behavior

The header stores no state. It provides compile-time linkage between the platform wrapper translation unit and the core.

## Dependencies And Integration Points

It depends on the core header for the platform ops type. Its only integration point is the Cadence DSI OF match entry guarded by `CONFIG_DRM_CDNS_DSI_J721E`.

## Risks And Test Signals

Build failures with J721E enabled catch declaration mismatches. Link failures would indicate that the wrapper object was not compiled while the core expects `dsi_ti_j721e_ops`.
