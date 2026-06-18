<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inetdevice.h -->
# sources/distributed-fs/ceph-client/include/linux/inetdevice.h

Purpose: Defines IPv4 per-device state, per-interface addresses, devconf helpers, and lookup/notifier APIs.

Important APIs/types/functions: `struct ipv4_devconf` stores sysctl data and explicit state bits. `struct in_device` links a net_device to IPv4 addresses, multicast lists/hash, IGMP timers/state, ARP parameters, devconf, refcount, and RCU head. `struct in_ifaddr` describes IPv4 interface addresses, masks, broadcast, scope, flags, lifetimes, labels, and timestamps. Helpers read/set devconf, combine all/per-device policy, iterate addresses under RTNL/RCU, look up devices/addresses, compute masks, and manage refcounts.

Control flow: Device setup creates `in_device`; address configuration mutates `ifa_list`; routing, ARP, multicast, and ioctls read devconf/address state under RCU or RTNL.

State/persistence: Per-netdevice IPv4 state persists while the network device is alive; address lifetimes and multicast timers update over time.

Dependencies/integration: Depends on netdevice, RCU, timers, sysctl, rtnetlink, neighbor, multicast, and notifier chains.

Risks: Locking context matters for address iteration and `ip_ptr`; missing refcount/RCU discipline can cause use-after-free.

Test signals: IPv4 address add/delete, ioctl gifconf, notifier callbacks, multicast timers, devconf sysctl changes, RCU lookups, and mask validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inetdevice.h -->
