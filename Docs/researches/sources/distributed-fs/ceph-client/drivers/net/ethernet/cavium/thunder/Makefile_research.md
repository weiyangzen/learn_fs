# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/Makefile

Purpose: Build glue for Cavium Thunder Ethernet drivers.

Important APIs, types, and functions: Kbuild rules include `thunder_xcv.o` under `CONFIG_THUNDER_NIC_RGX`, `thunder_bgx.o` under `CONFIG_THUNDER_NIC_BGX`, `nicpf.o` under `CONFIG_THUNDER_NIC_PF`, and `nicvf.o` under `CONFIG_THUNDER_NIC_VF`. Composite objects map `nicpf-y := nic_main.o` and `nicvf-y := nicvf_main.o nicvf_queues.o nicvf_ethtool.o`.

Control flow: Enabling PF builds `nic_main.c`; enabling VF links main, queues, and ethtool support into the VF driver object.

State and persistence: No runtime state. It controls build composition.

Dependencies and integration: Depends on Thunder Kconfig symbols and source files in the same directory. It expresses the separation between PF mailbox/global hardware driver and VF netdev/queue/ethtool driver.

Risks: Omitting `nicvf_ethtool.o` removes user-visible diagnostics and configuration. PF/VF symbols can be built independently, but runtime SR-IOV requires both sides where VFs are used.

Test signals: Matrix builds for each `CONFIG_THUNDER_NIC_*` symbol, module object composition, and link success after symbol changes.
