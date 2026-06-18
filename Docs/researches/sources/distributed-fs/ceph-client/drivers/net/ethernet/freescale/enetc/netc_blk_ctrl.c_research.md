# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/netc_blk_ctrl.c

## Purpose
Implements the NXP NETC block-control platform driver for i.MX94/i.MX95. It performs SoC-level pre-initialization of NETCMIX, PRB, and IERB blocks before ENETC/NETC PCI child devices probe, and recreates child platform devices after setup.

## Important APIs, Types, and Functions
Important types are `struct netc_devinfo` and `struct netc_blk_ctrl`. Important functions include `netc_blk_ctrl_probe`, `netc_blk_ctrl_remove`, `imx95_netcmix_init`, `imx94_netcmix_init`, `netc_ierb_init`, `imx95_ierb_init`, `imx94_ierb_init`, `imx95_enetc_mdio_phyaddr_config`, `imx94_enetc_update_tid`, debugfs `netc_prb_show`, and helper parsers for PCI BDF, link mode, PHY address, and EMDIO masks.

## Control Flow
Probe enables the optional IPG clock, matches platform data, maps named `ierb`, `prb`, and optional `netcmix` resources, runs NETCMIX link protocol configuration from child PCI nodes and `phy-mode`, unlocks IERB with warm reset if needed, applies SoC-specific IERB LDID/timer/MDIO PHY address programming, locks IERB, warns on PRB error, creates debugfs, and calls `of_platform_populate` for child devices. Remove depopulates children and removes debugfs.

## State and Persistence
Persistent state is SoC register programming: link MII/PCS protocol, I/O variant, external pin mux, IERB LDIDs for PF/VF/timer/EMDIO, timer binding per ENETC, port MDIO PHY addresses, and PRB lock state. Software state stores mapped base pointers, devinfo, platform device pointer, and debugfs root.

## Dependencies and Integration Points
Depends on OF child PCI descriptions, `phy-mode`, `ptp-timer` phandles, `linux/fsl/netc_global.h` accessors, clocks, debugfs, and platform population. It gates later ENETC4 PF/MDIO/PTP child probing by completing shared NETC initialization first.

## Risks
Risks include DT parsing assumptions, duplicate PHY addresses between central EMDIO and port MDIO, incorrect BDF-to-link/ID mappings, IERB unlock/lock timeout, invalid PRB configuration warnings that do not fail probe, and suspend/resume requirements not fully represented in this file.

## Test Signals
Probe i.MX94 and i.MX95 device trees with enabled/disabled ENETCs, all supported `phy-mode` values, central EMDIO plus port MDIO, custom `ptp-timer` phandles, debugfs PRB state, duplicate PHY address rejection, IERB lock timeout injection, and child-device probe ordering.
