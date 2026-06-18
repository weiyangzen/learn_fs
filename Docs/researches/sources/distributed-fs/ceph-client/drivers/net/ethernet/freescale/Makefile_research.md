# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/Makefile

## Purpose
This Makefile maps Freescale Ethernet Kconfig symbols to built objects and subdirectories.

## Important APIs, Types, and Functions
It builds composite objects for `fec` (`fec_main.o fec_ptp.o`), `gianfar_driver` (`gianfar.o gianfar_ethtool.o`), and `ucc_geth_driver` (`ucc_geth.o ucc_geth_ethtool.o`). It conditionally descends into `fs_enet/`, `fman/`, and `dpaa/`, and always descends into `dpaa2/` and `enetc/` so their internal Makefiles can decide based on their own symbols.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_*)` variables and composite `*-objs` lists. `CONFIG_FEC_MPC52xx_MDIO=y` adds `fec_mpc52xx_phy.o` to the MPC52xx build. DPAA1 is gated here by `CONFIG_FSL_DPAA_ETH`; DPAA2 and ENETC are always visited.

## State and Persistence
There is no runtime state. Build state is produced in the kernel output tree.

## Dependencies and Integration Points
This file integrates Kconfig symbols from `freescale/Kconfig` with Kbuild. It depends on subdirectory Makefiles for DPAA2, ENETC, FMan, and fs_enet.

## Risks
Unconditional `obj-y += dpaa2/ enetc/` is intentional for subdirectory symbol resolution but can surprise readers expecting top-level gating. Composite object names must match module expectations. Mismatched Kconfig/Makefile symbols would cause silent missing drivers.

## Test Signals
Run `make drivers/net/ethernet/freescale/` under representative configs and verify expected modules/objects are emitted for FEC, Gianfar, UCC, FMan, DPAA, DPAA2, and ENETC.
