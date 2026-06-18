# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_filters.c

## Purpose
`mcdi_filters.c` implements firmware-backed RX filter and RSS context management. Firmware owns write-only filter tables and returns opaque 64-bit handles, while Linux needs smaller IDs and lookup/replacement behavior. The file maintains a software hash-table shadow, translates `struct efx_filter_spec` to MCDI match masks, syncs automatic MAC/VLAN/default filters from netdevice state, restores filters/RSS after MC reboot, and manages shared/exclusive RSS contexts.

## Important APIs, Types, And Functions
Lifecycle APIs are `efx_mcdi_filter_table_probe()`, `efx_mcdi_filter_table_down()`, `efx_mcdi_filter_table_remove()`, `efx_mcdi_filter_table_restore()`, and `efx_mcdi_filter_table_reset_mc_allocations()`. Filter operations include `efx_mcdi_filter_insert()`, `efx_mcdi_filter_remove_safe()`, `efx_mcdi_filter_get_safe()`, `efx_mcdi_filter_clear_rx()`, `efx_mcdi_filter_count_rx_used()`, `efx_mcdi_filter_get_rx_id_limit()`, and `efx_mcdi_filter_get_rx_ids()`.

Receive-mode/VLAN APIs include `efx_mcdi_filter_sync_rx_mode()`, `efx_mcdi_filter_add_vlan()`, `efx_mcdi_filter_del_vlan()`, `efx_mcdi_filter_cleanup_vlans()`, and `efx_mcdi_filter_find_vlan()`. RSS APIs include `efx_mcdi_rx_push_rss_context_config()`, PF/VF RSS push helpers, default indirection programming, RSS pull/free/restore helpers, and optional `efx_mcdi_filter_rfs_expire_one()`.

## Control Flow
Probe queries firmware-supported normal and encapsulated match masks using `GET_PARSER_DISP_INFO`, disables VLAN filtering if required match forms are absent, allocates an 8192-row software table, and records multicast chaining/VLAN state. Insertion locks the filter table, validates RX-only filters, maps match flags to a firmware match priority, resolves RSS context, searches the software table by hash, handles duplicate/priority/replacement rules, then issues `MC_CMD_FILTER_OP`. Multicast recipient insertion may unsubscribe lower-priority recipients after a successful higher-priority insertion.

Receive-mode sync marks existing automatic filters old, snapshots netdevice unicast/multicast lists, handles VLAN-filter feature changes, synchronizes each VLAN's unicast, multicast, broadcast, and encapsulated default filters, then removes unrenewed old filters. Failures can fall back to unicast/multicast default filters or promiscuous-style subscriptions depending on multicast chaining and overflow.

RSS control flow allocates firmware contexts, programs indirection tables and keys, optionally enables UDP 4-tuple hash flags, falls back from exclusive to shared contexts for non-user PF setup on `-ENOBUFS`, and rebuilds ethtool RSS contexts after MC reboot. Filter restoration replays saved specs and drops entries that are unsupported after reboot or whose RSS context cannot be restored.

## State And Persistence Behavior
`efx->filter_state` is the host RAM shadow. Each row stores a saved filter spec pointer with packed private flags plus the firmware handle needed for removal. VLAN entries store automatic filter row IDs. Netdevice address-list shadows are refreshed during sync. Firmware filter handles and RSS context IDs are runtime MC allocations and become invalid after MC reboot; saved specs and ethtool RSS settings are used to reconstruct them. No state is written to disk.

## Dependencies And Integration Points
The file depends on `mcdi_filters.h`, `mcdi.h`, `nic.h`, `rx_common.h`, generic filter helpers, netdevice address lists/flags/features, ethtool RSS context infrastructure, RFS/RPS helpers, and MCDI commands `FILTER_OP`, `GET_PARSER_DISP_INFO`, and `RSS_CONTEXT_*`. It integrates with receive-mode changes, VLAN offload, vport and queue IDs, RSS ethtool operations, MC reboot recovery, and accelerated RFS.

## Risks And Edge Cases
The software table must remain consistent with firmware handles despite firmware being write-only. ID encoding depends on table size and match-priority ordering. Lock ordering across `filter_sem`, table rwsem, RSS mutex, address locks, and RPS locks is critical. Fallback paths for promiscuous/allmulti, multicast chaining, encapsulation capability, and shared RSS allocation are subtle and firmware-version dependent.

## Test Signals
Test VLAN filtering support and unsupported firmware, encapsulated filters, multicast chaining on/off, promisc/allmulti transitions, multicast overflow, VLAN add/delete, ethtool RSS create/set/get/delete, MC reboot with active filters, and RFS expiry. Watch logs for unsupported match flags, filter restore failures, default/broadcast insert failures, RSS fallback, and stale auto-filter marks.
