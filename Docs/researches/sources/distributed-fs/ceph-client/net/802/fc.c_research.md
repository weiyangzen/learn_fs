<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/fc.c -->
# sources/distributed-fs/ceph-client/net/802/fc.c

This file provides generic Fibre Channel net-device setup and header construction. It exports `alloc_fcdev()` for drivers that need a preconfigured FC-style `struct net_device`.

`fc_header()` is the key header operation. It pushes a Fibre Channel header and, for IPv4 or ARP, also pushes an 802.2 SNAP-style `struct fcllc` header because IPv4 can call `dev->hard_header` directly. It fills source from the provided address or device address and either copies the destination or returns a negative header length to signal unresolved destination. `fc_setup()` configures header ops, ARPHRD type, MTU, address length, queue length, broadcast flag, and all-ones broadcast address. `alloc_fcdev()` wraps `alloc_netdev()` with this setup.

State is per-net-device configuration only; there is no module-global mutable state. Dependencies are FC device header definitions, skb header push semantics, ARP/header-ops integration, and Ethernet protocol constants.

Risks include insufficient skb headroom, wrong SNAP insertion for non-IP/ARP protocols, and driver assumptions around FC address length and MTU. Tests should exercise header creation with and without destination/source addresses, IPv4/ARP SNAP formatting, non-IP header length, and basic device allocation defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/fc.c -->
