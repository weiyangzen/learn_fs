# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-j721e.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-j721e.c

## Purpose

This file implements TI J721E wrapper support for the Cadence MHDP8546 DisplayPort/eDP block. It maps wrapper registers, selects the supported DPI-to-VIF routing, and exports required input bus flags.

## Important APIs, Types, And Functions

`cdns_mhdp_j721e_init()` maps resource index 1 to `mhdp->j721e_regs`. `cdns_mhdp_j721e_enable()` enables VIF0 and selects DPI2. `cdns_mhdp_j721e_disable()` clears the wrapper DSC config register to defaults. `mhdp_ti_j721e_ops` and `mhdp_ti_j721e_bridge_input_bus_flags` are consumed by the core OF match data.

## Control Flow

The core calls wrapper init during probe, wrapper enable during atomic enable before VIF clock/video programming, and wrapper disable during atomic disable after VIF clock shutdown. Bus flags are copied in the core atomic check so the upstream source samples on the correct edges with DE high.

## State And Persistence Behavior

State is limited to the extra MMIO pointer and wrapper register writes. The routing is not dynamic and is reset on disable.

## Dependencies And Integration Points

It depends on the MHDP core data structures, platform resource ordering, and `CONFIG_DRM_CDNS_MHDP8546_J721E`. The supported SST routing is DSS0 DPI0 to eDP DPI2 through VIF0.

## Risks And Test Signals

The disable path clears `DPTX_DSC_CFG` rather than `DPTX_SRC_CFG`, so wrapper routing reset assumptions should be checked against hardware docs. Test signals are correct J721E eDP output, stable sampling edges, and wrapper resource mapping success.
