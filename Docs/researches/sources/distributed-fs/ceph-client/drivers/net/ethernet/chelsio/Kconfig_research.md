# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/Kconfig

## Purpose
This Kconfig file declares the Chelsio Ethernet driver menu and feature symbols. It gates all Chelsio Ethernet questions behind `NET_VENDOR_CHELSIO` and exposes build options for T1 (`cxgb`), optional T1 gigabit support, T3 (`cxgb3`), T4/T5/T6 PF (`cxgb4`), T4 DCB, T5 FCoE, T4/T5/T6 VF (`cxgb4vf`), the shared Chelsio library, and inline crypto subconfiguration.

## Important Symbols
`NET_VENDOR_CHELSIO` is a boolean vendor menu depending on PCI. `CHELSIO_T1` is a tristate selecting `CRC32` and `MDIO`; `CHELSIO_T1_1G` is a boolean depending on `CHELSIO_T1`. `CHELSIO_T3` depends on `PCI && INET` and selects firmware loading and MDIO. `CHELSIO_T4` depends on PCI, optional TLS compatibility, and optional PTP clock support, and selects firmware loading, MDIO, and zlib deflate. `CHELSIO_T4_DCB`, `CHELSIO_T4_FCOE`, `CHELSIO_T4VF`, and `CHELSIO_LIB` control advanced PF, VF, and library builds.

## Control Flow and Integration
Kconfig symbols flow into the Chelsio directory Makefiles. Enabling `CHELSIO_T1` includes `cxgb/` and builds the `cxgb` module; enabling later generations includes their directories. The `source "drivers/net/ethernet/chelsio/inline_crypto/Kconfig"` line nests inline crypto options under the vendor menu.

## State and Persistence
This file persists build-time configuration choices in kernel `.config`; it has no runtime state. The selected symbols determine compiled objects, modules, dependencies, and feature availability.

## Dependencies and Risks
The main dependency is PCI. Feature-specific dependencies ensure required subsystems are available. Risks include incorrect `select` usage causing missing symbols at build time, stale help URLs/docs, hidden feature coupling between T4 DCB and FCoE, and vendor menu defaults causing unexpected prompt visibility.

## Test Signals
Run `oldconfig`/`menuconfig` visibility checks and build matrix tests for built-in and module variants of T1/T3/T4/T4VF, with and without DCB/FCoE/inline crypto. Confirm that dependency-disabled symbols are not visible and that selected helper subsystems satisfy link requirements.
