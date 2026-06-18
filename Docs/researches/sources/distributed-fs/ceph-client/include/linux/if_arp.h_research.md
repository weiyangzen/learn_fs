# `sources/distributed-fs/ceph-client/include/linux/if_arp.h`

Purpose: kernel ARP helpers layered over the UAPI ARP header, giving network code a standard way to locate ARP headers, compute ARP header lengths, and decide whether a netdevice transmits a MAC header.

Important APIs/types/functions: `arp_hdr`, `arp_hdr_len`, and `dev_is_mac_header_xmit`. `arp_hdr_len` special-cases FireWire ARP address sizing and otherwise uses two hardware addresses plus two IPv4 addresses.

Control flow and state: stateless inline helpers over `sk_buff` and `net_device`. `dev_is_mac_header_xmit` switches on `dev->type` and treats tunnel/raw/PPP-like devices as L3 transmit devices.

Dependencies/integration: depends on `linux/skbuff.h`, `net_device`, and UAPI `if_arp.h`. Used by ARP, BPF redirect, traffic control mirred, and device transmit paths.

Risks: wrong `dev->type` classification changes whether callers prepend L2 headers; `arp_hdr_len` assumes IPv4 ARP address structure and device `addr_len` validity; FireWire behavior depends on `CONFIG_FIREWIRE_NET`.

Test signals: ARP packet construction on Ethernet and FireWire, BPF redirect to PPP/tunnel/raw devices, and compile coverage with and without FireWire support.
