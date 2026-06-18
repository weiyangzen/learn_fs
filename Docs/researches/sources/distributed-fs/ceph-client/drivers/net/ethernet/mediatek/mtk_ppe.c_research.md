<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe.c

## Purpose
`mtk_ppe.c` implements the MediaTek Packet Processing Engine core. It programs FOE table entries, manages the hardware flow cache, maintains software tracking for bound and pending flows, supports L2 bridge offload subflows, reads optional MIB accounting, and starts/stops the PPE block. It is the bridge between TC/offload request construction and hardware NAT/route/bridge execution.

## Important APIs And Functions
Low-level helpers `ppe_w32`, `ppe_r32`, `ppe_m32`, `ppe_set`, and `ppe_clear` wrap PPE MMIO. `mtk_ppe_wait_busy` and `mtk_ppe_mib_wait_busy` poll hardware busy bits. `mtk_mib_entry_read` serializes MIB reads and handles v3 64-bit counters versus older split-width counters. FOE construction APIs include `mtk_foe_entry_prepare`, `mtk_foe_entry_set_pse_port`, `mtk_foe_entry_set_ipv4_tuple`, `mtk_foe_entry_set_ipv6_tuple`, `mtk_foe_entry_set_dsa`, `mtk_foe_entry_set_vlan`, `mtk_foe_entry_set_pppoe`, `mtk_foe_entry_set_wdma`, and `mtk_foe_entry_set_queue`. Lifecycle APIs are `mtk_foe_entry_commit`, `mtk_foe_entry_clear`, `mtk_foe_entry_idle_time`, `mtk_ppe_prepare_reset`, `mtk_foe_entry_get_mib`, `mtk_ppe_init`, `mtk_ppe_deinit`, `mtk_ppe_update_mtu`, `mtk_ppe_start`, and `mtk_ppe_stop`.

## Control Flow
Flow entries are prepared in software, committed into a hash bucket, and only written to hardware once a matching unbound packet reaches the CPU. `mtk_foe_entry_commit` computes the PPE hash for routed/NAT flows and links the `mtk_flow_entry` into `ppe->foe_flow[hash / hash_offset]`; L2 bridge flows are stored in `ppe->l2_flows` by destination/source/VLAN key. `__mtk_ppe_check_skb` is called on selected CPU packets. It checks whether the hardware entry is still unbound, matches pending software entries against the hardware-discovered tuple, writes a bound FOE entry with `__mtk_foe_entry_commit`, or builds an L2 subflow for bridge entries.

`__mtk_foe_entry_commit` writes all FOE data before `ib1`, uses write barriers before ownership/state visibility, stamps the current PPE timestamp, enables MIB counting when available, and clears the PPE cache. Clearing invalidates the hardware entry, removes software nodes, recursively removes L2 subflows, clears accounting totals, and resets the entry hash. `mtk_flow_entry_update` refreshes software timestamps and detects hardware replacement. `mtk_ppe_start` initializes the FOE table, programs base addresses, age timers, bind limits, flow protocol enable bits, cache, default CPU ports, and optional accounting tables before enabling `MTK_PPE_GLO_CFG_EN`. `mtk_ppe_stop` invalidates all FOE entries, disables cache and aging, waits idle, and disables the engine.

## State And Persistence
`struct mtk_ppe` stores the MMIO base, coherent FOE table, optional MIB table, software accounting table, pending flow hlist buckets, L2 rhashtable, per-entry check timestamps, and SoC/version metadata. Hardware state persists while the PPE is enabled in the FOE and MIB tables. Software flow state persists until TC destroy, reset, stop, or replacement. A global `ppe_lock` protects flow lists, hardware entry mutation, and L2 subflow cleanup.

## Dependencies And Integration Points
This file depends on `mtk_eth_soc.h` for SoC version helpers and PSE port definitions, `mtk_ppe.h` for FOE layouts, and `mtk_ppe_regs.h` for register definitions. It integrates with TC offload through `mtk_ppe_offload.c`, with RX CPU packet handling through `mtk_ppe_check_skb`, with WED through WDMA-specific FOE fields, with DSA metadata for bridge VLAN/tag handling, and with debugfs via `mtk_ppe_debugfs_init`.

## Risks
Important risks are incorrect hash calculation, stale hardware cache after FOE edits, missing barriers before setting `ib1`, inconsistent version-specific bitfields, and cleanup races between hardware-learned entries and software destroy. L2 offload is more delicate because one logical bridge rule can create multiple hardware subflows that must be recursively cleared. Allocation error paths in `mtk_ppe_init` return `NULL` in several places after partial resource setup, so callers must tolerate missing PPEs. MIB accounting is read-clear based and accumulates into software totals; bad index or concurrent clear can skew stats.

## Test Signals
Exercise IPv4 NAT, IPv4 route, IPv6 3T/5T, bridge, VLAN, PPPoE, DSA, WDMA/WED, and queue-selection offloads. Verify FOE entries appear in debugfs, packet/byte counters increase when accounting is enabled, idle time updates, flows age out or destroy cleanly, PPE stop leaves no bound entries, and reset preparation reaches idle. Traffic should continue through CPU fallback for unsupported flow types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe.c -->
