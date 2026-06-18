# sources/distributed-fs/ceph-client/net/ethernet/eth.c

## Purpose
This file implements generic Ethernet netdevice helpers for the Linux network core. It supplies default Ethernet header operations, default `net_device` setup, Ethernet GRO offload glue, MAC address validation and assignment helpers, and platform/firmware/NVMEM MAC address discovery.

## Important APIs, Types, And Functions
Exported APIs include `eth_header()`, `eth_type_trans()`, `eth_get_headlen()`, `eth_header_parse()`, `eth_header_cache()`, `eth_header_cache_update()`, `eth_header_parse_protocol()`, `eth_prepare_mac_addr_change()`, `eth_commit_mac_addr_change()`, `eth_mac_addr()`, `eth_validate_addr()`, `ether_setup()`, `alloc_etherdev_mqs()`, `sysfs_format_mac()`, `eth_gro_receive()`, `eth_gro_complete()`, `eth_platform_get_mac_address()`, `platform_get_ethdev_address()`, `nvmem_get_mac_address()`, `fwnode_get_mac_address()`, `device_get_mac_address()`, and `device_get_ethdev_address()`. The file also defines `eth_header_ops` and registers `eth_packet_offload` at `fs_initcall()`.

## Control Flow
Transmit header creation pushes an `ethhdr`, fills protocol or length, chooses the source address from either caller input or `dev->dev_addr`, and either copies the destination, zeroes it for loopback/no-ARP devices, or returns `-ETH_HLEN` to request later address resolution. Receive protocol decoding resets the MAC header, pulls the Ethernet header, classifies packet type, handles DSA devices specially, and falls back to 802.2/802.3 heuristics for length-style frames. GRO receive validates common Ethernet headers across candidates, pulls the Ethernet header, then dispatches by protocol to registered packet offloads.

## State, Persistence, And Dependencies
The helpers mutate in-memory `sk_buff`, `hh_cache`, and `net_device` state only. MAC lookup is read-only against firmware properties and NVMEM cells, except wrappers that copy a successful address into `netdev->dev_addr`. Header-cache publication uses `smp_store_release()` for `hh->hh_len`. Dependencies include `netdevice`, ARP/neighbour cache, flow dissector, DSA, GRO, device properties, Open Firmware, NVMEM, and packet offload registration.

## Integration Points
Network drivers use `ether_setup()` and `alloc_etherdev_mqs()` for Ethernet defaults. Neighbour and routing paths use the header ops. Receive paths use `eth_type_trans()`. GRO uses this file through packet-offload registration for transparent Ethernet bridging/tunnel frames. Platform drivers use the MAC-address helpers to source stable hardware addresses from firmware, architecture hooks, or NVMEM.

## Risks
Header helpers assume adequate skb headroom and valid linear header access. Protocol classification preserves compatibility quirks such as IPX-over-802.3 and DSA tag handling, so changes can regress legacy or switch-tagged traffic. MAC changes deliberately do not update hardware filters for most real devices. Firmware MAC lookup must reject all-zero or malformed addresses and must free NVMEM buffers on every path.

## Test Signals
Useful signals include Ethernet transmit header construction tests, receive protocol classification for Ethernet II, 802.2, 802.3, DSA, and short frames, neighbour header-cache concurrency tests, GRO aggregation/flush behavior, invalid/live MAC address change errors, and firmware/NVMEM MAC lookup fallbacks.
