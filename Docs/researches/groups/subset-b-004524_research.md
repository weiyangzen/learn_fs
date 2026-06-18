# Research Group: subset-b-004524

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_eth_soc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_eth_soc.h

## Purpose
`mtk_eth_soc.h` is the shared contract for the MediaTek SoC Ethernet driver family. It defines register offsets, descriptor layouts, SoC capability bits, per-SoC data, core device state, MAC state, and exported helper prototypes used by the frame engine, GMAC, QDMA/PDMA, PPE flow offload, WED, phylink, XDP, and stats code. This header is not a passive constant bucket: the version-aware inline helpers here decide how PPE FOE bitfields are interpreted on NETSYS v1 versus v2/v3 hardware.

## Important APIs, Types, And Constants
The first major block describes hardware limits and register layouts: QDMA queue sizes, RX/TX DMA buffer sizes, LRO parameters, frame-engine interrupt bits, GDMA controls, PSE queue registers, PDMA/QDMA control bits, MAC registers, SGMII/TRGMII/XGMII controls, reset bits, and PSE port IDs. The descriptor structs `mtk_rx_dma`, `mtk_rx_dma_v2`, `mtk_tx_dma`, and `mtk_tx_dma_v2` encode the 4-word and 8-word DMA formats consumed by the data path. `TX_DMA_*` and `RX_DMA_*` macros expose owner, length, checksum, VLAN, port, PPE reason, and 64-bit address fields.

The central state structures are `struct mtk_eth`, `struct mtk_mac`, `struct mtk_tx_ring`, `struct mtk_rx_ring`, `struct mtk_hw_stats`, and `struct mtk_soc_data`. `mtk_soc_data` carries register map selection, capability flags, required clocks, offload/PPE versioning, hash offset, FOE entry size, DMA descriptor metadata, accounting support, and feature flags. `mtk_eth` aggregates MMIO, DMA device selection, netdev/MAC arrays, IRQs, regmaps, phylink PCS, rings, NAPI instances, DIM counters, DSA metadata, PPE instances, the flow rhashtable, XDP program pointer, and reset-monitor state. `mtk_mac` binds a netdev to a hardware MAC and stores phylink, stats, HWR LRO IPs, and device notifier state.

## Control Flow And Version Selection
The header's inline helpers are used throughout PPE and WED code to choose correct bitfields. `mtk_is_netsys_v1`, `mtk_is_netsys_v2_or_greater`, and `mtk_is_netsys_v3_or_greater` branch on `eth->soc->version`. `mtk_foe_get_entry` computes a FOE entry pointer from `ppe->foe_table`, the hash index, and `soc->foe_entry_size`, making correct SoC metadata mandatory. The `mtk_get_ib1_*`, `mtk_prep_ib1_vlan_layer`, `mtk_get_ib1_pkt_type`, and `mtk_get_ib2_multicast_mask` helpers abstract the incompatible FOE bitfield positions between v1 and later NETSYS layouts. `mtk_interface_mode_is_xgmii` limits internal/USXGMII/10G/5G handling to NETSYS v3 or newer.

## State And Persistence
All state described here is kernel runtime state. Persistent hardware state is represented through register offsets and DMA descriptors, but the header itself stores no data. `mtk_eth` owns long-lived driver allocations for rings, DMA scratch areas, clock handles, PPE objects, and the global flow table for TC flower offload. `mtk_hw_stats` accumulates hardware counters under synchronization. `mtk_rx_ring` keeps page-pool and XDP receive queue state; `mtk_tx_ring` tracks DMA descriptors and free counts. Reset state is tracked in `mtk_eth.reset` with delayed work and hang counters.

## Dependencies And Integration Points
The header depends on kernel DMA, netdevice, phylink, page pool, DIM, rhashtable, BPF/XDP, and bitfield APIs. It includes `mtk_ppe.h`, creating a tight dependency between the Ethernet core and flow offload data formats. Exported prototypes connect to implementation files for stats, register IO, GMAC path setup, TC setup, offload initialization, flow offload commands, flow cleanup, and DMA device switching. WED code depends on `struct mtk_eth`, PPE arrays, `mtk_eth_set_dma_device`, SoC version/capability helpers, PSE port constants, and descriptor address helpers.

## Risks
The dominant risk is version drift: a wrong `soc->version`, `offload_version`, `hash_offset`, or `foe_entry_size` causes PPE hashes, FOE entries, and DMA descriptors to be interpreted incorrectly. DMA length and 64-bit address macros are used directly in hot paths and must match descriptor layout. Capability bit combinations define valid mux/path setups, so new SoCs must update these carefully. Since `mtk_eth` contains shared data used by NAPI, reset work, offload callbacks, and WED attach/detach, locking and lifetime rules in implementation files must align with this structure.

## Test Signals
Useful signals include successful probe for each SoC match data, correct clock acquisition from `required_clks`, traffic through every GMAC path in the capability set, TX/RX checksum/TSO/VLAN feature tests, XDP pass/drop/tx/redirect counters, phylink mode changes, TC flower offload add/delete/stats, WED attach on supported SoCs, and reset-monitor recovery. Hardware register dumps and ethtool stats should reflect descriptor counters without DMA hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_eth_soc.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_debugfs.c

## Purpose
`mtk_ppe_debugfs.c` provides debugfs visibility into PPE FOE entries. It creates per-PPE debugfs directories with `entries` and `bind` files and formats active FOE table entries, including state, packet type, original/new tuples, L2 header rewrite fields, VLAN tags, IB words, and optional MIB packet/byte counters.

## Important APIs And Functions
`mtk_foe_entry_state_str` and `mtk_foe_pkt_type_str` translate hardware state and packet type enums to compact strings. `mtk_print_addr` and `mtk_print_addr_info` print IPv4/IPv6 endpoint data. `mtk_ppe_debugfs_foe_show` is the main seq-file renderer; `mtk_ppe_debugfs_foe_all_show` and `mtk_ppe_debugfs_foe_bind_show` select all non-invalid entries or only bound entries. `mtk_ppe_debugfs_init` creates `ppe%d/entries` and `ppe%d/bind`.

## Control Flow
When a debugfs file is read, the renderer iterates all `MTK_PPE_ENTRIES`, skips invalid entries, optionally filters to `MTK_FOE_STATE_BIND`, reads accounting via `mtk_foe_entry_get_mib`, decodes packet type using version-aware helpers, selects IPv4 or IPv6 tuple storage, prints original and translated addresses, selects the L2/IB2 storage based on packet type, reconstructs source and destination MAC addresses from split fields, and emits one line per entry.

## State And Persistence
The file does not own flow state. It reads live FOE DMA memory and may read-clear MIB hardware counters through `mtk_foe_entry_get_mib`, which also accumulates software totals. The debugfs directory name is persisted in `ppe->dirname`; the actual entries reflect current hardware/software state and can change while being read.

## Dependencies And Integration Points
It depends on debugfs, seq_file, IPv6 helpers, `mtk_eth_soc.h`, and PPE APIs. It is initialized from `mtk_ppe_init` after the PPE table and accounting structures are allocated. It uses the same version-aware packet type helpers as the core PPE code, avoiding direct NETSYS layout assumptions for `ib1`.

## Risks
Reading `entries` can be expensive because it scans all 16K FOE entries and may touch MIB hardware for each non-invalid entry. Accounting reads may alter counters if MIB read-clear is enabled, so debugfs reads are observability with side effects. The renderer only has packet type strings for routable/tunnel types and prints bridge types as `UNKNOWN`, which can confuse diagnostics for L2 offload. It reads live hardware without taking `ppe_lock`, so entries can change while being formatted.

## Test Signals
With debugfs enabled, verify `ppe0/entries` and `ppe0/bind` exist, invalid entries are skipped, bound flow lines show tuple/MAC/VLAN/IB data, MIB counters grow across traffic, and repeated reads do not crash while flows are added or removed. Test IPv4, IPv6, bridge, VLAN, PPPoE, DSA, and WED-directed entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_offload.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_offload.c

## Purpose
`mtk_ppe_offload.c` connects Linux TC flower flow offload to MediaTek PPE FOE programming. It parses `flow_cls_offload` rules, validates supported match/action combinations, converts matches and actions into `mtk_foe_entry` data, chooses an output PSE/DSA/WED path, manages the global flow rhashtable keyed by TC cookie, and reports offload stats.

## Important APIs And Functions
`struct mtk_flow_data` is a temporary parser result containing Ethernet addresses, IPv4/IPv6 endpoints, ports, input VLAN, pushed VLANs, and PPPoE session data. Helper functions parse or apply action data: `mtk_flow_offload_mangle_eth`, `mtk_flow_mangle_ports`, `mtk_flow_mangle_ipv4`, `mtk_flow_set_ipv4_addr`, and `mtk_flow_set_ipv6_addr`. `mtk_flow_get_wdma_info` resolves a forwarding path ending in `DEV_PATH_MTK_WDMA`; `mtk_flow_get_dsa_port` detects MediaTek DSA conduit/port data. `mtk_flow_set_output_device` chooses PSE port, queue, DSA tag, or WDMA metadata. Public APIs are `mtk_flow_offload_cmd`, `mtk_eth_setup_tc`, and `mtk_eth_offload_init`.

## Control Flow
`mtk_flow_offload_cmd` serializes replace, destroy, and stats under `mtk_flow_offload_mutex`. Replace first rejects duplicate cookies. It requires meta, control, and basic dissector keys; NETSYS v2 or newer can select a PPE index based on ingress netdev `mac->ppe_idx`. Address type chooses bridge, IPv4 HNAPT, or IPv6 5T. It parses flower actions in two passes: the first captures Ethernet mangle, redirect device, VLAN push/pop, PPPoE push, and checksum; the second applies IP and port mangles after original tuple setup. It then prepares a FOE entry, fills tuple fields, applies VLAN/PPPoE metadata, resolves output device and WED index, optionally enables WED offload, allocates `mtk_flow_entry`, commits it to the PPE, and inserts it into `eth->flow_table`.

Destroy looks up the cookie, clears the PPE entry, removes it from the flow rhashtable, decrements WED flow state if used, and frees the entry. Stats refresh idle time through `mtk_foe_entry_idle_time`, reports `lastused`, and adds MIB deltas when the flow has a bound hardware hash. TC block setup registers or unregisters flow block callbacks for ingress clsact binders.

## State And Persistence
The persistent software state is `eth->flow_table`, keyed by `f->cookie`, plus the `mtk_flow_entry` linked into PPE software buckets or L2 tables. Each entry records PPE index and WED index for later stats/destroy. WED flow reference state is maintained separately by `mtk_wed_flow_add` and `mtk_wed_flow_remove`. No flow survives driver teardown; hardware state is cleared by PPE lifecycle and destroy paths.

## Dependencies And Integration Points
This file depends on flow dissector, TC flower, DSA, rhashtable, `mtk_eth_soc.h`, and `mtk_wed.h`. It is called from Ethernet netdev TC setup and from WED TC setup. It programs FOE entries through `mtk_ppe.c` APIs and delegates Wi-Fi path information through `dev_fill_forward_path` and WED path data. It uses netdev arrays in `struct mtk_eth` to map redirect devices to PSE ports.

## Risks
Supported flow coverage is deliberately narrow; unsupported actions must reliably return `-EOPNOTSUPP` so software fallback remains correct. Error cleanup is critical: if insertion fails after WED enable or PPE commit, the code clears the entry, frees it, and removes the WED flow. A notable bug risk is reference underflow in WED flow removal if callers mismatch add/remove. Meta ingress selection compares netdev ops in `mtk_flow_is_valid_idev`, which is broad and assumes MediaTek netdevs share ops. IPv6 mangle support is absent; bridge offload rejects mangle and ports. WDMA forwarding depends on external WLAN path data being valid.

## Test Signals
Use `tc flower` add/delete/stats for IPv4 NAT, IPv6 route, pure L2 bridge, VLAN push, PPPoE push, DSA egress, and WED/WLAN redirect. Verify duplicate cookies return `-EEXIST`, unsupported keys/actions fall back, stats update packets/bytes/lastused, WED offload enable/disable callbacks balance, and destroy removes debugfs FOE entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_regs.h

## Purpose
`mtk_ppe_regs.h` is the register map for the PPE block. It provides offsets and bitfields used by `mtk_ppe.c` to configure global enable, supported flow types, protocol checking, FOE table location and aging policy, bind limits/rates, VLAN MTU enforcement, cache control, MIB accounting, and secondary bus controls.

## Important Constants
Core registers include `MTK_PPE_GLO_CFG`, `MTK_PPE_FLOW_CFG`, `MTK_PPE_IP_PROTO_CHK`, `MTK_PPE_TB_CFG`, `MTK_PPE_TB_BASE`, `MTK_PPE_BIND_RATE`, `MTK_PPE_BIND_LIMIT0/1`, `MTK_PPE_KEEPALIVE`, `MTK_PPE_UNBIND_AGE`, `MTK_PPE_BIND_AGE0/1`, `MTK_PPE_DEFAULT_CPU_PORT`, `MTK_PPE_VLAN_MTU0/1`, `MTK_PPE_CACHE_CTL`, `MTK_PPE_MIB_CFG`, `MTK_PPE_MIB_TB_BASE`, `MTK_PPE_MIB_SER_*`, `MTK_PPE_MIB_CACHE_CTL`, and `MTK_PPE_SBW_CTRL`. Enums describe scan modes, keepalive modes, and search-miss behavior.

## Control Flow
The PPE implementation uses these definitions in a predictable sequence: initialize FOE table base and table config, enable protocol and flow classes, configure unbind/bind aging and bind limits, enable cache, enable global PPE execution, set CPU ports, and optionally configure MIB table base and read-clear behavior. Stop/reset paths clear aging, cache, and global enable bits and poll `MTK_PPE_GLO_CFG_BUSY`. Accounting reads write an index to `MTK_PPE_MIB_SER_CR` and read serialized counter registers after `ST` clears.

## State And Persistence
Every macro maps to live hardware register state. These registers persist until reset or reprogramming. They influence how hardware interprets the coherent FOE table, whether new flows are built on search miss, which packet types are eligible, how old entries age, how MTU drops work, and whether MIB counters are populated.

## Dependencies And Integration Points
The header depends on kernel `BIT`, `GENMASK`, and field-prep usage via including files. It is consumed by `mtk_ppe.c` and indirectly by debug/diagnostic code. It must match `mtk_ppe.h` FOE layouts and `mtk_eth_soc.h` SoC metadata such as entry size and version.

## Risks
The most visible typo-like risk is `MTK_PPE_GLO_CFG_MCAST_ENTRIES` using `GNEMASK`, which would fail compilation if referenced. Register aliases are repeated for `MTK_PPE_KEEPALIVE`, so edits should avoid divergent definitions. Incorrect masks can silently misprogram hardware, leading to dropped traffic, failure to bind flows, broken aging, or invalid accounting. MIB cache enable uses a neighboring register and must not be confused with `MTK_PPE_MIB_CFG` bits.

## Test Signals
Compilation with all warnings catches unused broken macros only if referenced. Runtime signals include PPE start reaching not-busy, FOE table used count changing, flow classes binding for IPv4/IPv6/tunnel cases, MTU drop behavior matching configured interface MTU, and MIB counters returning sane deltas under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_star_emac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_star_emac.c

## Purpose
`mtk_star_emac.c` is a standalone platform netdev driver for the MediaTek STAR Ethernet MAC used by SoCs such as MT8516, MT8518, MT8175, and MT8365. It handles MMIO/regmap setup, per-SoC MII/RMII interface configuration, clock management, DMA descriptor rings, NAPI RX/TX, MDIO bus access, PHY connection, multicast hash filtering, hardware counters, suspend/resume, and netdev registration.

## Important APIs, Types, And Functions
Descriptor state is modeled by `struct mtk_star_ring_desc`, `mtk_star_ring_desc_data`, and `mtk_star_ring`. `struct mtk_star_priv` stores the netdev, regmaps, clocks, coherent descriptor memory, TX/RX rings, MDIO bus, NAPI structures, PHY state, timing flags, compatibility data, spinlock, and accumulated stats. `struct mtk_star_compat` carries SoC-specific interface setup and MAC clock divisor.

Core ring helpers are `mtk_star_ring_init`, `mtk_star_ring_pop_tail`, `mtk_star_ring_push_head`, RX/TX push wrappers, and `mtk_star_tx_ring_avail`. DMA helpers map and unmap RX/TX SKBs. Hardware setup helpers include `mtk_star_dma_init`, `mtk_star_dma_start`, `mtk_star_dma_stop`, `mtk_star_dma_disable`, `mtk_star_set_mac_addr`, `mtk_star_reset_counters`, `mtk_star_update_stats`, `mtk_star_reset_hash_table`, `mtk_star_set_hashbit`, `mtk_star_phy_config`, `mtk_star_init_config`, and `mtk_star_set_timing`. Netdev callbacks implement open, stop, xmit, stats, multicast mode, ioctl, ethtool, and PM.

## Control Flow
Probe allocates an etherdev, maps registers through regmap, obtains PERICFG syscon and IRQ, enables three clocks, validates MII/RMII mode, parses PHY and timing properties, runs SoC-specific interface mode setup, programs timing, sets a 32-bit DMA mask, allocates coherent descriptor memory, initializes config and MDIO, assigns a MAC address, adds NAPI, enables PHY managed PM, and registers the netdev.

Open calls `mtk_star_enable`: it disables powerdown and interrupts, stops DMA, writes MAC/config registers, resets the hash table, initializes descriptor rings, fills RX descriptors with mapped SKBs, requests IRQ, enables NAPI and interrupts, connects the PHY, starts DMA/PHY, and starts the netdev queue. TX maps the SKB head, pushes a descriptor with first/last/interrupt flags, accounts bytes, stops the queue if descriptor availability is low, and resumes TX DMA. TX NAPI pops completed descriptors, unmaps and frees SKBs, completes netdev queue accounting, wakes the queue above threshold, and re-enables TX interrupts. RX NAPI pops owned descriptors, drops CRC/oversize frames, allocates and maps replacement SKBs before handing the current SKB to the stack, pushes a fresh RX descriptor, resumes RX DMA, and re-enables RX interrupts when complete.

Stop disables queue/NAPI/interrupts/DMA, acknowledges interrupts, stops/disconnects PHY, frees IRQ, and unmaps/frees RX and TX SKBs. Suspend disables the running device and clocks; resume re-enables clocks and the netdev if it was running.

## State And Persistence
Runtime state lives in `mtk_star_priv`; descriptor ownership is shared with hardware through the COWN bit in coherent DMA memory. Accumulated `rtnl_link_stats64` are updated from hardware counters, which are read to reset/clear thresholded counters. PHY link, speed, duplex, and pause are cached and used to reprogram `PHY_CTRL1`. Multicast filter state persists in the hardware hash table until reset or mode change.

## Dependencies And Integration Points
The driver integrates with platform device probing, OF match data, syscon PERICFG, clocks, DMA API, netdev/NAPI, PHY/MDIO, ethtool, and PM. It does not share the main `mtk_eth_soc.h` data path; it is a separate MAC driver in the same vendor directory. Device tree properties include `mediatek,pericfg`, `phy-handle`, `phy-mode`, `mediatek,rmii-rxc`, `mediatek,rxc-inverse`, and `mediatek,txc-inverse`.

## Risks
TX maps only the linear SKB head even though availability checks account for fragments, so scatter-gather assumptions should be verified against netdev feature flags and SKB layout. RX allocation failure reuses the current SKB and counts drops, preserving ring operation but potentially hiding pressure. Descriptor ownership needs barriers exactly where implemented; changing COWN writes can break DMA coherency. Hash table operations have short polling timeouts and can fail under hardware faults. The stop path assumes `priv->phydev` exists after successful open. Multicast hash addressing is simple and can collide heavily.

## Test Signals
Probe should succeed for each compatible with correct MII/RMII PERICFG values and clock divisors. Runtime tests should cover open/close cycles, PHY link changes and pause settings, TX queue stop/wake under load, RX error drops, multicast/allmulti/promisc transitions, MDIO reads/writes, suspend/resume while running and stopped, hardware counter threshold interrupts, and DMA mapping failure injection where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_star_emac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed.c

## Purpose
`mtk_wed.c` implements MediaTek WED, the Wireless Ethernet Dispatch block that accelerates traffic between the Ethernet/PPE subsystem and MediaTek WLAN DMA engines. It registers WED hardware instances, exposes an operation table to WLAN drivers, attaches WLAN devices to available WED blocks, allocates TX/RX buffer managers and rings, configures WED/WDMA/WPDMA register mirrors, handles reset/start/stop/detach, coordinates Wi-Fi offload flow enablement, supports RRO/WOCPU paths on newer SoCs, and routes TC flower offload commands through the Ethernet PPE.

## Important APIs, Types, And Functions
Global state is `hw_list[3]` protected by `hw_lock`. SoC variants are described by `mt7622_data`, `mt7986_data`, and `mt7988_data`, which carry register offsets and descriptor sizes. Hardware registration is `mtk_wed_add_hw`; cleanup is `mtk_wed_exit`. WLAN-facing operations are assembled in `mtk_wed_add_hw` as `struct mtk_wed_ops`: attach, TX/RX ring setup, txfree ring setup, start/stop, reset DMA, register read/write, IRQ get/mask, detach, PPE check, TC setup, HW RRO start, RRO/MSDU page/IND RX ring setup, and MCU message update.

Attach/detach and lifecycle functions include `mtk_wed_assign`, `mtk_wed_attach`, `__mtk_wed_detach`, `mtk_wed_detach`, `mtk_wed_hw_init_early`, `mtk_wed_hw_init`, `mtk_wed_start`, `mtk_wed_stop`, `mtk_wed_deinit`, `mtk_wed_dma_enable`, `mtk_wed_dma_disable`, `mtk_wed_reset_dma`, `mtk_wed_rx_reset`, `mtk_wdma_rx_reset`, and `mtk_wdma_tx_reset`. Buffer/ring management includes TX buffer allocation/free, AMSDU buffer allocation/init/free, RX BM/HWRRO allocation/free/init, WDMA RX/TX ring setup, WED TX/RX ring setup, txfree ring setup, RRO and page ring setup, and indirect command ring setup. Flow accounting APIs are `mtk_wed_flow_add` and `mtk_wed_flow_remove`.

## Control Flow
`mtk_wed_add_hw` is called by the Ethernet driver with the WED DT node, `struct mtk_eth`, WDMA base/physical address, and index. It resolves the platform device, IRQ, and syscon regmap, publishes `mtk_soc_wed_ops` under RCU, creates `mtk_wed_hw`, selects SoC data by `eth->soc->version`, sets up v1 mirror/hifsys maps when needed, creates debugfs, and stores the instance in `hw_list`.

WLAN attach requires the caller to hold RCU. `mtk_wed_attach` module-pins this driver, selects a compatible unused hardware block, sets DMA mask and DMA device mapping, allocates TX buffer manager memory, allocates v3 AMSDU buffers, optionally allocates RRO resources, initializes early hardware, adjusts coherence mappings, reads revision, and initializes WOCPU support when RX acceleration is enabled. On failure it calls the detach path.

Start allocates RX buffers when RX capability exists, creates missing WDMA RX rings, initializes WED hardware once, configures interrupts, enables extension error interrupts, configures RRO through the MCU on RX-capable hardware, enables 512-WCID and AMSDU support, enables WED/WDMA/WPDMA DMA agents, and marks the device running. Ring setup redirects WLAN WPDMA rings through WED: WLAN-provided registers become WED-facing rings while WED-owned DMA rings are programmed into WPDMA/WDMA control registers. Reset paths carefully disable and poll each agent, reset indexes/FIFOs, reset buffer managers, coordinate WOCPU state, and rebuild descriptor rings.

PPE integration occurs through `mtk_wed_ppe_check`, which receives a CPU reason and FOE hash from WLAN/WED and calls `mtk_ppe_check_skb` for unbind-rate hits. TC setup on WED-backed netdevs registers flow-block callbacks that call `mtk_flow_offload_cmd` with the WED hardware index. `mtk_wed_flow_add/remove` toggle WLAN offload callbacks around a per-WED flow count and update extension interrupt masks.

## State And Persistence
`struct mtk_wed_hw` persists from `mtk_wed_add_hw` to `mtk_wed_exit`; `struct mtk_wed_device` is owned by the WLAN side but populated and zeroed by attach/detach. DMA-backed TX BM, RX BM, RRO, AMSDU, WDMA, and WED rings persist while attached. Hardware state spans WED, WDMA, WPDMA, PCIe interrupt mapping, hifsys/mirror syscons, and WOCPU reserved memory/MCU state. `num_flows` persists per WED hardware and gates WLAN offload enable/disable.

## Dependencies And Integration Points
This file depends on platform/OF/syscon/reserved-memory APIs, DMA mapping, debugfs, the public `linux/soc/mediatek/mtk_wed.h`, private `mtk_wed.h`, register definitions, `mtk_wed_wo.h`, `mtk_eth_soc.h`, `mtk_ppe.h`, flow offload, and TC. It integrates bidirectionally with WLAN drivers via `mtk_soc_wed_ops`, with Ethernet via `struct mtk_eth`, PPE arrays and DMA device switching, with WOCPU firmware through MCU messages, and with TC flower through the same offload command path as Ethernet netdevs.

## Risks
This is high-risk hardware orchestration. Resource allocation loops in TX/RX/HWRRO/AMSDU paths have partial allocation failure cases that rely on detach/free routines to clean up; leaks or double frees can occur if size fields do not match allocation counts. Reset sequencing is version-specific and depends on polling busy bits; missed busy conditions can leave DMA agents wedged. `hw_list` indexing assumes up to three instances and uses `!hw->index` in one detach coherence condition, which only reasons about two peers. `mtk_wed_flow_remove` decrements `num_flows` without an explicit underflow guard after initial checks. Raw ioremap in WO reset assumes the reset address is valid. DMA device switching for coherent WLAN paths must be balanced on detach.

## Test Signals
Test attach/detach loops for PCIe and AXI WLAN devices, v1/v2/v3 SoCs, RX-capable and TX-only configurations, HW RRO on/off, AMSDU on v3, WED start/stop/reset while traffic is active, suspend-like WLAN reset callbacks through `mtk_wed_fe_reset`, TC flower WED redirect flows, WED debugfs counters, extension interrupt errors, and fault injection for DMA allocation failures. Traffic tests should confirm PPE/WED offloaded flows enable WLAN callbacks once, disable when the last flow is removed, and recover after WED reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed.h

## Purpose
`mtk_wed.h` is the private WED header for the MediaTek Ethernet driver. It defines per-SoC WED register metadata, private hardware state, AMSDU allocation records, WDMA forwarding information, MMIO/regmap accessors for WED/WDMA/WPDMA rings, version helpers, public internal WED entry points, and build-time stubs when WED support is disabled.

## Important APIs And Types
`struct mtk_wed_soc_data` stores variant-specific register offsets, reset masks, TX ring descriptor size, and WDMA descriptor size. `struct mtk_wed_amsdu` records a v3 AMSDU TXD buffer and DMA address. `struct mtk_wed_hw` is the private hardware instance: it points to SoC data, device tree node, Ethernet core, WED regmap, hifsys/mirror regmaps, WDMA MMIO/physical base, debugfs directory, attached `mtk_wed_device`, WOCPU object, AMSDU array, PCIe base, flow count, version, IRQ, and index. `struct mtk_wdma_info` is the compact path result used by PPE offload to program WDMA index, queue, WCID, BSS, and AMSDU flag.

Inline helpers include version predicates, `wed_w32/r32`, `wdma_w32/r32`, `wpdma_tx_*`, `wpdma_rx_*`, `wpdma_txfree_*`, and `mtk_wed_get_pcie_base`. Public internal functions include `mtk_wed_add_hw`, `mtk_wed_exit`, `mtk_wed_flow_add`, `mtk_wed_flow_remove`, `mtk_wed_fe_reset`, `mtk_wed_fe_reset_complete`, and `mtk_wed_hw_add_debugfs`.

## Control Flow
When `CONFIG_NET_MEDIATEK_SOC_WED` is enabled, callers can register WED hardware, attach WLAN devices through the public ops table, and access WED/WDMA/WPDMA registers through these helpers. WPDMA accessor helpers return zero or no-op if a ring has not been configured yet, which lets debugfs and setup paths safely query optional rings. When WED is disabled, inline stubs compile out WED registration and make flow add return `-EINVAL`.

## State And Persistence
The header defines state owned by `mtk_wed.c`; it does not allocate directly. `mtk_wed_hw` persists across WLAN attaches until `mtk_wed_exit`. The attached `mtk_wed_device` pointer is a handoff to the WLAN owner and is cleared on detach. `num_flows` persists as the per-hardware WED offload reference count.

## Dependencies And Integration Points
It depends on the public MediaTek WED SoC header, debugfs, regmap, netdevice, and `mtk_wed_regs.h`. Ethernet code uses it to register WED hardware and call reset hooks. PPE offload uses `struct mtk_wdma_info` and `mtk_wed_flow_add/remove`. Debugfs uses raw register access helpers. The public `mtk_soc_wed_ops` path in external WLAN drivers depends on the behavior implemented behind these declarations.

## Risks
Because accessors hide missing ring pointers by returning zero, diagnostics can look like real zeroed hardware if a ring was never configured. Version helpers are simple equality checks, so future SoC versions require auditing `mtk_wed_is_v3_or_greater` assumptions. Build stubs must preserve call-site semantics; returning `-EINVAL` for flow add is important for offload cleanup paths. `mtk_wed_hw` lifetime is protected externally by `hw_lock` and RCU publication, not by the header itself.

## Test Signals
Build with WED enabled and disabled. With WED disabled, Ethernet should probe and TC offload should gracefully reject WED paths. With WED enabled, debugfs register access should reflect configured rings, WDMA info should program WED flows, and attach/detach should leave `wed_dev` and flow counts consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_debugfs.c

## Purpose
`mtk_wed_debugfs.c` creates debugfs diagnostics for WED hardware instances. It provides formatted register dumps for TX, RX, AMSDU, route queue manager, and RRO/indirect-command paths, plus a raw `regidx`/`regval` pair for direct WED register reads and writes. The file is primarily an observability and bring-up aid for complex WED/WDMA/WPDMA interactions.

## Important APIs And Functions
`struct reg_dump` describes one dump item: name, offset, register source type, base/ring index, and mask. Macros such as `DUMP_WED`, `DUMP_WDMA`, `DUMP_WPDMA_TX_RING`, `DUMP_WPDMA_RX_RING`, `DUMP_WED_RING`, and `DUMP_WED_MASK` build static register lists. `dump_wed_regs` selects the right accessor based on type and prints values with `print_reg_val`. Show functions are `wed_txinfo_show`, `wed_rxinfo_show`, `wed_amsdu_show`, `wed_rtqm_show`, and `wed_rro_show`. `mtk_wed_reg_get/set` implement raw register access. `mtk_wed_hw_add_debugfs` creates the per-instance directory and files.

## Control Flow
At hardware registration, `mtk_wed_hw_add_debugfs` creates `wed%d`, `regidx`, `regval`, and `txinfo`. For non-v1 hardware it adds `rxinfo`; for v3 or newer it also adds `amsdu`, `rtqm`, and `rro`. Each read obtains `hw` from `s->private`, checks `hw->wed_dev`, and dumps static register arrays. `wed_rxinfo_show` combines common RX registers with v2 or v3 route/RRO-specific arrays. Raw register access writes or reads `hw->debugfs_reg` through the WED regmap.

## State And Persistence
Debugfs state is the directory pointer in `hw->debugfs_dir` and the mutable `hw->debugfs_reg` selected by users. The dump files read live WED, WDMA, and WLAN WPDMA ring registers; they do not cache values. `regval` can mutate hardware state, so it is diagnostic control state rather than pure observation.

## Dependencies And Integration Points
The file depends on seq_file/debugfs, public WED structs, private WED helpers, and WED register macros. It uses `wed_r32`, `wdma_r32`, `wpdma_tx_r32`, `wpdma_rx_r32`, and `wpdma_txfree_r32`, so it reflects the same configured ring pointers created by `mtk_wed.c`. `mtk_wed_exit` removes the directory.

## Risks
`debugfs_create_file_unsafe` and raw `regval` writes are powerful and can destabilize hardware if used incorrectly. Dumps are unsynchronized with attach/detach and live reset beyond checking `wed_dev`, so values may be transient. Several dump labels or repeated counters appear copy-pasted, which can mislead manual diagnosis. Reading unconfigured WPDMA rings returns zero through helper stubs, which may be confused with valid zero register values.

## Test Signals
With debugfs enabled, verify `wed0/txinfo` appears for all WED versions, `rxinfo` for v2/v3, and `amsdu`, `rtqm`, `rro` for v3. During traffic, TX/RX ring indexes and MIB counters should move. During reset, dump files should not crash. Raw `regidx/regval` should read a known harmless register before any write testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_debugfs.c -->
