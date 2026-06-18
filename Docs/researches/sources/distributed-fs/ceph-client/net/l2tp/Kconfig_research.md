# sources/distributed-fs/ceph-client/net/l2tp/Kconfig

## Purpose
Defines the Kconfig entry points for the kernel L2TP subsystem. The menu controls the core L2TP data-plane support, debugfs visibility, L2TPv3 support, L2TP-over-IP sockets, and L2TPv3 Ethernet pseudowires.

## Important symbols
- `L2TP` is a tristate depending on `INET` and selecting `NET_UDP_TUNNEL`; it builds the core data-plane support.
- `L2TP_DEBUGFS` is a tristate depending on `L2TP && DEBUG_FS`; it builds `l2tp_debugfs`.
- `L2TP_V3` is a bool depending on `L2TP`; it gates L2TPv3-only features.
- `L2TP_IP` is a tristate depending on `L2TP_V3`; it enables plain IP protocol 115 L2TPv3 sockets.
- `L2TP_ETH` is a tristate depending on `L2TP_V3`; it enables Ethernet pseudowire net devices.

## Control flow and build impact
This file does not execute code directly. It shapes compilation through `Makefile`: core support follows `CONFIG_L2TP`, netlink follows `CONFIG_L2TP_V3`, IP/IP6 follows `CONFIG_L2TP_IP`, Ethernet follows `CONFIG_L2TP_ETH`, and debugfs follows `CONFIG_L2TP_DEBUGFS`.

## State and persistence behavior
No runtime state is stored here. The configuration choices persist in the kernel build configuration and decide whether corresponding code is built in, modular, or omitted.

## Dependencies and integration points
The configuration text documents that the kernel handles only L2TP data packets while userspace handles the control protocol. `L2TP_IP` affects firewall/protocol expectations because plain L2TP-over-IP uses IP protocol number 115. `L2TP_ETH` exposes virtual Ethernet interfaces suitable for IP assignment or bridging.

## Risks and test signals
Risk is primarily configuration mismatch: enabling pseudowire userspace without `L2TP_V3`, using plain IP encapsulation without `L2TP_IP`, or expecting debugfs files without `DEBUG_FS` and `L2TP_DEBUGFS`. Test signals are generated config dependencies, module availability, and Kbuild selection of the expected objects.
