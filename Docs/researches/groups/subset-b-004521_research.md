# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell subset-b-004521 research

Work item `subset-b-004521` covers Marvell Prestera router, RX/TX, SPAN, and switchdev support plus two Marvell Ethernet drivers. Each source section is delimited for reconciliation into the mapped source-tree-aligned report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_router_hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_router_hw.c

## Purpose
This file implements the Prestera router hardware object layer. It translates kernel routing concepts into hardware virtual routers, router interfaces, nexthop-neighbor objects, nexthop groups, and LPM FIB entries. The code is deliberately lower level than a route manager: it owns allocations, hardware IDs, hash-table lookups, and teardown ordering for objects that other Prestera routing code uses.

## Important APIs, types, and functions
The exported entry points are `prestera_router_hw_init()`, `prestera_router_hw_fini()`, `prestera_rif_entry_find/create/destroy()`, `prestera_nh_neigh_find/get/put/set()`, `prestera_nh_neigh_util_hw_state()`, and `prestera_fib_node_find/create/destroy()`.

Important internal helpers include `prestera_vr_get()` and `prestera_vr_put()` for table-id to hardware-VR refcounting, `__prestera_rif_entry_key_copy()` for canonical RIF keys, `__prestera_nexthop_group_create/destroy/find()`, `prestera_nexthop_group_set()`, and `prestera_nexthop_group_util_hw_state()`.

The file uses three `rhashtable` instances in `sw->router`: one each for FIB nodes, nexthop neighbors, and nexthop groups. Virtual routers and RIF entries are tracked by lists.

## Control flow
Initialization creates the nexthop-neighbor, nexthop-group, and FIB hash tables, then initializes VR and RIF lists. RIF creation canonicalizes the interface key, gets or creates the VR for the route table, calls `prestera_hw_rif_create()`, and appends the RIF to the router list. RIF destruction deletes the hardware RIF, releases the VR, and frees the entry.

Nexthop groups are built from up to `PRESTERA_NHGR_SIZE_MAX` neighbor keys. Creation gets each neighbor object, links a per-group head into each neighbor's group list, creates a hardware nexthop group, programs current neighbor information into hardware, inserts the group into the hash table, and clears its cached hardware-state bit. Neighbor updates call `prestera_nexthop_group_set()` for every dependent group.

FIB node creation gets the VR, selects a hardware group ID based on route type, optionally gets a nexthop group, calls `prestera_hw_lpm_add()`, then inserts the FIB node into the hash table. Destroy reverses this by deleting the LPM entry, releasing the nexthop group if used, releasing the VR, removing the hash entry, and freeing memory.

## State and persistence behavior
All state is in memory and tied to `struct prestera_switch`. The persistent hardware state is the Prestera ASIC tables programmed through `prestera_hw_*()` calls. Reference counts ensure VRs and nexthop groups survive while RIF/FIB users refer to them. Nexthop neighbors are retained while at least one group references them. The nexthop-group hardware-state cache is refreshed no more often than `PRESTERA_NH_ACTIVE_JIFFER_FILTER` milliseconds to avoid reading transient inactive state too often.

## Dependencies and integration points
This file depends on Linux `rhashtable`, refcounts, jiffies timing, Prestera switch/router storage, `prestera_iface`, and hardware calls from `prestera_hw.h`: VR, RIF, nexthop group, nexthop entries, nexthop-state block, and LPM add/delete. It is consumed by higher Prestera router/neigh/FIB logic and is not a standalone netdev path.

## Risks and edge cases
`prestera_router_hw_init()` returns `0` even if hash-table initialization fails, because the final error path returns `0`; this is a high-risk initialization bug. `prestera_rif_entry_find()` builds canonical key `lk` but compares the original `k` to stored keys, which can miss matches when unused fields differ. FIB programming only uses `key->addr.u.ipv4` for LPM add/delete, so IPv6 types declared in the header are not implemented here. Error unwinds in nexthop group creation must keep neighbor list links and hardware group creation balanced. Hardware-state cache indexing depends on `grp_id` being within `size_tbl_router_nexthop`.

## Test signals
Useful tests include init failure injection for all `rhashtable_init()` calls, route add/delete with duplicate table IDs to verify VR refcounts, duplicate RIF lookup with noncanonical padding, nexthop-neighbor update propagation to multiple groups, group create unwind with partial neighbor acquisition, FIB trap/drop/UC route add/delete, and ASIC mock assertions for LPM and nexthop call ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_router_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_router_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_router_hw.h

## Purpose
This header defines the Prestera router hardware object model and exports the router-hardware API used by the rest of the Prestera driver. It captures software keys, hardware IDs, reference relationships, route actions, and public lifecycle functions for virtual routers, RIFs, nexthop neighbors, nexthop groups, and FIB nodes.

## Important APIs, types, and functions
`struct prestera_vr` maps a kernel FIB table ID to a hardware VR ID and carries a `refcount_t`. `struct prestera_rif_entry` binds a Prestera interface key, VR pointer, MAC address, hardware RIF ID, and router-list node. `struct prestera_ip_addr` is a versioned IPv4/IPv6 union with `PRESTERA_IP_ADDR_PLEN()`. `struct prestera_nh_neigh_key` identifies a neighbor by IP address and RIF-cookie domain. `struct prestera_neigh_info` is the hardware-facing resolved-neighbor payload. `struct prestera_nh_neigh` links a neighbor to dependent nexthop groups. `struct prestera_nexthop_group` holds up to four neighbor keys and per-neighbor linkage. `struct prestera_fib_key`, `struct prestera_fib_info`, and `struct prestera_fib_node` describe route lookup keys and actions.

The exported functions cover object find/get/create/destroy/update operations plus `prestera_router_hw_init()` and `prestera_router_hw_fini()`.

## Control flow
The header shows the intended ownership graph: FIB nodes and RIF entries reference VRs; UC FIB nodes reference nexthop groups; nexthop groups reference nexthop neighbors through `prestera_nh_neigh_head`; neighbor updates can fan out to groups.

## State and persistence behavior
All structures are runtime-only kernel objects. Hardware persistence is represented by fields such as `hw_vr_id`, `hw_id`, and `grp_id`; these IDs are valid only while the driver has successfully programmed the corresponding ASIC resources. The key structs are value keys for list or hash lookup and must be fully canonicalized before use.

## Dependencies and integration points
The header depends on common Prestera definitions such as `struct prestera_switch` and `struct prestera_iface`, Linux list and refcount types, Ethernet address constants, and IP address types. It is the public boundary between router control-plane code and `prestera_router_hw.c`.

## Risks and edge cases
The header advertises IPv6 representation, but the C file's LPM programming path is IPv4-only. `prestera_nh_neigh_key.rif` is a raw cookie pointer; stale or nonunique cookies can collapse or split ARP/ND domains incorrectly. The fixed `PRESTERA_NHGR_SIZE_MAX` of four constrains ECMP width and must match hardware and higher-level assumptions.

## Test signals
Tests should validate key equality/canonicalization, table-ID VR sharing, max-width nexthop group keys, empty neighbor-key termination, IPv6 rejection or support behavior in callers, and ABI consistency between exported prototypes and users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_router_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_rxtx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_rxtx.c

## Purpose
This file implements Prestera packet RX/TX over switch SDMA. It creates DMA descriptor pools and circular RX/TX rings, handles the RX event from firmware/hardware, converts Prestera DSA-tagged CPU packets to normal Linux skbs, adds DSA tags for transmitted packets, and integrates RX processing with NAPI.

## Important APIs, types, and functions
Internal types include `struct prestera_sdma_desc`, `struct prestera_sdma_buf`, `struct prestera_rx_ring`, `struct prestera_tx_ring`, `struct prestera_sdma`, and `struct prestera_rxtx`. Public functions are `prestera_rxtx_switch_init()`, `prestera_rxtx_switch_fini()`, `prestera_rxtx_port_init()`, and `prestera_rxtx_xmit()`.

Key helpers include descriptor initializers, `prestera_sdma_rx_skb_alloc()`, `prestera_sdma_rx_skb_get()`, `prestera_rxtx_process_skb()`, `prestera_sdma_rx_poll()`, `prestera_sdma_rx_init/fini()`, `prestera_sdma_tx_init/fini()`, `prestera_sdma_tx_recycle_work_fn()`, `prestera_rxtx_handle_event()`, and `prestera_sdma_xmit()`.

## Control flow
Switch init allocates `sw->rxtx`, requests SDMA mode from hardware with `prestera_hw_rxtx_init()`, creates a DMA pool for 16-byte descriptors, initializes eight RX rings of 1000 descriptors each, initializes one TX ring, registers the RXTX event handler, creates a dummy NAPI netdev, and enables NAPI.

The RX event handler masks SDMA RX interrupts and schedules NAPI. `prestera_sdma_rx_poll()` walks all RX queues until budget or all queues are done, identifies CPU-owned descriptors, trims the backing skb to descriptor packet length, swaps in a fresh DMA buffer, parses the Prestera DSA header, resolves the ingress `prestera_port`, removes the DSA header with checksum adjustment, restores the Ethernet header layout, applies VLAN accel metadata, reports devlink traps, and batches packets into `netif_receive_skb_list()`.

Transmit starts in `prestera_rxtx_xmit()`, which ensures DSA headroom, pushes the DSA header, shifts destination/source MAC fields, builds the tag, then calls `prestera_sdma_xmit()`. The SDMA TX path serializes with `tx_lock`, maps the skb for DMA, fills descriptor buffer and length, throttles by burst/waiting for the queue start bit, marks the descriptor DMA-owned, starts the TX queue, and schedules recycling work.

## State and persistence behavior
Runtime state consists of descriptor rings, skb pointers, DMA mappings, a work item, a NAPI object, and hardware SDMA registers. No on-disk state is persisted. Descriptor ownership bits are the synchronization contract with hardware, with memory barriers before handing RX/TX descriptors to DMA. TX buffers remain `is_used` until the recycle worker sees CPU ownership and unmaps/frees the skb.

## Dependencies and integration points
The file integrates with `prestera_hw_*` register/event APIs, `prestera_dsa_parse/build()`, `prestera_port_find_by_hwid()`, `prestera_devlink_trap_report()`, Linux DMA pools, NAPI, skb VLAN acceleration, and netdev RX delivery. `prestera_rxtx_port_init()` sets port headroom for DSA tags.

## Risks and edge cases
RX allocation fallback copies from the old buffer if replacing the DMA skb fails; this avoids dropping but adds allocation/copy complexity. `dma_map_single()` for RX uses `skb->len`, which is zero for a newly allocated skb in normal Linux skb semantics; this is suspicious because the intended DMA length is the available buffer size. TX descriptor exhaustion drops packets but still returns `NETDEV_TX_OK`, relying on stats rather than queue backpressure. `prestera_rxtx_xmit()` returns `NET_XMIT_DROP` after modifying skb headroom if DSA build fails, so callers depend on normal ndo semantics for freeing. Large packets above `PRESTERA_SDMA_BUFF_SIZE_MAX` are not supported by this ring format.

## Test signals
Test with mocked SDMA registers and descriptors for RX budget handling, interrupt mask reenable, DSA parse failure, unknown ingress port, VLAN tag propagation, devlink trap reporting, TX descriptor busy drops, burst wait timeout, TX recycle unmap/free, init unwind at each allocation/register step, and port headroom setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_rxtx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_rxtx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_rxtx.h

## Purpose
This header declares the Prestera RX/TX public interface. It lets switch setup code initialize and tear down SDMA packet I/O, lets port setup reserve DSA headroom, and exposes the transmit function used by Prestera netdev operations.

## Important APIs, types, and functions
The header forward-declares `struct prestera_switch` and `struct prestera_port`, includes `<linux/netdevice.h>` for `netdev_tx_t`, and exports `prestera_rxtx_switch_init()`, `prestera_rxtx_switch_fini()`, `prestera_rxtx_port_init()`, and `prestera_rxtx_xmit()`.

## Control flow
Callers are expected to initialize RX/TX once per switch before ports transmit packets, initialize each port to set required headroom, call `prestera_rxtx_xmit()` from the port netdev start-xmit path, and tear down switch RX/TX after ports are stopped.

## State and persistence behavior
The header exposes no state structs; all SDMA state is private to `prestera_rxtx.c` and attached to `sw->rxtx`. There is no persistence.

## Dependencies and integration points
It is the compile-time boundary between Prestera core/port netdev code and the SDMA implementation. The dependency on `netdevice.h` is needed for `struct sk_buff` through declarations and `netdev_tx_t`.

## Risks and edge cases
Because the implementation state is opaque, callers must obey lifecycle ordering. Calling transmit before switch init or after switch fini would dereference missing `sw->rxtx`. Port init currently only sets headroom, so later DSA headroom requirements must keep this API synchronized.

## Test signals
Build tests should catch prototype drift. Runtime tests should verify switch init/fini wraps all port xmit lifetimes and that port netdevs expose enough `needed_headroom` for DSA insertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_rxtx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_span.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_span.c

## Purpose
This file implements Prestera SPAN/mirroring resource management. It allocates hardware SPAN IDs for destination ports, reference-counts those IDs across rules, binds and unbinds SPAN rules to source ports, and keeps a per-switch software list of active SPAN entries.

## Important APIs, types, and functions
Internal state is `struct prestera_span_entry`, containing list linkage, destination port, refcount, and hardware SPAN ID, plus `struct prestera_span`, which stores the owning switch and entry list. Public functions are `prestera_span_init()`, `prestera_span_fini()`, `prestera_span_rule_add()`, and `prestera_span_rule_del()`.

Important helpers include `prestera_span_entry_create()`, `prestera_span_entry_del()`, `prestera_span_entry_find_by_id()`, `prestera_span_entry_find_by_port()`, `prestera_span_get()`, and `prestera_span_put()`.

## Control flow
Initialization allocates `sw->span` and initializes the entry list. Adding a rule rejects an already mirrored binding, gets or allocates a SPAN ID for the destination port via `prestera_hw_span_get()`, binds the source binding port with `prestera_hw_span_bind()`, and stores the ID in `binding->span_id`. Deleting checks that a binding has a SPAN ID, unbinds hardware with `prestera_hw_span_unbind()`, releases the SPAN ID through `prestera_span_put()`, and marks the binding invalid.

## State and persistence behavior
SPAN state is runtime-only and anchored at `sw->span`. A hardware SPAN ID persists until the last rule referencing its destination port is deleted and `prestera_hw_span_release()` succeeds. `binding->span_id` is the cross-module state used to prevent duplicate add and identify delete.

## Dependencies and integration points
The file depends on Prestera switch and port definitions, flow block binding state from `prestera_flow.h`, ACL-related includes, Linux list/refcount helpers, and hardware APIs `prestera_hw_span_get/release/bind/unbind()`. It is used by flower/ACL mirroring offload code.

## Risks and edge cases
If `prestera_hw_span_release()` fails in `prestera_span_put()`, the entry remains on the list with a refcount that has already reached zero, making future behavior risky. There is no explicit locking in this file; callers must serialize rule operations. `span_id` is `u8`, while the invalid ID macro is `-1`; the invalid value must live in the binding field with compatible signedness. Finalization only warns if entries remain.

## Test signals
Tests should cover two rules sharing one destination port, deletion order and reference counts, bind failure unwind, release failure behavior, duplicate add returning `-EEXIST`, delete without add returning `-ENOENT`, and `prestera_span_fini()` with no leaked entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_span.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_span.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_span.h

## Purpose
This header declares the Prestera SPAN interface used by flow/ACL offload code. It defines the invalid SPAN marker and exposes switch lifecycle and rule add/delete operations for mirroring.

## Important APIs, types, and functions
The main constant is `PRESTERA_SPAN_INVALID_ID`, used to mark a binding without a hardware mirror ID. The header forward-declares `struct prestera_port`, `struct prestera_switch`, and `struct prestera_flow_block_binding`, and exports `prestera_span_init()`, `prestera_span_fini()`, `prestera_span_rule_add()`, and `prestera_span_rule_del()`.

## Control flow
Switch setup calls init before any SPAN rule can be installed. Rule add takes a source binding, destination `to_port`, and ingress/egress direction flag. Rule delete takes the same binding and direction to unbind hardware.

## State and persistence behavior
No structs are exposed; SPAN state is private to `prestera_span.c` and referenced through `sw->span` and `binding->span_id`. No state persists beyond driver lifetime.

## Dependencies and integration points
The header includes `<net/pkt_cls.h>` because SPAN rules are tied to traffic-control classifier offload paths. It is included by Prestera flow and ACL code.

## Risks and edge cases
The invalid ID macro is negative while hardware IDs are unsigned in the implementation. Callers must initialize `binding->span_id` to the invalid value and avoid concurrent add/delete races.

## Test signals
Compile tests should catch signature drift with flow-block code. Runtime tests should assert that binding initialization uses `PRESTERA_SPAN_INVALID_ID` and that ingress and egress deletions match the direction used on add.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_span.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_switchdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_switchdev.c

## Purpose
This file implements Prestera switchdev offload for Linux bridges. It maintains software bridge, bridge-port, VLAN, FDB, and MDB state, handles switchdev notifier events, programs Prestera hardware for bridge membership, VLAN membership, STP state, flooding, learning, locked ports, multicast database behavior, and forwards hardware FDB learn/age events back to the bridge.

## Important APIs, types, and functions
Public functions are `prestera_switchdev_init()`, `prestera_switchdev_fini()`, `prestera_bridge_port_join()`, and `prestera_bridge_port_leave()`. Internal state includes `struct prestera_switchdev`, `struct prestera_bridge`, `struct prestera_bridge_port`, `struct prestera_bridge_vlan`, `struct prestera_port_vlan`, `struct prestera_br_mdb_entry`, `struct prestera_br_mdb_port`, and `struct prestera_fdb_event_work`.

Important flows are bridge create/destroy, bridge-port add/ref/put, 802.1D and 802.1Q join/leave, VLAN add/delete, FDB add/delete and flush, MDB create/sync/delete, switchdev object/attribute notifier handling, asynchronous FDB workqueue processing, and Prestera FDB event reporting.

## Control flow
Initialization allocates `sw->swdev`, initializes the bridge list, creates an ordered workqueue, registers atomic and blocking switchdev notifiers, registers Prestera FDB hardware event handling, and sets default ageing time. Finalization unregisters FDB and switchdev handlers, destroys the workqueue, and frees state.

Bridge port join finds or creates a bridge object. VLAN-aware bridges are limited to one per switch; VLAN-unaware bridges allocate a hardware bridge ID. The port is refcounted as a `prestera_bridge_port`, marked offloaded through `switchdev_bridge_port_offload()`, and for VLAN-unaware bridges is added to the hardware bridge and configured with flood/learning/locked flags. Leave flushes FDB entries, resets PVID or deletes hardware bridge membership, unoffloads the port, flushes MDB state, resets bridge flags and STP, and drops references.

Attribute handling maps STP states to Prestera hardware states, applies bridge-port flags, validates ageing time range, rejects VLAN filtering changes on an existing bridge, toggles multicast-disabled state, and updates mrouter state. Object handling adds or deletes VLANs and MDB entries. VLAN add creates hardware VLAN membership, adjusts PVID, joins the software bridge VLAN, applies STP, and links `prestera_port_vlan` to `prestera_bridge_vlan`.

FDB notifier work is queued on `swdev_wq` to run under RTNL. User-added nonlocal FDB entries are programmed into hardware and reported as offloaded; deletes remove the hardware FDB entry. Hardware FDB learn/age events are converted to `SWITCHDEV_FDB_ADD_TO_BRIDGE` or `SWITCHDEV_FDB_DEL_TO_BRIDGE`.

MDB handling keeps a software MDB list per bridge, creates hardware MDB entries, tracks member bridge ports, and synchronizes flood-domain ports based on multicast enablement, mrouter presence, VLAN membership, and explicit MDB membership.

## State and persistence behavior
All bridge state is runtime-only. Hardware state persists in ASIC tables until explicit delete/flush calls or switch reset. Refcounts keep bridge ports alive while VLAN objects reference them. The global ordered workqueue serializes deferred FDB operations. Bridge objects are destroyed when their port list becomes empty. MDB state is enabled only when multicast is enabled and an mrouter exists; otherwise multicast falls back to flooding behavior.

## Dependencies and integration points
The file integrates Linux switchdev notifiers, bridge helpers, RTNL, netdev upper/lower traversal, LAG helpers, Prestera hardware APIs for bridges/VLAN/STP/FDB/MDB, flood-domain helpers, and Prestera FDB event handling. It also relies on `prestera_netdev_check()` and `prestera_port_dev_lower_find()` to map Linux devices to Prestera ports.

## Risks and edge cases
Only one VLAN-aware bridge is supported. VLAN filtering cannot change after bridge creation. Error unwind for VLAN joins must restore PVID and hardware VLAN state. MDB sync assumes `prestera_port_dev_lower_find()` returns a port before VLAN checks; missing lower ports can be risky. `prestera_switchdev_handler_init()` destroys `swdev_wq` on notifier registration failure, and the outer init error path also destroys it, creating possible double destroy on that path. FDB work allocates and copies MAC addresses in atomic context; allocation failure returns `NOTIFY_BAD`. LAG handling depends on valid `port->lag` for all member ports.

## Test signals
Test signals include bridge join/leave for VLAN-aware and VLAN-unaware bridges, rejection of a second VLAN-aware bridge, STP transitions and rollback, bridge flag programming and reset, ageing time limits, VLAN add/delete PVID transitions, user FDB add/delete offload notifications, hardware FDB learned/aged notifications, LAG FDB paths, MDB enable/disable with mrouter changes, multicast flood sync, notifier unregister/order teardown, and failure injection for workqueue/notifier/hardware calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_switchdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_switchdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_switchdev.h

## Purpose
This header declares the Prestera switchdev bridge-offload interface. It is the small public API used by Prestera core/netdev code to initialize switchdev support and react when a Prestera port joins or leaves a Linux bridge.

## Important APIs, types, and functions
The exports are `prestera_switchdev_init()`, `prestera_switchdev_fini()`, `prestera_bridge_port_join()`, and `prestera_bridge_port_leave()`. The join API receives the bridge netdev, Prestera port, and extack for user-visible error reporting. The leave API receives the bridge netdev and Prestera port.

## Control flow
Switch setup calls init after core switch data structures are ready and before bridge events are expected. Port upper-device handling calls bridge-port join/leave as bridge relationships change. Switch teardown calls fini after ports are removed from bridge contexts.

## State and persistence behavior
The header exposes no state; implementation-private state is held in `sw->swdev`. Hardware bridge state is created and removed by the implementation.

## Dependencies and integration points
The declarations rely on `struct prestera_switch`, `struct prestera_port`, `struct net_device`, and `struct netlink_ext_ack` being visible to users. It integrates Prestera port lifecycle code with Linux switchdev bridge offload.

## Risks and edge cases
Callers must not call join before `prestera_switchdev_init()`, and leave must match a previous join. The header does not express bridge mode limitations; callers learn those through runtime errors and extack/log messages.

## Test signals
Compile coverage should catch signature drift. Integration tests should exercise netdev upper join/leave sequences and verify init/fini lifecycle ordering around bridge events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_switchdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/pxa168_eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/pxa168_eth.c

## Purpose
This file is the platform Ethernet driver for Marvell PXA168-style 10/100 controllers. It manages MMIO registers, fixed RX/TX DMA descriptor rings, the controller's MAC hash filter table, MDIO/SMI PHY access, PHY link adjustment, NAPI receive processing, transmit completion reclaim, platform probe/remove, and netdev/ethtool operations.

## Important APIs, types, and functions
Important types are `struct rx_desc`, `struct tx_desc`, `struct pxa168_eth_private`, and `struct addr_table_entry`. The netdev operations are open, stop, start_xmit, set_rx_mode, set_mac_address, validate_addr, PHY ioctl, change_mtu, tx_timeout, and optional netpoll. The platform driver exports probe, remove, shutdown, and stub PM callbacks.

Key helpers include `abort_dma()`, `rxq_refill()`, `hash_function()`, `add_del_hash_entry()`, `init_hash_table()`, `eth_port_start/reset()`, `txq_reclaim()`, `rxq_process()`, `pxa168_eth_collect_events()`, `pxa168_eth_int_handler()`, `set_port_config_ext()`, `pxa168_eth_adjust_link()`, `pxa168_init_phy()`, `pxa168_init_hw()`, `rxq_init/deinit()`, `txq_init/deinit()`, `pxa168_rx_poll()`, `pxa168_eth_start_xmit()`, and SMI read/write helpers.

## Control flow
Probe enables the clock, allocates an Ethernet netdev, maps registers, obtains IRQ, configures netdev ops and MTU bounds, reads MAC address from device tree or hardware or generates one, loads platform-data or DT PHY settings, sets up NAPI and refill timer, allocates/registers an MDIO bus, initializes hardware, and registers the netdev.

Open initializes and connects the PHY if needed, requests IRQ, allocates RX/TX rings, refills RX descriptors with skbs, enables NAPI, and starts the port. `eth_port_start()` starts the PHY, programs current RX/TX descriptor pointers, clears/enables interrupts, enables the MAC, and starts RX DMA. Stop resets the port, disables NAPI and timer, frees IRQ, and deinitializes rings.

RX interrupt collection disables interrupts and schedules NAPI. NAPI reclaims TX completions, wakes the queue if space returned, processes RX descriptors until budget, refills RX buffers, completes NAPI, and reenables interrupts. RX packets are accepted only for single-descriptor, non-error frames; CRC length is removed before `netif_receive_skb()`. TX maps a single skb to one descriptor, sets DMA ownership and TX flags, starts high-priority TX DMA, updates stats, and stops the queue when the ring is nearly full.

## State and persistence behavior
Runtime state is stored in `pxa168_eth_private`: ring indexes, descriptor memory, skb arrays, MDIO bus, NAPI object, refill timer, work item, MAC hash-table DMA memory, PHY settings, and MMIO base. There is no disk persistence. Hardware state persists in registers and DMA tables until reset/remove/shutdown. The hash table is DMA coherent and rebuilt for MAC and multicast changes.

## Dependencies and integration points
The driver depends on platform devices, device tree, clocks, `of_get_ethdev_address()`, phylib, mdiobus C22 scanning, DMA mapping/coherent allocation, NAPI, netdev ops, ethtool PHY helpers, and Marvell PXA168 platform data.

## Risks and edge cases
Probe calls `platform_get_irq()` into `err` but checks `BUG_ON(dev->irq < 0)` before assigning `dev->irq = err`; this appears wrong and can miss negative IRQ errors other than defer. RX DMA mapping in `rxq_refill()` does not check `dma_mapping_error()`. TX mapping in `pxa168_eth_start_xmit()` also does not check DMA mapping failure. Several `BUG_ON()` calls can panic the kernel for runtime conditions such as ring wrap or invalid port number. Suspend/resume return `-ENOSYS` under `CONFIG_PM`. The hash table supports only the smaller 1/2KB mode and can return `-ENOSPC` for crowded multicast filters.

## Test signals
Useful tests include probe with DT and platform-data variants, missing PHY handle, IRQ error handling, MAC fallback paths, MDIO read/write timeouts, RX ring refill allocation failure and timer recovery, TX ring full/queue wake, MTU change while running, multicast/promiscuous hash programming, PHY link speed/duplex adjustment, tx timeout reopen, and DMA mapping failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/pxa168_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/skge.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/skge.c

## Purpose
This file is the PCI driver for SysKonnect/Marvell Yukon and Genesis Gigabit Ethernet adapters. It provides PCI probe/remove, board reset, one or two netdev ports per adapter, DMA descriptor rings, NAPI RX/TX completion, PHY/MAC initialization for Genesis and Yukon families, ethtool operations, Wake-on-LAN, multicast filtering, interrupt handling, suspend/resume, shutdown, and optional debugfs diagnostics.

## Important APIs, types, and functions
The file relies on hardware types from `skge.h`, especially `struct skge_hw`, `struct skge_port`, `struct skge_ring`, descriptor structs, and register macros. Netdev operations are `skge_up()`, `skge_down()`, `skge_xmit_frame()`, `skge_ioctl()`, `skge_get_stats()`, `skge_tx_timeout()`, `skge_change_mtu()`, `skge_set_multicast()`, and `skge_set_mac_address()`.

Major helper groups are ethtool/WOL/VPD access, ring allocation and RX buffer setup, Genesis XMAC/Broadcom PHY initialization and link handling, Yukon GMAC/Marvell PHY initialization and link handling, queue/RAM buffer setup, TX/RX data paths, interrupt and error handling, PCI reset/probe/remove, PM, and debugfs.

## Control flow
Module init optionally forces 32-bit DMA for DMI-listed boards, initializes debugfs, and registers the PCI driver. Probe enables the PCI device, requests BARs, sets bus mastering and DMA masks, allocates `skge_hw`, maps registers, resets and identifies the board, initializes one or two netdevs, registers them, and for dual-port boards requests the shared IRQ at probe time.

Opening a port validates its MAC, allocates a coherent descriptor block for RX and TX rings, allocates ring element arrays, fills RX buffers, requests IRQ for single-port boards, initializes the MAC/PHY family under `phy_lock`, configures RAM buffer partitions and BMU queues, starts RX, enables LEDs and port interrupts, enables NAPI, and programs multicast filters. Closing disables TX, stops timers/NAPI/interrupts, frees IRQ for single-port boards, stops family-specific MAC/PHY, resets TX/RX queues and FIFOs, cleans TX/RX buffers, frees rings and coherent memory, and clears `skge->mem`.

Transmit pads short skbs, verifies descriptor availability, maps the linear head and fragments, programs checksum offload fields, marks descriptors owned by hardware with memory barriers, starts the TX queue, updates BQL, and stops the netdev queue when low on descriptors. TX completion in NAPI unmaps descriptors no longer owned by hardware, frees the skb on EOF, completes BQL, and wakes the queue when enough descriptors are available.

RX NAPI first handles TX completion, then walks RX descriptors until budget or hardware ownership, validates frame status and hardware length, copies small frames or swaps in a new skb for larger frames, applies RX checksum metadata, passes packets through GRO, reuses descriptors on error or allocation failure, restarts the receiver, and reenables interrupts after NAPI completion.

The top-level ISR masks by `hw->intr_mask`, schedules PHY tasklet work for external PHY interrupts, schedules per-port NAPI for RX/TX queue interrupts, clears packet arbiter timeouts, dispatches MAC interrupts, and handles hardware error interrupts. The PHY tasklet reads slow PHY registers under `phy_lock`, updates link state, then unmasks external interrupts.

## State and persistence behavior
Runtime board state lives in `struct skge_hw`; per-port state lives in `struct skge_port`. Descriptor memory is coherent DMA allocated on port open and freed on close. Hardware register state persists while the PCI device is powered and is rebuilt by `skge_reset()` and `skge_up()`. WOL settings are stored in `skge->wol` and programmed during suspend/shutdown; they are not persisted to disk. Optional debugfs entries exist only while enabled and devices are up.

## Dependencies and integration points
The driver integrates with PCI, DMA mapping, netdev, NAPI/GRO, ethtool, MII ioctls, DMI quirks, debugfs, tasklets, PM, and architecture IRQ headers. It depends heavily on register and descriptor definitions in `skge.h`. It supports multiple vendors through the PCI ID table and separates Genesis and Yukon behavior through `is_genesis()` and hardware ID checks.

## Risks and edge cases
The driver contains many hardware errata workarounds and chip-specific branches; regressions can be family-specific. RX/TX ring manipulation depends on memory barriers and ownership bits. `skge_set_coalesce()` uses `min(delay, ecmd->rx_coalesce_usecs)` in the TX branch, which looks suspicious when only TX coalescing is configured. Debugfs notifier behavior depends on netdev ops pointer matching. PCI error handling may mask hardware error interrupts if bits cannot be cleared. Probe has distinct IRQ ownership rules for single-port and dual-port boards. WOL programming changes PHY power behavior during suspend/shutdown. Several paths use `BUG_ON()` for DMA alignment/boundary assumptions.

## Test signals
Test with supported PCI IDs for one-port and two-port cards, 32-bit and 64-bit DMA mask paths, Genesis and Yukon resets, copper and fiber PHYs, forced/autoneg link settings, pause negotiation, WOL magic/link wake, VPD read/write, ring resize while running, MTU changes with jumbo frames, checksum offload TX/RX, fragmented skb transmit unwind, RX allocation failure and small-packet copy path, interrupt masking/NAPI reenabling, PHY tasklet link changes, suspend/resume with running ports, shutdown WOL, and debugfs creation/removal when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/skge.c -->
