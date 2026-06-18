<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_net.h -->
# sources/distributed-fs/ceph-client/include/linux/of_net.h

## Purpose
This header declares OF network-device helpers for PHY interface mode, MAC address discovery, NVMEM MAC fallback, and netdev lookup by node.

## Important APIs, types, and functions
With `CONFIG_OF && CONFIG_NET`, it exports `of_get_phy_mode()`, `of_get_mac_address()`, `of_get_mac_address_nvmem()`, `of_get_ethdev_address()`, and `of_find_net_device_by_node()`. Stubs return `-ENODEV` or `NULL`.

## Control flow
Network drivers read DT properties to choose `phy_interface_t`, obtain a MAC address from standard properties or NVMEM, copy it to a `net_device`, and optionally locate an existing netdev tied to a DT node.

## State and persistence
The header stores no state. MAC addresses copied into `net_device` persist as device configuration; NVMEM state is external.

## Dependencies and integration points
It depends on PHY interface definitions, OF, `struct net_device`, NVMEM-backed address lookup, and network device registration.

## Risks and test signals
Risks include invalid or all-zero MAC handling, PHY mode string mismatch, NVMEM lookup ordering, stale netdev-by-node references, and disabled NET/OF stubs. Test DT MAC property variants, NVMEM MAC cells, PHY mode parsing, netdev lookup ref/lifetime behavior, and non-OF network builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_net.h -->
