# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/Makefile

## Purpose
Defines the Kbuild composite object for the Siena driver.

## Important build entries
`sfc-siena-y` includes core hardware, lifecycle, common reset/datapath, channels, NIC, TX/RX, self-test, ethtool, PTP, MCDI, port, and monitor objects. `sfc-siena-$(CONFIG_SFC_SIENA_MTD)` adds `mtd.o`; `sfc-siena-$(CONFIG_SFC_SIENA_SRIOV)` adds `siena_sriov.o`; `obj-$(CONFIG_SFC_SIENA)` builds `sfc-siena.o`.

## Control flow and integration
The linked object set must satisfy symbols referenced by `efx.c`, `efx_common.c`, channel, ethtool, and hardware type tables. Conditional object inclusion mirrors Kconfig feature switches.

## State and persistence behavior
No runtime state. This is persistent build metadata.

## Dependencies
Depends on Kbuild composite-object semantics and Kconfig symbols.

## Risks
Missing objects create unresolved symbols, while adding source files without this Makefile leaves code unbuilt. Optional feature stubs must match conditional objects.

## Test signals
Kernel builds with `SFC_SIENA=y/m` and optional feature combinations validate the recipe.
