# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/Kconfig

## Purpose
This Kconfig file defines the Renesas Ethernet driver menu and the build-time feature gates for SuperH Ethernet, Ethernet AVB, Renesas Ethernet Switch, R-Car Gen4 PTP, and Renesas Ethernet-TSN support. It controls which objects from the Renesas Ethernet directory can be built and which common networking subsystems are selected for each driver.

## Important APIs, Types, And Functions
- `config NET_VENDOR_RENESAS` gates the whole Renesas Ethernet submenu and defaults to enabled.
- `config SH_ETH` enables the SuperH Ethernet driver and selects `CRC32`, `MII`, `MDIO_BITBANG`, and `PHYLIB`.
- `config RAVB` enables the Renesas Ethernet AVB driver, depends on `PTP_1588_CLOCK_OPTIONAL`, and selects `PAGE_POOL`, `PHYLIB`, `RESET_CONTROLLER`, and MDIO/MII support.
- `config RENESAS_ETHER_SWITCH` enables the R-Switch driver, depends on required PTP clock support, selects `PHYLINK`, and selects `RENESAS_GEN4_PTP`.
- `config RENESAS_GEN4_PTP` builds the shared R-Car Gen4 gPTP provider, visible as a tristate prompt only under `COMPILE_TEST`.
- `config RTSN` enables the Ethernet-TSN driver and also selects `RENESAS_GEN4_PTP`.

## Control Flow
Kconfig evaluation first asks whether the Renesas vendor menu is visible. Inside the menu, each driver symbol becomes available when its architecture or `COMPILE_TEST` dependency is met. Selecting `RENESAS_ETHER_SWITCH` or `RTSN` automatically selects the shared Gen4 PTP module, while `RAVB` can compile with optional PTP support through `PTP_1588_CLOCK_OPTIONAL`.

## State And Persistence
The file persists only build configuration in the generated kernel `.config`. There is no runtime state. The selected symbols determine which object files are compiled, whether drivers are built-in or modules, and whether required network, PHY, PTP, reset, page-pool, and checksum dependencies are available to source files.

## Dependencies And Integration Points
This file integrates with `drivers/net/ethernet/renesas/Makefile`, which consumes the symbols to build `sh_eth.o`, `ravb.o`, `rswitch.o`, `rcar_gen4_ptp.o`, and `rtsn.o`. It depends on architecture symbols such as `ARCH_RENESAS` and `SUPERH`, generic `COMPILE_TEST`, and network infrastructure symbols such as `PTP_1588_CLOCK`, `PHYLIB`, `PHYLINK`, `MDIO_BITBANG`, `PAGE_POOL`, and `RESET_CONTROLLER`.

## Risks And Edge Cases
- `RENESAS_GEN4_PTP` is only user-visible for `COMPILE_TEST`, but it is selected by real drivers; dependency changes must keep selected builds valid.
- `RENESAS_ETHER_SWITCH` selects `PHYLINK`, while the visible header/source interactions also use classic PHY and switchdev APIs; missing dependency selects elsewhere would show up as build failures.
- `RAVB` depends on optional PTP support, so source paths must compile with PTP disabled or module-optional semantics respected.
- Overly broad `COMPILE_TEST` exposure can find missing include or dependency assumptions on non-Renesas architectures.

## Test Signals
Run `allmodconfig`/`allyesconfig` and targeted `ARCH_RENESAS` builds with `RAVB`, `RENESAS_ETHER_SWITCH`, `RENESAS_GEN4_PTP`, and `RTSN` as built-in and modules. Confirm the Makefile links the expected composite objects and that dependency-selected headers and symbols are available without manual user selection.
