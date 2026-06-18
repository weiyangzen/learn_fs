# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/Makefile

Purpose: Defines how the Hisilicon HNS RoCE hardware v2 driver is built and which source objects make up the module.

Important APIs/types/functions: The Makefile sets include paths into the HNS3 Ethernet driver directories and local source directory, then lists `hns-roce-hw-v2-objs`: main, command, PD, AH, HEM, MR, QP, CQ, allocation, doorbell, SRQ, restrack, debugfs, hardware v2, and bonding objects. `obj-$(CONFIG_INFINIBAND_HNS_HIP08)` binds the object aggregate to the Kconfig symbol.

Control flow: Kbuild compiles the listed objects into `hns-roce-hw-v2.o` when the config symbol is enabled. Include flags make HNS3 private headers visible to the RDMA driver.

State and persistence: Build metadata only. The object list is the persistence contract for which subsystems are linked into the module.

Dependencies and integration: Integrates directly with `drivers/net/ethernet/hisilicon/hns3`, `hns3pf`, and `hns3_common`. This reflects the driver coupling to HNAE3 handles, netdev state, and hardware mailbox/provider interfaces.

Risks: Missing object entries silently drop functionality at link time; stale include paths break cross-subsystem builds. Test signals include module build, modpost unresolved symbol checks, and verifying new features such as bonding/debugfs are included in the object aggregate.
