# sources/distributed-fs/ceph-client/include/rdma/ib_sysfs.h

Purpose: defines a typed sysfs attribute wrapper for RDMA device port attributes and helper macros to declare read/write/admin/read-only/write-only attributes.

Important APIs and types: `struct ib_port_attribute` embeds `struct attribute` and provides port-aware `show()` and `store()` callbacks receiving `ib_device`, port number, the attribute object, and buffer/count. Macros `IB_PORT_ATTR_RW`, `IB_PORT_ATTR_ADMIN_RW`, `IB_PORT_ATTR_RO`, and `IB_PORT_ATTR_WO` declare attributes with appropriate mode. `ib_port_sysfs_get_ibdev_kobj()` maps a sysfs kobject back to `ib_device` and port number.

Control flow: RDMA core or drivers declare port attributes, sysfs invokes generic wrappers that recover the device/port from kobject, and then dispatch to the port-aware callbacks. Admin attributes restrict mode to owner read/write.

State and persistence: no persistent state is owned here. Sysfs files expose live RDMA device/port state or accept live configuration writes implemented by callbacks.

Dependencies and integration points: depends on Linux sysfs/kobject infrastructure and `struct ib_device`. It integrates RDMA port objects with the device model and sysfs user interfaces.

Risks and test signals: risks include kobject-to-port lookup lifetime races, overly permissive attribute mode, callback buffer length mistakes, and accessing removed devices. Test sysfs read/write for each port, admin mode permissions, device removal while sysfs file is open, invalid kobject lookup, and callback error propagation.
