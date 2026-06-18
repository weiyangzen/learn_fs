# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/filter.h

## Purpose
`filter.h` defines the NIC-independent hardware filter specification API used by Falcon-architecture and later Solarflare filter implementations. It models what a packet filter matches, its priority, whether it applies to RX or TX, and the queue/RSS behavior to apply when a packet matches.

## Important APIs, Types, And Functions
`enum ef4_filter_match_flags` describes matchable fields: remote/local IP host, remote/local MAC, remote/local ports, EtherType, inner/outer VLAN ID, IP protocol, and local MAC I/G bit for default unicast or multicast filters. `enum ef4_filter_priority` establishes replacement policy from hints through required filters. `enum ef4_filter_flags` records RX RSS, RX scatter, automatic-filter override, and direction bits. `struct ef4_filter_spec` is a compact 64-byte specification containing bitfield metadata, RSS context, DMA queue ID, VLANs, MACs, EtherType, protocol, IPv4/IPv6-sized address arrays, and ports.

The inline constructors `ef4_filter_init_rx()` and `ef4_filter_init_tx()` zero the structure, set direction, priority, default RSS context, and queue. Setter helpers build common match forms: `ef4_filter_set_ipv4_local()`, `ef4_filter_set_ipv4_full()`, `ef4_filter_set_eth_local()`, `ef4_filter_set_uc_def()`, and `ef4_filter_set_mc_def()`.

## Control Flow
Callers must initialize a spec with the RX or TX constructor before setting match fields. Each setter mutates `match_flags` and the corresponding fields, returning `0` unless the Ethernet-local setter is asked to match neither VLAN nor MAC, in which case it returns `-EINVAL`. Hardware-specific filter operations later validate and translate the abstract spec into Falcon or Siena filter-table entries.

## State And Persistence
The header itself keeps no state. `ef4_filter_spec` values are transient request objects passed into the NIC type's `filter_insert`, `filter_remove_safe`, `filter_get_safe`, RFS, and clear/count/list operations. Once accepted, the persistent state lives in `efx->filter_state` and in hardware filter tables.

## Dependencies And Integration Points
The file depends on Linux type definitions, Ethernet address helpers, byte-order helpers, and `ETH_ALEN`/`ETH_P_IP`. It is included by `net_driver.h`, making the spec type part of the central `struct ef4_nic_type` filter operation contract. It integrates with RX queue selection, RSS contexts, accelerated RFS, automatic MAC-list filters, user-required filters, and TX source filtering on Siena-class hardware.

## Risks
The main correctness risk is creating a spec whose `match_flags` combination is unsupported by the active NIC type. The comments explicitly note that Falcon supports only a narrower subset than Siena or later hardware. Queue IDs are 12-bit fields, and `EF4_FILTER_RX_DMAQ_ID_DROP` uses the all-ones hardware value, so callers must avoid accidental queue/drop confusion. Byte order is also important: VLANs, EtherType, IP addresses, and ports are stored in network order.

## Test Signals
Signals include successful insertion/removal by hardware-specific filter code, RX packet steering to expected queues, drop-filter behavior, RSS distribution for RSS-marked filters, multicast/unicast default filter behavior, RFS acceleration expiry, and negative tests for invalid Ethernet-local filters or unsupported match combinations.
