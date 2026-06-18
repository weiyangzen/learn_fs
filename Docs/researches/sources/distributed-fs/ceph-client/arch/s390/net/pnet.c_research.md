## sources/distributed-fs/ceph-client/arch/s390/net/pnet.c

Purpose: extracts s390 Physical Network Identifier values from CCW group or PCI network devices so upper layers can identify ports attached to the same physical network.

Important APIs, types, and functions: `pnet_id_by_dev_port()` is exported GPL. Internal `pnet_ids_by_device()` fills a 64-byte utility string buffer. Constants define four 16-byte PNET IDs.

Control flow: callers pass a device and port. The code rejects null devices or ports beyond four. For CCW group devices, it reads the utility string from the first child ccw device, converts EBCDIC to ASCII, and copies all PNET IDs. For PCI devices, it copies `zdev->util_str` and converts it. `pnet_id_by_dev_port()` returns the selected nonzero 16-byte ID or `-ENOENT`.

State and persistence: no persistent state. Stack buffers hold copied PNET IDs. Device utility strings are read from CCW or zPCI device state.

Dependencies and integration points: depends on ccwgroup/ccwdev helpers, zPCI device conversion, EBCDIC conversion, and network code configured with `CONFIG_HAVE_PNETID`.

Risks: CCW groups assume the first bundled subchannel utility string represents the group. Empty all-zero IDs are treated as absent. Device type checks must match the actual parent devices passed by networking drivers.

Test signals: CCW group and PCI network devices with populated utility strings, empty utility strings returning `-ENOENT`, invalid port indexes, non-supported device types returning no ID, and ASCII conversion correctness.
