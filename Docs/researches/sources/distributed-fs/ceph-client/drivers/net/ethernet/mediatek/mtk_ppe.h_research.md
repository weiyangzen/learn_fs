<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe.h

## Purpose
`mtk_ppe.h` defines the software and hardware data model for MediaTek PPE flow offload. It describes FOE table sizes, IB1/IB2 bitfields, packet types, flow states, per-protocol FOE entry layouts, software flow tracking, MIB accounting structures, `struct mtk_ppe`, public PPE APIs, and the inline throttled `mtk_ppe_check_skb` entry point.

## Important APIs, Types, And Constants
The table size is fixed by `MTK_PPE_ENTRIES_SHIFT`, `MTK_PPE_ENTRIES`, and `MTK_PPE_HASH_MASK`. IB1 macros describe unbind and bind state bits, timestamp fields, VLAN layers, PPPoE, cache, TTL, packet type, UDP, and static flags, with separate v2 field positions. IB2 macros encode queue IDs, PSE QoS, destination ports, multicast, MIB counting, WDMA device/index/ring info, port aggregation, and DSCP. WINFO and AMSDU macros encode WED/WLAN metadata.

Hardware layouts include `struct mtk_foe_mac_info`, `mtk_foe_bridge`, `mtk_ipv4_tuple`, `mtk_foe_ipv4`, `mtk_foe_ipv4_dslite`, `mtk_foe_ipv6`, `mtk_foe_ipv6_6rd`, and the union `struct mtk_foe_entry`. `MTK_FOE_ENTRY_V1_SIZE`, `V2_SIZE`, and `V3_SIZE` identify SoC-specific entry sizes. Software state is represented by `struct mtk_flow_entry`, which can be an L4 flow, an L2 bridge rule, or an L2 subflow. `struct mtk_ppe` owns table pointers, DMA addresses, software hash buckets, L2 rhashtable, accounting table, and device metadata.

## Control Flow
The header exposes builder and lifecycle functions implemented in `mtk_ppe.c`. Offload code prepares a FOE entry, sets tuples and encapsulation metadata, maps it to an output port or WDMA target, commits it, clears it, queries idle time, and reads MIB deltas. `mtk_ppe_check_skb` is an inline guard around `__mtk_ppe_check_skb`: it validates PPE presence and hash range, rate-limits checks per hash to once per `HZ / 10`, records `jiffies`, and calls the heavy hardware/software reconciliation path.

## State And Persistence
The structures defined here persist in kernel memory for the lifetime of a PPE instance or offloaded flow. FOE entries are mirrored into coherent DMA memory consumed by hardware. `mtk_flow_entry.hash == 0xffff` means no active hardware hash is associated. L2 bridge flows use an rhashtable key ending at `mtk_foe_bridge.key_end`; subflows point back to their base flow and are linked for recursive cleanup. MIB accounting uses accumulated `u64` byte and packet counters.

## Dependencies And Integration Points
The header uses kernel bitfield and rhashtable APIs and is included by the Ethernet core, PPE implementation, debugfs, and offload code. It intentionally relies on `mtk_eth_soc.h` for version-aware helpers rather than embedding all SoC branching here. WED support depends on `mtk_foe_entry_set_wdma` and WINFO fields. TC flower offload depends on `struct mtk_flow_entry.cookie` and `node` for `eth->flow_table` lookup.

## Risks
The layout is hardware ABI. Padding, union offsets, and entry sizes must not drift from the hardware table format. Version-specific IB1/IB2 masks are easy to misuse if code bypasses helper functions. `mtk_ppe_check_skb` throttling prevents excessive hardware checks, but it also means repeated packets for a hash may not immediately bind a flow. Any extension to packet types or WED metadata must update debugfs, hash matching, and offload builders together.

## Test Signals
Compile coverage should include all configs with and without WED/debugfs. Runtime tests should verify that prepared FOE entries have expected byte layout for v1, v2, and v3 SoCs, unsupported flow types return errors, L2 subflow cleanup frees all children, and `mtk_ppe_check_skb` binds only after a relevant CPU reason supplies a valid hash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe.h -->
