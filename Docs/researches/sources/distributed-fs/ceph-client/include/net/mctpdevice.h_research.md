<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mctpdevice.h -->
# sources/distributed-fs/ceph-client/include/net/mctpdevice.h

## Purpose
`mctpdevice.h` defines the MCTP per-netdevice wrapper and the binding operations used by physical MCTP transports.

## Important APIs, types, and functions
It defines `struct mctp_dev`, `struct mctp_netdev_ops`, `MCTP_INITIAL_DEFAULT_NET`, and functions for netdevice registration, lookup under RTNL or generic access, refcount hold/put, and device-flow key set/release.

## Control flow
A physical transport registers a netdevice as MCTP-capable with binding type and optional flow release callback. The MCTP core looks up the wrapper, manages local EID address arrays under RTNL plus `addrs_lock`, and associates `mctp_sk_key` flow state with the device.

## State and persistence
Runtime state includes the backing netdevice pointer, MCTP net ID, physical binding, local EID array, refcount, RCU teardown, and optional transport operations. No persistent state exists.

## Dependencies and integration points
It depends on list/types/refcount headers, netdevice state from `mctp.h`, and physical binding enums. It integrates transport drivers with the MCTP route/socket core.

## Risks and test signals
Risks include refcount/RCU lifetime errors, address-array mutation without RTNL or lock protection, flow release callback ordering, and unregister while keys still reference the device. Tests should cover register/unregister, local EID updates, key flow set/release, and netdev teardown.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mctpdevice.h` completely for this pass (58 lines, 1363 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mctpdevice.h -->
