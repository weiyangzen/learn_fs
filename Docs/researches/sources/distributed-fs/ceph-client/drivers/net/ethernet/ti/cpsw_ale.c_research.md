# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_ale.c

## Purpose
`cpsw_ale.c` implements the CPSW Address Lookup Engine abstraction. It hides ALE register and table layout differences across legacy CPSW, NetCP NU switch, AM65, J721E, and AM64 variants, and provides APIs for unicast, multicast, VLAN, port control, rate limiting, aging, table dump/restore, and default classifier setup.

## Important APIs, Types, And Functions
The key constructor is `cpsw_ale_create()`, which matches `dev_id`, creates a regmap over ALE MMIO, allocates regmap fields and VLAN untag tracking, reads hardware version/table sizes, and initializes variant-specific field metadata. Table APIs include `cpsw_ale_add_ucast()`, `cpsw_ale_del_ucast()`, `cpsw_ale_add_mcast()`, `cpsw_ale_del_mcast()`, `cpsw_ale_flush_multicast()`, `cpsw_ale_add_vlan()`, `cpsw_ale_del_vlan()`, `cpsw_ale_vlan_add_modify()`, and `cpsw_ale_vlan_del_modify()`. Control APIs are `cpsw_ale_control_set()` and `cpsw_ale_control_get()`, backed by `ale_controls[]`. Lifecycle APIs are `cpsw_ale_start()` and `cpsw_ale_stop()`. Diagnostics and restore paths use `cpsw_ale_dump()`, `cpsw_ale_restore()`, and `cpsw_ale_get_num_entries()`.

## Control Flow
Table operations scan the hardware table for matching address/VLAN/free/ageable entries, construct 68-bit entries through bitfield helpers, and write them through `ALE_TABLE` plus `ALE_TABLE_CONTROL`. VLAN functions merge port membership, registered/unregistered multicast masks, and untag masks, with special handling for NU switch VLAN mask mux registers. Start programs the ALE prescale for 1000 pps granularity, enables global rate limiting, enables and clears ALE, then starts either software aging timer or hardware aging timer. Stop reverses aging and disables/clears ALE. Default classifier setup resets policer/thread mappings and maps PCP priorities to RX channels through ALE policer entries.

## State And Persistence
The ALE table, port controls, policer registers, VLAN mask mux registers, aging timer, and `p0_untag_vid_mask` are persistent runtime hardware/software state. `cpsw_ale_create()` mutates global `ale_controls[]` offsets and widths for NU switch variants, which affects all ALE users in the module. Entry allocation prefers existing matching entries, then free entries, then ageable unicast entries. `p0_untag_vid_mask` mirrors host-port untag VLANs so RX VLAN encapsulation handling can decide whether to restore tags.

## Dependencies And Integration Points
The file depends on MMIO, regmap/regmap_field, Linux timers, bitmaps, Ethernet helpers, VLAN constants, and module/platform infrastructure. It is consumed by `cpsw.c`, `cpsw_new.c`, `cpsw_priv.c`, `cpsw_ethtool.c`, and `cpsw_switchdev.c` for filtering, switch mode, bridge VLANs/MDB/FDBs, multicast state, timestamp-aware RX VLAN processing, ethtool register dumps, and TC policer offload.

## Risks
ALE entry bit positions differ by SoC, so incorrect `vlan_entry_tbl` or dynamic port bit width corrupts VLAN membership. The global mutation of `ale_controls[]` for NU variants could be unsafe if multiple ALE hardware types coexist in one kernel instance. Table scans are linear in ALE entries and happen under caller context, so large ALE tables can make control operations expensive. Rate limits round down to 1000 pps granularity. `WARN_ON(idx > ale_entries)` accepts `idx == ale_entries`; callers should not pass an out-of-range index. Aging may evict non-persistent unicast entries when tables are full.

## Test Signals
Exercise add/delete of VLAN, unicast, multicast, allmulti, unknown VLAN controls, ALE bypass, rate limits below and above 1000 pps, and ethtool register dumps. Test legacy CPSW and NU/K3 variants for correct table size detection, VLAN mask mux behavior, host-port untag RX handling, software and hardware aging, and classifier thread mapping for 1-8 RX channels.
