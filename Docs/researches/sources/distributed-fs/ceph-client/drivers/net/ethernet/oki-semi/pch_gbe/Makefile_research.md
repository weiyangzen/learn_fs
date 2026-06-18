# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/Makefile

## Purpose
Defines object composition of the PCH GBE driver.

## Important APIs, Types, And Functions
Builds `pch_gbe.o` for `CONFIG_PCH_GBE`; `pch_gbe-y` includes `pch_gbe_phy.o`, `pch_gbe_ethtool.o`, `pch_gbe_param.o`, and `pch_gbe_main.o`.

## Control Flow
kbuild links the listed implementation objects into one built-in object or module.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Combines PHY helpers, ethtool support, module parameter validation, and PCI/netdev core.

## Risks And Edge Cases
Missing an object breaks link-time resolution for the corresponding driver area.

## Test Signals
`CONFIG_PCH_GBE=y/m` should produce one `pch_gbe` target containing all four objects.
