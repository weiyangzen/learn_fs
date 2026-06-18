# sources/distributed-fs/ceph-client/include/linux/net/intel/iidc_rdma.h

Purpose: declares the common Intel IIDC RDMA auxiliary-device interface shared between LAN PCI drivers and RDMA auxiliary drivers.

Important APIs and types: `enum iidc_rdma_event_type` defines MTU, traffic-class, reset warning, and critical-error event bits. `struct iidc_rdma_event` carries a bitmap of event types plus a register value. Reset types distinguish function and device reset, while protocol bits identify iWARP and RoCEv2. `struct iidc_rdma_core_dev_info` carries the PCI device, auxiliary device, active RDMA protocol, and driver-private IIDC data. `struct iidc_rdma_core_auxiliary_dev` embeds an auxiliary device with core info. `struct iidc_rdma_core_auxiliary_drv` embeds an auxiliary driver and an event handler.

Control flow: the LAN core allocates/populates core device info and auxiliary devices; the RDMA auxiliary driver binds through auxiliary bus registration and receives event callbacks for MTU/TC changes and reset/error conditions. Driver-specific headers extend the common core info with LAN-specific operations.

State and persistence: state is live device association and selected RDMA protocol. There is no durable storage; resets and events describe transient hardware/software state.

Dependencies and integration points: depends on auxiliary bus, PCI/device/netdevice headers, Ethernet constants, kernel bitmap helpers, and DSCP definitions. It forms the common IIDC handshake between Intel LAN drivers and RDMA providers.

Risks and test signals: risks include event bitmap width drift, stale auxiliary device lifetime, mismatched active protocol, null private data expectations, and event ordering around MTU/TC before/after notifications. Test auxiliary probe/remove, protocol selection, before/after MTU and TC events, warning and critical reset paths, and multi-protocol compile coverage.
