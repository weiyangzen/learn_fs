# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/Kconfig

## Purpose
This Kconfig file defines the Cavium Ethernet driver menu and the build-time configuration surface for Thunder NIC, BGX/RGX MAC blocks, the shared Cavium PTP clock, LiquidIO PF/core support, Octeon management Ethernet, and LiquidIO VF support.

## Important APIs, Types, And Functions
The important symbols are `NET_VENDOR_CAVIUM`, `THUNDER_NIC_PF`, `THUNDER_NIC_VF`, `THUNDER_NIC_BGX`, `THUNDER_NIC_RGX`, `CAVIUM_PTP`, `LIQUIDIO_CORE`, `LIQUIDIO`, `OCTEON_MGMT_ETHERNET`, and `LIQUIDIO_VF`. It has no C APIs, but these symbols gate compilation and module composition throughout `drivers/net/ethernet/cavium`.

## Control Flow
`NET_VENDOR_CAVIUM` opens the vendor subtree. The Thunder PF selects BGX; BGX and RGX select PHY/MDIO dependencies; Thunder VF implies `CAVIUM_PTP`. `CAVIUM_PTP` depends on PCI, 64-bit builds, and the PTP clock framework. `LIQUIDIO` selects `LIQUIDIO_CORE`, firmware loading, CRC32, and devlink; `LIQUIDIO_VF` selects `LIQUIDIO_CORE` and requires PCI MSI.

## State And Persistence
State is configuration metadata persisted in kernel `.config`. It affects whether objects are built-in, modules, or absent. It does not create runtime state.

## Dependencies And Integration Points
This integrates with the kernel Kconfig dependency resolver, module build rules, PCI, PHYLIB, MDIO, PTP, FW_LOADER, CRC32, NET_DEVLINK, and PCI_IOV/MSI-related runtime assumptions implied by the selected drivers.

## Risks
Misconfigured dependencies can produce missing shared objects or unavailable runtime features. `THUNDER_NIC_VF` only implies, rather than selects, `CAVIUM_PTP`; timestamp consumers must tolerate absent PTP support. `LIQUIDIO` redundantly depends on PCI through both `64BIT && PCI` and `PCI`.

## Test Signals
Run `make olddefconfig` and compile matrixes for built-in/module/disabled combinations, especially `LIQUIDIO_CORE` selected by PF and VF, `CAVIUM_PTP` absent with optional PTP users, and Thunder PF/BGX/RGX dependency closure.
