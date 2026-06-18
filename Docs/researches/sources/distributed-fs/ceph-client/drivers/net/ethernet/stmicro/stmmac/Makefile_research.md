# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/Makefile

## Purpose
The STMMAC Makefile builds the shared STMMAC core object and conditionally builds platform and PCI glue drivers.

## Important APIs, Types, And Functions
- `stmmac.o` is composed from core datapath, ethtool, MDIO, ring/chain modes, DWMAC 100/1000/4/5/XGMAC cores, descriptors, PTP, traffic control, XDP, EST, FPE, VLAN, PCS, and optional selftests.
- `stmmac-platform.o` is composed from `stmmac_platform.o`.
- Conditional `obj-$(CONFIG_DWMAC_*)` entries build specific platform glue modules.
- `STMMAC_LIBPCI`, `STMMAC_PCI`, and PCI DWMAC variants are mapped to their objects.

## Control Flow
kbuild first composes the shared core when `CONFIG_STMMAC_ETH` is set, then emits enabled platform/PCI glue modules based on individual Kconfig symbols. The comment notes that the generic platform driver must be ordered last.

## State And Persistence
Build-only; no runtime state.

## Dependencies And Integration Points
This file is the build integration point for the STMMAC core and all glue drivers in this subset: `chain_mode.c`, descriptor headers via core objects, DWC QoS, Anarion, EIC7700, generic, i.MX, Ingenic, Intel platform, and Intel PCI.

## Risks
Object ordering matters for generic platform matching; moving `DWMAC_GENERIC` earlier may cause overly broad compatible strings to bind before specific drivers. Adding a new glue driver requires matching Kconfig and Makefile changes.

## Test Signals
`make M=drivers/net/ethernet/stmicro/stmmac` with selected configs should compile the expected object set, and module aliases should be provided by each glue driver's OF/PCI tables.
