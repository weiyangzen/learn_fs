# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/Kconfig

## Purpose
This file adds the STMicroelectronics/Synopsys Ethernet vendor menu and includes the STMMAC Kconfig subtree.

## Important APIs, Types, And Functions
- `NET_VENDOR_STMICRO` is a vendor-level bool, default `y`, requiring `HAS_IOMEM`.
- If enabled, it sources `drivers/net/ethernet/stmicro/stmmac/Kconfig`.

## Control Flow
Kernel configuration enters this vendor menu, then delegates all specific STMMAC options to the nested Kconfig.

## State And Persistence
Configuration-only; no runtime state.

## Dependencies And Integration Points
Connects the STMMAC driver family to the global Ethernet driver configuration hierarchy.

## Risks
Disabling `NET_VENDOR_STMICRO` hides all STMMAC options, including many non-ST SoC glue drivers that use Synopsys IP.

## Test Signals
Menu visibility and successful selection of nested `STMMAC_ETH` and platform/PCI variants.
