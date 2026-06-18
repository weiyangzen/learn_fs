# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-j721e.h

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-j721e.h

## Purpose

This header exposes the TI J721E MHDP8546 wrapper operations and bridge input bus flags to the generic MHDP core.

## Important APIs, Types, And Functions

It includes `cdns-mhdp8546-core.h`, forward-declares `struct mhdp_platform_ops`, and declares `mhdp_ti_j721e_ops` and `mhdp_ti_j721e_bridge_input_bus_flags`.

## Control Flow

There is no executable code. The core OF table references these externs when building J721E support, passing them through `struct cdns_mhdp_platform_info`.

## State And Persistence Behavior

The header stores no runtime state; it is compile-time linkage only.

## Dependencies And Integration Points

It depends on the core header for shared types and is integrated by the core only under `CONFIG_DRM_CDNS_MHDP8546_J721E`.

## Risks And Test Signals

Declaration/definition mismatches show up at build or link time. Runtime validation is indirect through the J721E platform match path.
