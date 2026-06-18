# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/Makefile

## Purpose
This Makefile descends into the STMMAC subdirectory when the main STMMAC Ethernet symbol is enabled.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_STMMAC_ETH) += stmmac/` selects the subdirectory.

## Control Flow
kbuild includes `drivers/net/ethernet/stmicro/stmmac/Makefile` when `CONFIG_STMMAC_ETH` is enabled.

## State And Persistence
Build-only; no runtime state.

## Dependencies And Integration Points
Depends on `STMMAC_ETH` from the nested Kconfig.

## Risks
No direct risk beyond build omission if the parent symbol is not enabled.

## Test Signals
Full kernel builds should traverse the `stmmac/` directory whenever STMMAC is built-in or modular.
