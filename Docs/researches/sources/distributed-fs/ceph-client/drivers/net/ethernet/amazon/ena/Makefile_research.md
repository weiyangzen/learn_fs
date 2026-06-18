# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/Makefile

Purpose: this Makefile builds the Elastic Network Adapter driver as a composite Kbuild object.

Important APIs, types, and functions: `obj-$(CONFIG_ENA_ETHERNET) += ena.o` declares the final object or module. `ena-y` combines `ena_netdev.o`, `ena_com.o`, `ena_eth_com.o`, `ena_ethtool.o`, `ena_xdp.o`, `ena_phc.o`, `ena_devlink.o`, and `ena_debugfs.o`.

Control flow: Kbuild links the component objects into `ena.o` when ENA is enabled. There is no runtime logic here.

State and persistence: persistent state is the component list and the build mode implied by `CONFIG_ENA_ETHERNET`.

Dependencies and integration points: the object list shows the driver architecture: PCI/netdev front end, communication/admin layer, Ethernet descriptor helpers, ethtool, XDP, PHC, devlink, and debugfs. These objects share headers such as `ena_com.h`, `ena_admin_defs.h`, `ena_eth_io_defs.h`, and `ena_netdev.h`.

Risks: any new translation unit for ENA features must be added here or it will not link. Removing optional-looking files such as `ena_debugfs.o` is not conditional here; the C file handles `CONFIG_DEBUG_FS` internally.

Test signals: module builds should emit one `ena` module containing all listed objects, and missing references between netdev, com, PHC, devlink, and debugfs code should be caught at link time.
