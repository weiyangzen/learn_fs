# subset-b-006168

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_forward.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_forward.c

Purpose: implements bridge egress forwarding and flooding. It decides whether a frame can be delivered to a port, applies egress VLAN handling, invokes bridge netfilter hooks, queues packets to lower devices, handles clone-on-flood semantics, and contains multicast-specific replication support when IGMP snooping is enabled.

Important APIs, types, and functions:

- `br_forward()` forwards one skb to a selected bridge port, optionally cloning when the original must also be delivered locally.
- `br_flood()` floods unknown unicast, multicast, or broadcast traffic to eligible ports.
- `br_multicast_flood()` performs MDB/router-port aware multicast replication under `CONFIG_BRIDGE_IGMP_SNOOPING`.
- `br_forward_finish()` and `br_dev_queue_push_xmit()` are netfilter continuation/output helpers and are exported for bridge users.
- `should_deliver()` is the central egress eligibility test. It checks hairpin mode, origin port, STP/MST state, VLAN egress permission, switchdev egress permission, and isolated-port rules.
- `maybe_deliver()` and `deliver_clone()` implement the "clone all but the final skb" flooding pattern.

Core control flow:

- `br_forward()` first handles backup-port redirection: if the destination port has a configured backup and the primary link is not running or has no carrier, it redirects to the backup and records `backup_nhid` in the bridge skb control block. It then runs `should_deliver()`. If local receive is also needed, it clones and forwards the clone; otherwise it consumes the original skb. If delivery is rejected and no local receive is pending, it frees the skb.
- `__br_forward()` marks switchdev forwarding offload before VLAN handling so `br_handle_vlan()` can decide whether to pop or keep VLAN headers. It changes `skb->dev` to the egress device and selects `NF_BR_FORWARD` for transit frames or `NF_BR_LOCAL_OUT` for locally originated frames. Transit frames reject LRO skbs and fix checksums; local netpoll frames bypass normal qdisc transmit through `br_netpoll_send_skb()`.
- `br_forward_finish()` clears skb timestamps and invokes `NF_BR_POST_ROUTING`; `br_dev_queue_push_xmit()` restores the Ethernet header, rejects non-forwardable frames, drops fake routes, fixes partial checksum VLAN network header positioning, sets switchdev offload forwarding marks, and calls `dev_queue_xmit()`.
- `br_flood()` iterates the bridge port list under RCU. It skips ports according to per-port flood flags (`BR_FLOOD`, `BR_MCAST_FLOOD`, `BR_BCAST_FLOOD`), proxy ARP/neighbour suppression, and the shared delivery rules. It clones to the previous selected port and saves the current port for final zero-copy delivery.
- `br_multicast_flood()` merges MDB port groups and multicast router ports, handles multicast-to-unicast replication by copying the skb and rewriting destination MACs, respects include/block flags for source-specific multicast, and again sends only the final copy without cloning.

State and persistence behavior:

- This file keeps almost no persistent state itself. It consumes bridge, port, VLAN, multicast, and skb control-block state maintained elsewhere.
- It mutates transient skb fields: Ethernet header position, `skb->dev`, checksum metadata, network header for VLAN partial checksum, switchdev offload marks, traffic-control miss indication, multicast statistics, and bridge private skb control fields.
- Drop accounting uses device statistics and skb drop reasons such as no transmit target or no memory. Multicast TX accounting is updated through `br_multicast_count()`.

Dependencies and integration points:

- Egress VLAN policy comes from `br_handle_vlan()`, `br_allowed_egress()`, and VLAN groups.
- Netfilter integration uses `NF_HOOK()` for `NF_BR_FORWARD`, `NF_BR_LOCAL_OUT`, and `NF_BR_POST_ROUTING`.
- Switchdev integration uses egress permission checks and offload forwarding marks to keep hardware and software forwarding behavior aligned.
- `br_input.c` calls `br_forward()`, `br_flood()`, and `br_multicast_flood()` after ingress learning and destination lookup.
- Netpoll, multicast snooping, proxy ARP, neighbour suppression, MST/STP state, isolated ports, backup ports, and qdisc transmit are all part of the egress decision surface.

Risks and edge cases:

- Ownership of the skb is subtle. Flooding intentionally clones only earlier deliveries and gives the original skb to the final egress or local receive path. Any new branch must preserve that ownership model.
- `should_deliver()` combines multiple policy systems. A change in ordering can affect VLAN filtering, MST forwarding, hardware offload domains, hairpin forwarding, or isolated port behavior.
- Backup-port redirection depends on RCU pointers and link state checks. It records backup nexthop state in the skb control block for later consumers.
- Multicast-to-unicast replication temporarily pushes and pulls the Ethernet header around `pskb_copy()`. Header offset mistakes would corrupt outgoing frames.
- Partial checksum VLAN handling relies on correct VLAN protocol/depth parsing before transmit.

Test signals:

- Forward known unicast, unknown unicast flood, broadcast, and multicast traffic across ports with combinations of hairpin, isolated, flood flags, VLAN filtering, and MST/STP state.
- Validate backup-port redirection by dropping carrier on a primary port and checking egress and `backup_nhid` behavior.
- Exercise netfilter bridge hooks at forward, local-out, and post-routing points.
- With IGMP snooping, test MDB-only multicast, router-port replication, multicast-to-unicast, source include/exclude, and blocked MDB port groups.
- Monitor skb drop reasons, `tx_dropped`, multicast counters, and switchdev offload marks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_forward.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_if.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_if.c

Purpose: implements bridge and bridge-port lifecycle operations exposed to userspace and other bridge subsystems. It creates and deletes bridge netdevices, enslaves and releases lower devices, manages port object lifetime, promiscuous/all-multicast mode, headroom, MTU, feature recomputation, local FDB entries, STP port enablement, multicast port context, netpoll, sysfs, upper-device links, and backup-port relationships.

Important APIs, types, and functions:

- Bridge device management: `br_add_bridge()`, `br_del_bridge()`, and `br_dev_delete()`.
- Port management: `br_add_if()`, `br_del_if()`, `new_nbp()`, `del_nbp()`, `destroy_nbp_rcu()`, and the `brport_ktype` kobject type.
- Port/link state helpers: `br_port_carrier_check()`, `br_port_flags_change()`, `br_port_flag_is_set()`, `nbp_backup_change()`, and `nbp_backup_clear()`.
- Promiscuity and filtering helpers: `br_manage_promisc()`, `br_port_set_promisc()`, `br_port_clear_promisc()`, `nbp_delete_promisc()`, and `nbp_update_port_count()`.
- Device shape helpers: `port_cost()`, `br_mtu_auto_adjust()`, `br_features_recompute()`, `get_max_headroom()`, and `update_headroom()`.

Core control flow:

- `br_add_bridge()` allocates a `struct net_bridge` embedded in a netdevice with `br_dev_setup()`, assigns the target net namespace, attaches `br_link_ops`, and registers the device.
- `br_add_if()` validates that the lower device is a usable Ethernet device, is not itself a bridge, has no master, and is allowed to be bridged. It allocates a `struct net_bridge_port`, joins the device, enables all-multicast, creates kobject/sysfs state, enables netpoll, installs the bridge RX handler, links the bridge as upper master, disables LRO, adds the port to `br->port_list` under RCU, adjusts promiscuity/static FDB filters, headroom, local FDB entries, VLAN state, STP state, notifications, MTU, and master features. Each failure label unwinds only the pieces already installed.
- `del_nbp()` is the inverse port teardown. It removes sysfs links, clears promiscuity or static filters, disables STP, deletes MRP and CFM state, notifies link deletion, removes the port from the RCU list, updates headroom, flushes VLANs and FDB entries, processes deferred switchdev work, clears backup links, unlinks the upper device, clears `IFF_BRIDGE_PORT`, unregisters the RX handler, deletes multicast context, removes kobject state, disables netpoll, and frees through RCU.
- `br_dev_delete()` deletes all ports, uninitializes MST, recalculates neighbour suppression, removes bridge-local FDB entries, cancels FDB GC, removes bridge sysfs, and queues netdevice unregister.
- `br_port_carrier_check()` updates path cost from ethtool link speed when not admin-set and enables/disables STP state when lower carrier changes and the bridge is running.
- `br_manage_promisc()` decides whether ports can leave promiscuous mode based on bridge promiscuity, VLAN filtering, auto-port count, and unicast-filter support. Static FDB entries are synced to hardware filters before clearing promiscuity.

State and persistence behavior:

- Port membership persists in `br->port_list` and lower device upper links until `br_del_if()`, bridge deletion, or error unwind. Readers use RCU; administrative mutation is under RTNL.
- Port objects have kobject lifetime plus an RCU grace period before final `netdev_put()` and free. The RX handler marks the lower netdevice as a bridge port for `br_port_get_*()` helpers.
- Bridge-wide `auto_cnt`, needed headroom, MTU user flag, local FDB entries, multicast contexts, VLAN contexts, STP timers, MRP/CFM state, and backup redirection counters are updated as derived runtime state.
- No disk persistence is involved; userspace must recreate bridge topology after restart.

Dependencies and integration points:

- This file connects rtnetlink/ioctl bridge operations to netdevice core, sysfs, kobjects, STP, FDB, VLAN, multicast snooping, MRP, CFM, switchdev, DSA RX-handler selection, netpoll, ethtool, and net namespace ownership.
- `br_ioctl.c` calls `br_add_bridge()`, `br_del_bridge()`, `br_add_if()`, and `br_del_if()` for legacy interfaces.
- `br_input.c` depends on the RX handler installed here and on `IFF_BRIDGE_PORT`.
- `br_fdb.c` is called for local address insertion, port flushing, and static filter sync/unsync.

Risks and edge cases:

- The `br_add_if()` unwind path is long and order-sensitive. A new resource added in the middle must be unwound in the correct reverse order to avoid leaks, stale upper links, or active RX handlers on rejected devices.
- Promiscuity optimization depends on device `IFF_UNICAST_FLT` capacity and static FDB sync success. Failure can reduce filtering precision or require promiscuous fallback.
- Port deletion must coordinate RCU packet readers, switchdev deferred work, netpoll, sysfs/kobject lifetime, and netdevice references.
- Bridge MTU and headroom are derived from member ports unless user-set; adding/removing unusual devices can change bridge packet constraints.
- Backup-port counters must be cleared both for a port's own backup and for other ports redirecting to it.

Test signals:

- Add and remove valid and invalid lower devices, including non-Ethernet, bridge-as-port, busy-master, `IFF_DONT_BRIDGE`, and devices with RX handler conflicts.
- Verify error-unwind paths with injected failures in sysfs, netpoll, upper-link, VLAN initialization, and address notification.
- Check port carrier transitions update STP state and path cost.
- Validate static FDB filter sync when toggling VLAN filtering, bridge promiscuity, and port flags.
- Confirm bridge MTU/headroom/features after adding and deleting ports with different MTUs, headrooms, and feature sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_input.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_input.c

Purpose: implements ingress processing for bridge ports. It is the bridge RX handler, validates incoming frames, handles reserved link-local MACs, invokes bridge netfilter pre-routing/local-in hooks, applies VLAN ingress policy, learns source MACs, enforces locked-port/MAB policy, integrates multicast snooping and neighbour suppression, performs FDB lookup, forwards/floods frames, and passes frames up to the bridge netdevice when local delivery is needed.

Important APIs, types, and functions:

- `br_get_rx_handler()` returns either `br_handle_frame()` or a DSA dummy handler.
- `br_handle_frame()` is installed as the lower device RX handler and decides whether the bridge consumes or passes an skb.
- `br_handle_frame_finish()` is the main post-netfilter ingress bridge pipeline and is exported.
- `br_pass_frame_up()` delivers an skb to the bridge device through `NF_BR_LOCAL_IN` and `netif_receive_skb()`.
- `nf_hook_bridge_pre()` runs `NF_BR_PRE_ROUTING`, including manual queue handling when bridge netfilter is enabled.
- `br_add_frame()` and `br_del_frame()` maintain a bridge-private list of protocol frame handlers, used by MRP.

Core control flow:

- `br_handle_frame()` ignores loopback skbs, drops invalid source MAC addresses, obtains a writable shared skb, clears the bridge skb control block, handles VLAN tunnel metadata, and checks reserved link-local destinations. STP and LLDP addresses are passed locally or selectively forwarded based on group forward masks; pause frames are dropped.
- Before normal forwarding, registered bridge frame-type handlers are consulted. If an MRP handler consumes an ETH_P_MRP frame, bridge normal forwarding is bypassed.
- For regular frames, non-MST ports must be in forwarding or learning state before entering `nf_hook_bridge_pre()`. With MST enabled, state filtering is deferred to VLAN ingress logic because state is per-MSTI/VLAN.
- `nf_hook_bridge_pre()` either runs bridge pre-routing hooks, handles `br_netfilter_broute` pass-through, queue/drop/stolen verdicts, or directly calls `br_handle_frame_finish()`.
- `br_handle_frame_finish()` obtains the bridge port, selects effective STP state, calls `br_allowed_ingress()` to validate VLAN and update VID/state/vlan output, enforces locked-port and MAB behavior, marks switchdev source information, learns the source with `br_fdb_update()` when enabled, classifies destination as unicast/multicast/broadcast, handles IGMP/MLD receive logic, and drops learning-state frames after learning.
- For unicast, it looks up the destination FDB entry by `(dest, vid)` with an optional fallback to VLAN 0 local entries. Local entries go to `br_pass_frame_up()`, non-local known entries go to `br_forward()`, and unknown entries flood.
- For multicast, it obtains the MDB entry, decides whether local receive is required based on host joins, router status, querier state, and all-multicast flags, then uses `br_multicast_flood()` when there is a hit or `br_flood()` otherwise. Broadcast always forces local receive.
- If `local_rcv` is true after forwarding/flooding, the original skb is delivered up through the bridge device.

State and persistence behavior:

- Persistent bridge state is updated through FDB learning (`updated`, `dst`, flags), locked MAB entries, multicast snooping state, neighbour suppression side effects, and per-packet statistics. This file itself owns transient skb control fields such as `brdev`, `promisc`, `src_port_isolated`, `proxyarp_replied`, and bridge netfilter broute state.
- Port state, VLAN state, bridge options, FDB entries, MDB entries, and multicast router state are consumed under RCU. Packet ownership transfers to forwarding, flooding, netfilter, or local receive paths.
- Local delivery resets switchdev offload marks before stacking another bridge above this one, avoiding offload-state leakage.

Dependencies and integration points:

- Depends on `br_fdb.c` for learning and destination lookup, `br_forward.c` for egress, VLAN helpers for ingress/egress policy, multicast snooping for IGMP/MLD/MDB decisions, neighbour suppression/proxy ARP, bridge netfilter, DSA, switchdev, and MRP frame-type registration.
- `br_if.c` installs this handler and uses the dummy handler for DSA ports so hardware bridging can coexist with packet-type handlers.
- Netfilter integration spans `NF_BR_PRE_ROUTING` and `NF_BR_LOCAL_IN`; bridge netfilter can reroute frames away from bridge forwarding through broute.

Risks and edge cases:

- Ingress ordering is security-sensitive. Source learning happens only after VLAN filtering and locked-port checks to reduce spoofing. Moving learning earlier could poison the FDB.
- Locked ports combine FDB lookup, locked flag refresh, MAB entry creation, and no-roaming behavior. Incorrect handling can bypass authentication or break legitimate authorization refresh.
- MST defers STP filtering until VLAN ingress state is known; applying classic port state too early would break per-MSTI forwarding.
- skb ownership across netfilter verdicts, forwarding, flooding, and local receive is easy to get wrong, especially with broute or queued packets.
- Reserved link-local MAC handling must preserve standards behavior for STP, pause, LLDP, and selectively forwarded group addresses.

Test signals:

- Test invalid source MAC drops, link-local reserved MAC behavior, STP state filtering, and MST per-VLAN state filtering.
- Exercise VLAN ingress failures, FDB learning, known unicast, unknown unicast flood, local MAC delivery, broadcast local receive, and promiscuous bridge receive.
- Validate locked-port and MAB behavior: miss creates locked entry, mismatch drops, locked match refreshes and drops, authorized entry forwards.
- Test bridge netfilter accept/drop/queue/broute decisions and local-in delivery.
- Verify multicast receive with IGMP/MLD, MDB hits, host joins, router ports, all-multicast, and no-querier cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_ioctl.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_ioctl.c

Purpose: preserves the legacy bridge ioctl ABI. It supports old `brctl`-style bridge creation/deletion, bridge listing, port add/delete, bridge and port information queries, STP and timer configuration, path cost and priority changes, and old-format FDB dumps. Newer control-plane features live in rtnetlink, but this file keeps compatibility for `SIOCGIFBR`, `SIOCSIFBR`, `SIOCBRADDBR`, `SIOCBRDELBR`, `SIOCBRADDIF`, `SIOCBRDELIF`, and `SIOCDEVPRIVATE`.

Important APIs, types, and functions:

- `br_ioctl_stub()` handles deviceless bridge ioctls and add/delete-port ioctls under RTNL.
- `br_dev_siocdevprivate()` handles deprecated per-bridge private ioctls.
- `old_deviceless()` implements old global bridge commands such as get version, list bridges, add bridge, and delete bridge.
- Helper functions include `br_dev_read_uargs()`, `get_bridge_ifindices()`, `get_port_ifindices()`, `get_fdb_entries()`, and `add_del_if()`.
- Legacy ABI structures include `struct __bridge_info`, `struct __port_info`, and `struct __fdb_entry` from bridge UAPI headers.

Core control flow:

- `br_dev_read_uargs()` reads 2 to 4 unsigned long arguments from user memory and handles 32-bit compat syscalls by copying `unsigned int` arguments and translating the pointer argument with `compat_ptr()`.
- `br_dev_siocdevprivate()` decodes `BRCTL_*` commands on a bridge netdevice. Add/delete interface calls `add_del_if()`. Information commands snapshot bridge or port STP fields and timer values under RCU and copy to userspace. Set commands require `CAP_NET_ADMIN` in the bridge net namespace, call STP/timer setter functions, and notify either a port link update or bridge device state change on success.
- `get_fdb_entries()` caps the request to one page of `struct __fdb_entry`, allocates a temporary kernel buffer, fills it with `br_fdb_fillbuf()`, and copies only the returned number of records to userspace.
- `old_deviceless()` handles global commands. It lists bridge ifindices by walking netdevices under RCU, and creates/deletes bridge devices after copying an IFNAMSIZ name from userspace.
- `br_ioctl_stub()` performs early capability and ifreq parsing for add/delete-port commands, strips alias suffixes after `:`, takes RTNL, dispatches to global or bridge-specific operations, and releases RTNL.

State and persistence behavior:

- This file does not own long-lived state. It reads bridge, port, timer, and FDB state and mutates bridge topology or STP configuration by delegating to `br_add_bridge()`, `br_del_bridge()`, `br_add_if()`, `br_del_if()`, and STP setter functions.
- It preserves ABI quirks such as page-sized FDB dump limits, port number split into low/high fields, default port-list count of 256, and 32/64-bit compatibility handling.
- All topology-changing ioctl operations are serialized by RTNL or by the callee's expected locking. Information queries use RCU where appropriate.

Dependencies and integration points:

- Depends on net namespace capability checks, user-copy helpers, compat syscall support, rtnetlink locking, bridge STP/timer APIs, bridge lifecycle from `br_if.c`, and FDB export from `br_fdb.c`.
- This is an alternative control plane to rtnetlink. It must not expose features that only rtnetlink can configure, but it must keep old behavior stable.

Risks and edge cases:

- User pointer handling is the main risk. Argument counts, compat translation, copy sizes, IFNAMSIZ termination, and page-sized allocations protect old ABI paths from overflows and bad pointers.
- `args[2] >= 2048` in bridge listing avoids excessive allocation, while FDB dumping clamps to `PAGE_SIZE / sizeof(struct __fdb_entry)`.
- Deviceless add/delete bridge commands operate by name and require the target bridge to be down for deletion through `br_del_bridge()`.
- Setters notify state changes only after successful mutation; missing notification would leave old tools with stale state.
- The interface is deprecated and incomplete compared with rtnetlink, so tests should focus on compatibility, not feature parity.

Test signals:

- Run old `brctl` or ioctl-based tests for addbr, delbr, addif, delif, show bridges, showmacs, showstp, setageing, setfd, sethello, setmaxage, stp on/off, setbridgeprio, setportprio, and setpathcost.
- Exercise 32-bit compat ioctl calls on a 64-bit kernel if available.
- Verify permission failures for unprivileged users and namespace-scoped `CAP_NET_ADMIN`.
- Test bad pointers, too few or too many arguments, negative port counts, oversized bridge-list requests, nonexistent devices, and non-bridge targets.
- Compare old FDB dump output against rtnetlink FDB state for normal dynamic and static entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mdb.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_mdb.c

Purpose: implements rtnetlink dump, notification, add, delete, flush, and get support for the bridge multicast database (MDB) and multicast router ports. It bridges user-visible `RTM_*MDB` messages to internal multicast snooping state, including host joins, per-port group membership, router-port timers, VLAN multicast snooping contexts, source-specific multicast, protocol tags, and switchdev notification.

Important APIs, types, and functions:

- Dump/fill APIs: `br_mdb_dump()`, `br_mdb_fill_info()`, `br_rports_size()`, `br_rports_fill_info()`, `__mdb_fill_info()`, and `__mdb_fill_srcs()`.
- Notification APIs: `br_mdb_notify()`, `br_mdb_flag_change_notify()`, and `br_rtr_notify()`.
- Mutation APIs: `br_mdb_add()`, `br_mdb_del()`, `br_mdb_del_bulk()`, and helpers for `(*,G)`, `(S,G)`, source-list replacement, and host joins.
- Query API: `br_mdb_get()`.
- Key internal structures include `struct net_bridge_mdb_entry`, `struct net_bridge_port_group`, `struct net_bridge_group_src`, `struct br_ip`, `struct br_mdb_config`, and `struct br_mdb_flush_desc`.

Core control flow:

- Router-port dump walks bridge or VLAN multicast contexts and emits per-port router attributes: ifindex, timer, router type, IPv4/IPv6 timers, and optional VID.
- MDB dump emits `RTM_GETMDB` replies with nested `MDBA_MDB`/`MDBA_MDB_ENTRY`/`MDBA_MDB_ENTRY_INFO` attributes. It handles host-joined entries, port groups, timers, flags, source address, routing protocol, source lists, and group mode depending on IGMP/MLD version.
- `br_mdb_add()` initializes a `br_mdb_config` from netlink attributes, validates bridge running state and multicast enablement, resolves the target port if not a host join, rejects invalid IP/L2/source combinations, expands VID 0 across VLAN memberships when VLAN filtering is enabled, and calls `__br_mdb_add()` under `multicast_lock`.
- `br_mdb_add_group()` chooses the correct bridge or VLAN multicast context, creates or finds the MDB group, handles bridge-host joins, and dispatches to `br_mdb_add_group_star_g()` for `(*,G)` or `br_mdb_add_group_sg()` for `(S,G)`.
- Source-specific multicast support creates source entries and also installs corresponding `(S,G)` forwarding entries. `(*,G)` EXCLUDE groups update related `(S,G)` entries so replication remains correct. Replacement marks existing sources for deletion, adds the requested set, then removes old marked sources.
- `br_mdb_del()` builds the same config, optionally expands across VLANs, and removes either a host join or a matching port group under `multicast_lock`.
- `br_mdb_del_bulk()` builds a flush descriptor from ifindex, VID, state and optional state mask, and `RTPROT`; it scans all MDB entries and removes matching host joins and port groups.
- `br_mdb_get()` parses a group, locks multicast state while sizing and filling the reply, and unicasts an `RTM_NEWMDB`-formatted response.

State and persistence behavior:

- MDB state is runtime multicast snooping state held in `br->mdb_list`, each MDB entry's host flag/timer, RCU-linked port groups, per-port source lists, router-port lists, and optional VLAN multicast contexts.
- `br->multicast_lock` serializes MDB mutation and size-then-fill get replies. RCU protects dump and packet-path readers, with lockdep annotations for multicast lock cases.
- Temporary entries use timers based on multicast membership intervals or group membership intervals. Permanent entries delete timers. Host leave can restart the group timer when no ports remain.
- Notifications to `RTNLGRP_MDB` and switchdev are the external observation path; switchdev notification can be suppressed for flag-only notifications.

Dependencies and integration points:

- Depends heavily on multicast core helpers in other bridge files: `br_multicast_new_group()`, `br_multicast_new_port_group()`, `br_multicast_del_pg()`, `br_multicast_host_join()`, `br_multicast_host_leave()`, `br_multicast_star_g_handle_mode()`, source-list helpers, router-port helpers, and multicast context selection.
- `br_forward.c` consumes MDB port groups for multicast replication. `br_input.c` resolves MDB entries on multicast ingress.
- Netlink policies validate MDB entry attributes, source attributes, group modes, state masks, and protocol tags. Switchdev receives MDB add/delete notifications for hardware programming.
- VLAN snooping integration requires a configured VID and enabled VLAN multicast context when `BROPT_MCAST_VLAN_SNOOPING_ENABLED` is set.

Risks and edge cases:

- Source-specific multicast is the most complex area. Failing to maintain the derived `(S,G)` forwarding entries for `(*,G)` source lists or EXCLUDE mode can produce multicast leaks or drops.
- Size-then-fill netlink replies must hold the multicast lock where entries can change; dumps tolerate RCU iteration but need correct continuation indexes.
- VID 0 expansion mutates `cfg.entry->vid` and `cfg.group.vid` while iterating VLANs. Errors can leave a partial set of VLAN entries.
- L2 MDB entries are only allowed as permanent entries; IP host joins cannot carry flags or source-specific groups.
- VLAN multicast snooping rejects non-VID entries and disabled VLAN contexts; callers must surface these extack messages cleanly.

Test signals:

- Test `bridge mdb add/del/show/get/flush` for IPv4, IPv6, and L2 groups; host joins and port joins; permanent and temporary entries; VLAN-specific and VID 0 expansion.
- Cover IGMPv3/MLDv2 source lists, INCLUDE/EXCLUDE mode, source replacement, duplicate sources, empty INCLUDE rejection, and invalid multicast source addresses.
- Verify router-port dumps and notifications for IPv4, IPv6, VLAN contexts, and timer values.
- Validate bulk flush by port, bridge host entry, VID, permanent state mask, and `RTPROT`.
- Observe `RTNLGRP_MDB` events and switchdev MDB notifications, and test packet replication through `br_multicast_flood()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mrp.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_mrp.c

Purpose: implements bridge Media Redundancy Protocol (MRP) runtime behavior. It creates and deletes MRP ring instances, assigns primary/secondary/interconnect ports, manages ring and interconnect states and roles, generates or monitors MRP test frames in software when hardware does not offload them, registers an ETH_P_MRP frame handler, and forwards or consumes MRP control frames according to ring and interconnect roles.

Important APIs, types, and functions:

- Instance lifecycle: `br_mrp_add()`, `br_mrp_del()`, `br_mrp_port_del()`, and `br_mrp_enabled()`.
- Configuration APIs: `br_mrp_set_port_state()`, `br_mrp_set_port_role()`, `br_mrp_set_ring_state()`, `br_mrp_set_ring_role()`, `br_mrp_start_test()`, `br_mrp_set_in_state()`, `br_mrp_set_in_role()`, and `br_mrp_start_in_test()`.
- Frame handling: `br_mrp_process()`, `br_mrp_rcv()`, `br_mrp_mrm_process()`, `br_mrp_mra_process()`, and `br_mrp_mim_process()`.
- Timed software work: `br_mrp_test_work_expired()` and `br_mrp_in_test_work_expired()`.
- skb construction helpers create ring test and interconnect test frames with MRP TLVs and common headers.
- Important state lives in `struct br_mrp`: ring ID, interconnect ID, port RCU pointers, role/state fields, transition counters, sequence ID, test intervals/end times/max-miss counters, monitor mode, and offload flags.

Core control flow:

- `br_mrp_add()` validates unique ring ID, valid primary/secondary ports, and that no selected port is already part of another MRP instance. It allocates `struct br_mrp`, marks the two ports forwarding and `BR_MRP_AWARE`, registers the MRP frame type if this is the first instance, initializes delayed work, adds the instance to `br->mrp_list`, and asks switchdev to add the instance. Failure unwinds through `br_mrp_del_impl()`.
- `br_mrp_del_impl()` cancels software test work, disables hardware/software test generation, disables ring/interconnect roles, deletes switchdev objects, restores ports to normal bridge state, clears `BR_MRP_AWARE`, removes the instance from the RCU list, frees it by RCU, and unregisters the frame type when the list becomes empty.
- Ring role and interconnect role setters call switchdev. If hardware fully handles the role, software detection/generation is suppressed; if hardware supports only software backup, delayed work and software forwarding remain active; if unsupported, configuration fails.
- `br_mrp_start_test()` and `br_mrp_start_in_test()` first attempt switchdev test-frame generation. On software fallback they set interval, end time, max-miss, monitor state, reset miss counters, and queue delayed work on `system_percpu_wq`.
- Test work increments miss counters until max miss; when a closed ring or monitored MRA stops seeing expected frames, it notifies userspace through port-open events. If not in monitor mode, it builds and transmits MRP Test frames on primary and secondary ports. Interconnect test work sends InTest frames on primary, secondary, and interconnect ports.
- `br_mrp_rcv()` handles MRP frames on aware ports. Ring frames are consumed by MRM behavior or monitored by MRA/MRC behavior, then forwarded when role rules allow. Interconnect frames are forwarded or suppressed based on ring port, interconnect port, MIM/MIC role, ring port blocking state, frame TLV type, and whether a received InTest belongs to this MIM.

State and persistence behavior:

- MRP state is per-bridge runtime state in `br->mrp_list`; instances are RCU visible and administratively mutated under RTNL. Port pointers are RCU assignments.
- Port state is directly changed to forwarding/blocking/disabled and `BR_MRP_AWARE` is set while a port participates. Deletion restores normal forwarding or disabled state based on the bridge device running state.
- Sequence IDs and transition counters are monotonic within an instance. Miss counters and timers are transient. Lost continuity flags are set in `br_mrp_netlink.c` notification helpers.
- Software-generated test frames are scheduled only for the requested period; work exits once `test_end` or `in_test_end` is reached.

Dependencies and integration points:

- Netlink parsing and reporting live in `br_mrp_netlink.c`. Hardware offload shims live in `br_mrp_switchdev.c`.
- It registers a custom frame type through `br_add_frame()`/`br_del_frame()` in `br_input.c`, and forwards MRP frames through normal `br_forward()` egress.
- It depends on switchdev MRP objects/attributes, delayed workqueues, RCU, RTNL, bridge port state, and userspace notifications for ring/interconnect open or closed events.
- MRP is rejected by netlink when STP is enabled, so MRP owns loop prevention for its participating ports.

Risks and edge cases:

- Instance teardown must cancel delayed work before freeing the RCU object; otherwise software test work could access freed MRP state.
- Hardware support classification matters. Treating partial support as full hardware offload would stop required software monitoring; treating full support as software could duplicate protocol frames.
- MRP forwarding rules are role-specific and TLV-specific. Incorrect suppression can create loops on a closed ring or break interconnect continuity detection.
- Port uniqueness across primary, secondary, and interconnect roles prevents ambiguous forwarding and teardown; bypassing it could corrupt multiple rings.
- `sizeof(oui)` is used in one option length expression where `oui` is a pointer variable; this should be checked against protocol layout expectations.

Test signals:

- Configure add/delete rings with valid, duplicate, missing, and reused ports. Verify frame handler registration only while instances exist.
- Test MRM, MRC, and MRA roles with hardware full, software-backup, and unsupported switchdev responses.
- Validate software Ring Test and InTest frame generation intervals, period expiry, sequence increments, and miss/open notifications.
- Feed ring and interconnect TLV frames for MIM/MIC/MRA/MRM combinations and verify forwarding destinations.
- Delete ports participating in MRP and confirm work cancellation, port state restoration, switchdev cleanup, and RCU-safe teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mrp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mrp_netlink.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_mrp_netlink.c

Purpose: provides rtnetlink parsing, validation, reporting, and user notification glue for bridge MRP. It translates nested `IFLA_BRIDGE_MRP_*` attributes into typed bridge MRP operations, fills link information for configured MRP instances, and toggles per-port continuity-loss flags that are reported through bridge link notifications.

Important APIs, types, and functions:

- `br_mrp_parse()` is the main setter/deleter entry point called from bridge link handling.
- `br_mrp_fill_info()` emits configured MRP instances into `IFLA_BRIDGE_MRP` nested attributes.
- Notification helpers `br_mrp_ring_port_open()` and `br_mrp_in_port_open()` update port flags and send `RTM_NEWLINK`.
- Parser helpers cover instance add/delete, port state, port role, ring state, ring role, ring test start, interconnect state, interconnect role, and interconnect test start.
- Netlink policies define required nested attribute types and reject unspecified attributes.

Core control flow:

- `br_mrp_parse()` first corrects the bridge pointer when called for a port and rejects MRP configuration if STP is enabled. It parses the top-level nested MRP attributes and processes each present sub-command in a fixed order, returning immediately on the first error.
- Instance parsing requires ring ID plus primary and secondary ifindices, defaults priority to `MRP_DEFAULT_PRIO` if absent, and calls `br_mrp_add()` for `RTM_SETLINK` or `br_mrp_del()` otherwise.
- Port-level parsers require a valid port pointer from the caller and pass role/state values to `br_mrp_set_port_state()` or `br_mrp_set_port_role()`.
- Ring and interconnect parsers build small typed structures, require IDs and state/role fields, then call the matching runtime functions in `br_mrp.c`.
- Start-test parsers enforce minimum interval of 1 through netlink policy, require interval, max-miss, and period fields, default monitor to false for ring tests, and call the software/hardware start functions.
- `br_mrp_fill_info()` iterates `br->mrp_list` under RCU assumptions and emits ring ID, participating ifindices, priority, ring state/role, test interval/max-miss/monitor, interconnect state/role, and interconnect test parameters for each instance.
- `br_mrp_ring_port_open()` and `br_mrp_in_port_open()` look up the bridge port by device, set or clear `BR_MRP_LOST_CONT` or `BR_MRP_LOST_IN_CONT`, and notify link listeners.

State and persistence behavior:

- This file owns no independent durable state. It mutates `struct br_mrp` and `struct net_bridge_port` state through runtime APIs and port flags.
- Netlink extack messages are the main diagnostics for missing attributes, STP conflicts, and invalid parser inputs.
- MRP info dumps reflect current in-kernel runtime fields; they are not reconstructed from userspace configuration.

Dependencies and integration points:

- Relies on UAPI definitions in `uapi/linux/mrp_bridge.h`, generic netlink/rtnetlink nested attribute helpers, bridge runtime functions in `br_mrp.c`, bridge port lookup from `br_private.h`, and link notifications through `br_ifinfo_notify()`.
- The parser is part of bridge link configuration alongside VLAN, STP, and other bridge attributes.
- MRP cannot coexist with STP according to this control-plane guard.

Risks and edge cases:

- `br_mrp_parse()` can receive either bridge-level or port-level requests. Some attributes require a port pointer; callers must only provide them in the correct context.
- Top-level processing is sequential and not transactional across multiple nested attributes. If a later attribute fails, earlier changes remain applied.
- Attribute presence validation is manual. Missing required fields produce extack errors; unexpected command combinations can still depend on lower-level runtime validation.
- `br_mrp_fill_info()` must size skb space correctly in its caller; failure paths cancel the right nested attributes to avoid malformed netlink messages.
- Continuity notification helpers use `br_port_get_rcu()` and mutate flags; callers should already be in an RCU-safe context or otherwise guarantee object lifetime.

Test signals:

- Configure every MRP nested attribute through `ip link`/rtnetlink and verify success, extack strings for missing fields, and error paths for STP-enabled bridges.
- Dump link info after each operation and confirm ring IDs, ifindices, roles, states, intervals, max-miss values, and monitor flags.
- Send multi-attribute requests where a later operation fails and verify the non-transactional resulting state.
- Trigger ring and interconnect open/closed notifications and observe `BR_MRP_LOST_CONT` / `BR_MRP_LOST_IN_CONT` reflected in link events.
- Test port-context misuse, invalid ifindices, duplicate IDs, and disabled interconnect role handling through lower runtime validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mrp_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mrp_switchdev.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_mrp_switchdev.c

Purpose: is the switchdev adapter for bridge MRP. It converts bridge MRP instance, role, state, test generation, and port role/state requests into switchdev objects or attributes, and reports whether hardware fully handled the operation, supports software-backup mode, or cannot support the request.

Important APIs, types, and functions:

- Instance object operations: `br_mrp_switchdev_add()` and `br_mrp_switchdev_del()`.
- Ring operations: `br_mrp_switchdev_set_ring_role()`, `br_mrp_switchdev_send_ring_test()`, and `br_mrp_switchdev_set_ring_state()`.
- Interconnect operations: `br_mrp_switchdev_set_in_role()`, `br_mrp_switchdev_send_in_test()`, and `br_mrp_switchdev_set_in_state()`.
- Port attribute operations: `br_mrp_port_switchdev_set_state()` and `br_mrp_port_switchdev_set_role()`.
- `br_mrp_switchdev_port_obj()` is the common add/delete wrapper that maps switchdev return codes to `enum br_mrp_hw_support`.

Core control flow:

- When `CONFIG_NET_SWITCHDEV` is disabled, operations that can fall back to software return `BR_MRP_SW`, while pure state-setting helpers return success. This lets `br_mrp.c` run software protocol logic without requiring hardware support.
- `br_mrp_switchdev_port_obj()` calls `switchdev_port_obj_add()` or `switchdev_port_obj_del()` on the bridge device. Success means hardware handled the object (`BR_MRP_HW`). `-EOPNOTSUPP` means software fallback is allowed (`BR_MRP_SW`). Any other error means no usable support (`BR_MRP_NONE`).
- `br_mrp_switchdev_add()` sends `SWITCHDEV_OBJ_ID_MRP` with primary/secondary port devices, ring ID, and priority. Delete sends the same object ID with null ports and ring ID.
- Ring role and interconnect role setters first try full hardware offload. If full offload is unsupported, they retry with `sw_backup = true`, asking hardware to install the pieces needed while software runs protocol behavior. Success in that retry returns `BR_MRP_SW`.
- Ring and interconnect test generation create switchdev test objects with interval, max-miss, IDs, period, and monitor flags. A zero interval deletes/stops the object.
- Port state and role helpers send switchdev attributes `SWITCHDEV_ATTR_ID_PORT_STP_STATE` and `SWITCHDEV_ATTR_ID_MRP_PORT_ROLE` to the physical port.

State and persistence behavior:

- This file does not store state. It reflects the current `struct br_mrp` and port fields into switchdev driver state and reports support level to callers.
- Hardware state persists in the driver until corresponding delete/disable calls or device teardown. Software state such as `ring_role_offloaded` is stored by callers in `br_mrp.c`.

Dependencies and integration points:

- Depends on switchdev object IDs for MRP, ring role/test/state, interconnect role/test/state, and switchdev attributes for port STP state and MRP port role.
- Called exclusively by `br_mrp.c` during MRP configuration, teardown, and software/hardware fallback decisions.
- Uses `rtnl_dereference()` for MRP port pointers, matching the administrative locking expected by the caller.

Risks and edge cases:

- Return-code mapping defines runtime behavior. Treating non-`EOPNOTSUPP` errors as fallback would hide real hardware programming failures; treating `EOPNOTSUPP` as fatal would disable software MRP unnecessarily.
- The interconnect role fallback path differs from ring role logic: the first helper returns on any support value other than `BR_MRP_NONE`, so review is needed to ensure retry-on-unsupported semantics match the intended switchdev contract.
- Role disable paths use object delete operations and may dereference `i_port`; callers must ensure the port exists when disabling interconnect role.
- Null `extack` in several switchdev calls limits user diagnostics for hardware failures.

Test signals:

- Use switchdev-capable and non-switchdev bridge ports to verify full hardware, software-backup, and unsupported outcomes.
- Mock or instrument switchdev drivers to return success, `-EOPNOTSUPP`, and other errors for each object type.
- Confirm MRP add/delete objects carry correct ring ID, priority, and port devices.
- Verify ring/interconnect test start and stop issue add/delete object operations based on interval.
- Check port STP state and MRP port role attributes are sent when MRP runtime state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mrp_switchdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mst.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_mst.c

Purpose: implements bridge Multiple Spanning Tree (MST) support. It allows VLANs to be assigned to MST instances, stores per-port per-MSTI forwarding states through VLAN state, exposes MST state through rtnetlink and exported APIs, gates MST mode changes, and notifies switchdev hardware of MST enablement, VLAN-to-MSTI mappings, and per-port MST states.

Important APIs, types, and functions:

- Mode APIs: `br_mst_enabled()`, `br_mst_set_enabled()`, and `br_mst_uninit()`.
- Query APIs: `br_mst_get_info()` returns VLAN membership for an MSTI and `br_mst_get_state()` returns a port's state for an MSTI.
- State mutation: `br_mst_set_state()` applies an MSTI state to all VLANs on a port whose bridge VLAN maps to that MSTI.
- VLAN mapping: `br_mst_vlan_set_msti()` changes a bridge VLAN's MSTI and synchronizes port VLAN states.
- Initialization and netlink helpers: `br_mst_vlan_init_state()`, `br_mst_info_size()`, `br_mst_fill_info()`, and `br_mst_process()`.
- `DEFINE_STATIC_KEY_FALSE(br_mst_used)` provides a jump-label optimization for MST checks in hot paths.

Core control flow:

- `br_mst_set_enabled()` refuses to toggle MST while any port has VLANs configured, because existing VLAN state would need migration. It sends `SWITCHDEV_ATTR_ID_BRIDGE_MST`, updates the static key, and toggles `BROPT_MST_ENABLED`.
- `br_mst_uninit()` decrements the static key if a bridge is deleted while MST is enabled.
- `br_mst_vlan_init_state()` starts all VLANs in MSTI 0. Bridge VLANs are forwarding; port VLANs inherit the port's current STP state.
- `br_mst_vlan_set_msti()` sends `SWITCHDEV_ATTR_ID_VLAN_MSTI`, updates the bridge VLAN's `msti`, and for each port that has that VID, calls `br_mst_vlan_sync_state()`. Sync inherits an existing state for the same MSTI on that port, or disables the VLAN if this is the first VLAN in that MSTI.
- `br_mst_set_state()` optionally sends `SWITCHDEV_ATTR_ID_PORT_MST_STATE` for nonzero MSTIs, then walks the port VLAN list under RCU and updates each VLAN whose master bridge VLAN maps to the requested MSTI. `br_mst_vlan_set_state()` also updates PVID state when needed.
- `br_mst_process()` parses nested `IFLA_BRIDGE_MST_ENTRY` attributes, requires MST mode enabled, validates MSTI and state ranges, and applies each entry through `br_mst_set_state()`.
- `br_mst_fill_info()` emits one netlink entry per unique MSTI in a VLAN group, reporting MSTI and current state.

State and persistence behavior:

- MST mode is stored as a bridge option bit plus the global static key count. VLAN-to-MSTI mapping is stored in bridge VLAN objects. Per-port MST state is represented by each port VLAN's `state`.
- No separate MST database exists; MST state is derived from VLAN lists and bridge VLAN mappings.
- Switchdev hardware state is updated best-effort; `-EOPNOTSUPP` is accepted for software operation, while other errors abort changes.
- Administrative operations expect RTNL or RCU context as annotated by the functions.

Dependencies and integration points:

- `br_input.c` and `br_forward.c` use MST-aware checks so per-VLAN state can replace classic per-port STP state when MST is enabled.
- VLAN code owns VLAN objects, PVID state, and master/port VLAN relationships used here.
- Switchdev drivers can offload bridge MST enablement, VLAN MSTI mapping, and per-port MSTI state.
- Rtnetlink bridge attributes use `br_mst_process()`, `br_mst_info_size()`, and `br_mst_fill_info()` to configure and report MST.

Risks and edge cases:

- MST mode cannot be toggled with VLANs on ports. Tests must verify this guard because changing mode with live VLANs could leave inconsistent per-VLAN states.
- MSTI 0 is reserved for CST in netlink policy; per-MST switchdev state notifications are skipped for 0 and handled by normal STP state.
- State synchronization when moving a VLAN to a new MSTI intentionally disables it if no peer VLAN on that port has an established state. Misunderstanding this can look like a forwarding regression.
- The static key must be balanced across enable, disable, and bridge deletion. Unbalanced increments would keep MST hot-path code enabled globally.
- Netlink fill emits one entry per unique MSTI by bitmap. Large or sparse MSTI mappings should be checked against skb sizing.

Test signals:

- Enable/disable MST on bridges with and without configured port VLANs and verify extack/error behavior.
- Assign VLANs to MSTIs, query VLAN bitmaps with `br_mst_get_info()`, and verify per-port `br_mst_get_state()`.
- Set MST states through rtnetlink and confirm ingress/egress forwarding follows VLAN state rather than only port state.
- Validate switchdev notifications for bridge MST mode, VLAN MSTI mapping, and nonzero per-port MST state.
- Dump MST netlink info and ensure duplicate MSTIs are emitted once with the expected state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mst.c -->
