<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_fdb.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_fdb.c

Purpose: implements the Linux bridge forwarding database (FDB). It owns allocation, lookup, ageing, deletion, netlink dump/get/add/delete/flush operations, local MAC bookkeeping, externally learned and offloaded entry state, static unicast filter synchronization, and integration with switchdev and tracepoints. The FDB maps `(MAC address, VLAN ID)` keys to optional bridge ports or to the bridge device itself for local entries, and is read from hot packet paths such as `br_handle_frame_finish()`.

Important APIs, types, and functions:

- `br_fdb_init()` / `br_fdb_fini()` create and destroy the `net_bridge_fdb_entry` kmem cache. `br_fdb_hash_init()` / `br_fdb_hash_fini()` initialize each bridge's `rhashtable`.
- `struct net_bridge_fdb_entry` is stored in both `br->fdb_hash_tbl` and `br->fdb_list`; its key is `struct net_bridge_fdb_key`, with state in `flags`, `dst`, `updated`, and `used`.
- Lookup and reader APIs include `br_fdb_find_rcu()`, `br_fdb_find_port()`, `br_fdb_fillbuf()`, `br_fdb_dump()`, and `br_fdb_get()`.
- Mutation APIs include `br_fdb_update()`, `br_fdb_add_local()`, `br_fdb_find_delete_local()`, `br_fdb_delete_by_port()`, `br_fdb_flush()`, `br_fdb_add()`, `br_fdb_delete()`, `br_fdb_delete_bulk()`, `br_fdb_external_learn_add()`, `br_fdb_external_learn_del()`, `br_fdb_offloaded_set()`, and `br_fdb_clear_offload()`.
- Local and static helper paths include `fdb_add_hw_addr()`, `fdb_del_hw_addr()`, `br_fdb_changeaddr()`, `br_fdb_change_mac_address()`, `br_fdb_toggle_local_vlan_0()`, `br_fdb_sync_static()`, and `br_fdb_unsync_static()`.
- `fdb_fill_info()` formats rtnetlink neighbor messages using `NUD_*`, `NTF_*`, `NDA_*`, and bridge extended FDB attributes.

Core control flow:

- Entries are created by `fdb_create()` after optional dynamic learned entry limit enforcement through `br->fdb_max_learned` and `br->fdb_n_learned`. Insertions go into the rhashtable first, then the RCU hlist, so readers can resolve by key and dump in list order.
- Packet learning calls `br_fdb_update()` from the ingress path under RCU and bottom halves disabled. Existing entries are refreshed by `updated`; roaming changes `dst` unless the entry is sticky; external-learn and locked bits are cleared when software learning takes over; changed entries notify switchdev and rtnetlink.
- `br_fdb_cleanup()` is delayed work. It walks `br->fdb_list` under RCU, deletes expired dynamic entries under `hash_lock`, sends inactive notifications for tracked entries, and reschedules itself based on the nearest expiry, bounded to at least 10 ms.
- Netlink add validates bridge or port context, state, VLAN membership, sticky/permanent combinations, activity notification attributes, and extended flags. If no VID is provided and VLANs exist, it applies the requested entry to every usable VLAN.
- Netlink delete mirrors add by deleting a specific VID or all usable VLANs. Bulk delete converts `ndm_state`, `ndm_flags`, explicit masks, VLAN, and ifindex into `struct net_bridge_fdb_flush_desc`, validates that the selected device belongs to the target bridge, and flushes matching entries.
- Local entries are special: they are static, may have `dst == NULL` for the bridge device, and are regenerated when bridge or port MACs and VLAN policy change. `fdb_delete_local()` preserves a local address if another port or the bridge still owns the same address on the same VID.
- Externally learned entries are created by switchdev or user requests with `NTF_EXT_LEARNED`; optional locked entries require an MAB-capable port. Offload state can be toggled independently.

State and persistence behavior:

- FDB state is runtime bridge state, not persistent storage. It lives in the bridge rhashtable/list until ageing, deletion, port teardown, bridge deletion, external-learn deletion, or netlink/user mutation.
- `hash_lock` protects structural mutation and flag/accounting changes that must be serialized. RCU protects packet-path and dump readers. `dst`, `updated`, and `used` use `READ_ONCE()`/`WRITE_ONCE()` when concurrently visible.
- Dynamic entry ageing depends on `hold_time()`: topology changes shorten hold time to `forward_delay`, otherwise `ageing_time` applies. Static and external-learned entries do not expire.
- Static FDB entries are mirrored into lower device unicast filters through `dev_uc_add()`/`dev_uc_del()` when ports are not promiscuous. Failures are rolled back where possible.
- Notifications are durable only as events: switchdev is notified before/with rtnetlink on add/delete/update, tracepoints record FDB mutations, and `RTNLGRP_NEIGH` subscribers observe `RTM_NEWNEIGH` and `RTM_DELNEIGH`.

Dependencies and integration points:

- Packet ingress in `br_input.c` uses `br_fdb_find_rcu()` for unicast forwarding and `br_fdb_update()` for source learning.
- Port and bridge lifecycle in `br_if.c` add/delete local entries, synchronize static filters, and flush entries by port.
- VLAN logic is central through `br_vlan_group()`, `nbp_vlan_group()`, `br_vlan_find()`, `br_vlan_should_use()`, and `BROPT_FDB_LOCAL_VLAN_0`.
- Switchdev integration reports learned, deleted, offloaded, and externally learned entries to hardware drivers.
- Legacy ioctl support in `br_ioctl.c` calls `br_fdb_fillbuf()` for old bridge tools.

Risks and edge cases:

- The FDB is on a hot path with mixed RCU and spinlock access. Missing `hash_lock`, stale `dst` handling, or freeing without RCU would become packet-path use-after-free bugs.
- Dynamic learned entry limiting only applies on new entry creation. Races can lose an update if another CPU creates the same entry first, intentionally avoiding a slow retry.
- Local MAC handling is subtle when ports share MAC addresses, VLAN 0 local entries are toggled, or bridge VLAN membership changes. Wrong handling can remove local delivery or leave stale local entries.
- Static unicast filter synchronization can fail on devices with limited filter space; bridge code logs errors but often continues by using promiscuous mode or best-effort rollback.
- Locked/MAB entries intentionally drop traffic until authorization. Incorrect flag conversion from netlink could bypass port locking, so `NTF_EXT_LOCKED` is rejected from normal add.

Test signals:

- Validate dynamic learning, roaming, sticky entries, ageing after topology changes, and `fdb_max_learned` behavior with bridge traffic and `bridge fdb show`.
- Exercise netlink add/delete/replace/flush with VLAN-specific entries, all-VLAN expansion, `NTF_USE`, `NTF_EXT_LEARNED`, `NTF_STICKY`, notification flags, and invalid ext flags.
- Check local entries after bridge MAC change, port MAC change, VLAN filtering changes, and `fdb_local_vlan_0` toggles.
- Use switchdev or mocked drivers to verify offload notifications and external-learn add/delete paths.
- Watch rtnetlink `RTNLGRP_NEIGH`, tracepoints, `tx_dropped`, and device unicast filter programming when testing error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_fdb.c -->
