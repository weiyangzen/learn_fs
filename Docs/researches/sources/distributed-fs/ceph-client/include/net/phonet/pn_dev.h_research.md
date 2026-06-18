# sources/distributed-fs/ceph-client/include/net/phonet/pn_dev.h

Purpose: declares Phonet network-device address and route management structures and functions.

Important APIs and types: `struct phonet_device_list` stores netns device list and lock. `struct phonet_device` links a net_device, 64-address bitmap, and RCU head. APIs initialize/exit device and netlink support, add/delete/get/lookup addresses, notify address changes, add/delete routes, notify route changes, and find route output devices under RCU or refcounted lookup.

Control flow: netdevice/netlink operations add addresses and routes; packet output uses destination address lookup to choose a Phonet device; notifications report RTM-style address/route events.

State and persistence: state is netns-local runtime lists, address bitmaps, and routing mappings. It is not persisted by the header.

Dependencies and integration points: depends on net_device, net namespaces, spinlocks, RCU, seq_file proc operations, and Phonet netlink.

Risks and test signals: risks include address bitmap bounds, RCU use-after-free on devices, route lookup after device removal, and notification mismatches. Test address add/delete/lookup, route add/delete/output, netns teardown, device unregister, and proc seq iteration.
