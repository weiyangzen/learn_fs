# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/Kconfig

## Purpose
This Kconfig file defines build-time configuration for the Microchip Sparx5 switch driver, optional DCB support, and LAN969x family support layered on top of Sparx5.

## Important APIs, Types, And Functions
The symbols are `SPARX5_SWITCH`, `SPARX5_DCB`, and `LAN969X_SWITCH`. `SPARX5_SWITCH` is a tristate with dependencies on switchdev, MMIO, OF, supported architectures or compile testing, optional PTP clock support, and bridge availability. It selects `PHYLINK`, `PHY_SPARX5_SERDES`, `RESET_CONTROLLER`, `VCAP`, and `FDMA`. `SPARX5_DCB` is a bool default-y option gated by `SPARX5_SWITCH && DCB`. `LAN969X_SWITCH` is a bool depending on `SPARX5_SWITCH` and selects `PAGE_POOL`.

## Control Flow
There is no runtime control flow. The kernel configuration controls whether the shared Sparx5 object is built, whether `sparx5_dcb.o` is included, and whether LAN969x-specific files and page-pool based FDMA support are compiled into the Sparx5 module.

## State And Persistence
State is the kernel `.config` selection. It persists only through normal kernel configuration and build artifacts.

## Dependencies And Integration Points
This file connects the driver to net/switchdev, phylink, serdes PHY support, reset controller support, VCAP core, FDMA core, DCBNL, page_pool, OF platform probing, and architecture guards for Sparx5 and LAN969x SoCs.

## Risks And Edge Cases
`LAN969X_SWITCH` is a bool under a tristate parent, so LAN969x support is compiled into the Sparx5 module rather than as a separate module. Missing `PAGE_POOL` selection would break LAN969x FDMA compilation. Bridge dependency allows `BRIDGE=n`, so code must tolerate no bridge module. Compile-test coverage can expose architecture-specific assumptions around MMIO and DMA.

## Test Signals
Build configurations should include `SPARX5_SWITCH=m/y`, with and without `SPARX5_DCB`, with `LAN969X_SWITCH=y`, `COMPILE_TEST=y`, and bridge disabled. Expected output is one Sparx5 module containing optional LAN969x objects when selected.
