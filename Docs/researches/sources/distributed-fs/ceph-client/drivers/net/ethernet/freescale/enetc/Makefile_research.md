# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/Makefile

Purpose: Maps ENETC/NETC Kconfig symbols to kernel modules and object files. It defines the build composition for shared core, PF/VF, ENETC4, MDIO, PTP, QoS, IERB, NTMP, and NETC block-control code.

Important targets: `fsl-enetc-core.o` includes `enetc.o`, `enetc_cbdr.o`, and `enetc_ethtool.o`. `nxp-enetc-pf-common.o` includes `enetc_pf_common.o`. `nxp-netc-lib.o` includes `ntmp.o`. `fsl-enetc.o` includes `enetc_pf.o` and conditionally `enetc_msg.o` and `enetc_qos.o`. `nxp-enetc4.o` includes `enetc4_pf.o` and conditionally `enetc4_debugfs.o` under `CONFIG_DEBUG_FS`. Separate modules are declared for VF, IERB, MDIO, PTP, and NETC block control.

Control flow and state: The Makefile has build-time flow only. It persists no runtime state, but its conditional object selection determines whether runtime features such as SR-IOV messaging, QoS, and debugfs exist in the compiled module.

Dependencies and integration points: Directly implements the module layout implied by `Kconfig`. It integrates with Kbuild's `obj-$(CONFIG_...)` and per-module `foo-y`/`foo-$(CONFIG_...)` mechanisms.

Risks: Object composition must match symbol exports and Kconfig dependencies. If `enetc4_debugfs.o` references functions or types not present when `CONFIG_DEBUG_FS` is enabled, `nxp-enetc4.o` link fails. Conditional QoS and PCI IOV objects mean feature tests must use matching configs.

Test signals: Build matrix coverage across PF, VF, ENETC4, MDIO, PTP, QoS, PCI_IOV, and DEBUG_FS configurations. Module load tests should verify the module names advertised by Kconfig.
