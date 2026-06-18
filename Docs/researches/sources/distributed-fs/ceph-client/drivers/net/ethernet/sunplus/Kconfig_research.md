# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/Kconfig

## Purpose
This Kconfig file declares the Sunplus Ethernet driver menu. It exposes a vendor gate `NET_VENDOR_SUNPLUS` and the `SP7021_EMAC` tristate option for Sunplus SP7021 dual 10/100 Ethernet hardware.

## Important APIs, Types, And Options
- `config NET_VENDOR_SUNPLUS` is a boolean menu gate named "Sunplus devices", defaults to `y`, and depends on `ARCH_SUNPLUS || COMPILE_TEST`.
- `if NET_VENDOR_SUNPLUS` scopes Sunplus device-specific options.
- `config SP7021_EMAC` is a tristate named "Sunplus Dual 10M/100M Ethernet devices", depends on `SOC_SP7021 || COMPILE_TEST`, selects `PHYLIB`, and documents that the driver creates two net-device interfaces and builds as module `sp7021_emac`.

## Control Flow And State Behavior
Kconfig controls build visibility and dependency resolution only. If `NET_VENDOR_SUNPLUS=n`, the SP7021 prompt is hidden and no Sunplus object is selected through this subtree. If `SP7021_EMAC=m` or `y`, the Makefile builds the composite `sp7021_emac` driver from its object list. No runtime state is stored here.

## Dependencies And Integration Points
The file integrates with the kernel networking vendor menu and the adjacent Makefile. `COMPILE_TEST` allows wider build coverage outside Sunplus architectures. `PHYLIB` selection ensures the selected driver has PHY framework support.

## Risks And Edge Cases
- `NET_VENDOR_SUNPLUS` defaults to `y`, so compile-test configurations may expose the submenu broadly.
- `SP7021_EMAC` selects `PHYLIB` but does not express MDIO/GPIO/clock/reset dependencies here; those may be handled in source or broader SoC configuration.
- The help text promises two net-device interfaces, which should stay consistent with the driver implementation.

## Test Signals
Run Kconfig build matrix checks for `ARCH_SUNPLUS`, non-Sunplus `COMPILE_TEST`, built-in, module, and disabled configurations. Confirm `sp7021_emac.ko` naming and PHYLIB dependency resolution.
