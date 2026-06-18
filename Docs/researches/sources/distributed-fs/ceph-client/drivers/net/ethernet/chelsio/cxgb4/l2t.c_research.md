# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/l2t.c

Purpose: manages the cxgb4 software mirror of the hardware Layer-2 table used by offload traffic to resolve next-hop MAC/VLAN/port information and queue packets while neighbor resolution is pending.

Important APIs/functions: `cxgb4_l2t_get`, `cxgb4_l2t_release`, `cxgb4_l2t_send`, `t4_l2t_update`, `t4_l2t_alloc_switching`, `t4_init_l2t`, `do_l2t_write_rpl`, `cxgb4_select_ntuple`, `cxgb4_check_l2t_valid`, and debugfs `t4_l2t_fops`; internal helpers hash addresses, allocate/reuse entries, write hardware L2 entries, and drain ARP queues.

Control flow: `cxgb4_l2t_get` hashes neighbor address plus ifindex, finds or allocates an entry, references the neighbor, records VLAN/logical port, and starts in resolving state. `cxgb4_l2t_send` sends immediately for valid/stale entries or queues packets for resolving/sync-write entries and triggers neighbor events. Neighbor updates write hardware entries, send queued packets, or invoke ARP error handlers on failure. Switching allocation creates non-hashed entries keyed by VLAN/port/MAC.

State and persistence: `struct l2t_data` holds a flexible array of entries, hash bucket heads embedded in entries, rover pointer, rwlock, and free count. Each `l2t_entry` has state, refcount, neighbor pointer, ARP queue, VLAN, lport, MAC, and lock. Hardware L2 table entries are updated by CPL work requests.

Dependencies/integration: uses Linux neighbor, VLAN, skb queue, debugfs/seq_file, jhash, and Chelsio CPL/management TX APIs. ULDs and offload paths call it before sending packets that require L2 resolution.

Risks: locking mixes table rwlocks, entry spinlocks, and bottom-half variants; ordering must remain consistent. Entries with refcount zero can remain hashed for reuse. `do_l2t_write_rpl` derives local index from firmware TID and assumes it falls within the adapter slice. ARP failure path releases entry lock while invoking handlers.

Test signals: IPv4/IPv6 neighbor resolution, VLAN priority handling, loopback path, stale-to-valid transitions, failed neighbor resolution with and without ARP error handler, switching entries, L2T_WRITE reply errors, debugfs dump, and refcount/free reuse races.
