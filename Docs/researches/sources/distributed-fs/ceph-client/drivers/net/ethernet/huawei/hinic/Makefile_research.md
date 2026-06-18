# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/Makefile

Defines the composite `hinic.o` module. `hinic-y` includes main netdev, TX/RX, port, hardware device/IO/QP/CMDQ/WQ/MGMT/API/EQ/IF/mbox/SR-IOV, common helpers, ethtool, devlink, and debugfs objects.

No runtime state is created, but build composition controls which symbols/features exist in the driver. The researched objects `hinic_common.o`, `hinic_ethtool.o`, `hinic_devlink.o`, `hinic_hw_api_cmd.o`, and `hinic_debugfs.o` are built here. Risks are unresolved symbols or missing features if object lists drift. Test with `CONFIG_HINIC=m/y`.
