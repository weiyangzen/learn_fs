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
