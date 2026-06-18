# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/Makefile

Purpose: this Makefile wires the Chelsio T4/T5/T6 SR-IOV Virtual Function Ethernet driver into the kernel build. When `CONFIG_CHELSIO_T4VF` is enabled, it builds one module or built-in object named `cxgb4vf` from the VF driver's main, hardware, and SGE implementation files.

Important build variables: `obj-$(CONFIG_CHELSIO_T4VF) += cxgb4vf.o` ties the aggregate driver object to Kconfig. `cxgb4vf-objs := cxgb4vf_main.o t4vf_hw.o sge.o` defines the linked components: PCI/netdev/debugfs/ethtool logic in `cxgb4vf_main.o`, firmware and hardware mailbox helpers in `t4vf_hw.o`, and queue/datapath logic in `sge.o`.

Control flow and integration: there is no runtime flow in the Makefile. Build flow is symbol driven: enabling the Kconfig symbol compiles the three objects and links them into a single driver. The resulting driver registers a PCI driver whose device IDs are included from the PF driver's PCI ID table and whose module metadata is defined in `cxgb4vf_main.c`.

State and persistence: persistent state is build output and module metadata generated from the selected configuration. There is no runtime state in this file. The aggregate object boundary matters because symbols can remain file-local where appropriate while still linking into one driver module.

Dependencies and integration points: this file depends on the surrounding kernel build system and the `CONFIG_CHELSIO_T4VF` Kconfig symbol. The objects it links depend on shared Chelsio headers from `../cxgb4/`, Linux PCI, netdevice, ethtool, debugfs, DMA mapping, and firmware mailbox infrastructure.

Risks: omitting one object breaks link-time symbol resolution or removes major functionality. For example, dropping `sge.o` would leave transmit/receive queue functions unresolved, while dropping `t4vf_hw.o` would remove firmware command helpers needed by probe and configuration. A mismatch between Kconfig and Makefile names would silently prevent the driver from building in expected configurations.

Test signals: `make M=drivers/net/ethernet/chelsio/cxgb4vf`, `allmodconfig`, and `CONFIG_CHELSIO_T4VF=m/y` builds should produce a single `cxgb4vf` module or built-in object. `modinfo cxgb4vf` should show metadata and PCI aliases from `cxgb4vf_main.c` and the included Chelsio PCI ID table.
