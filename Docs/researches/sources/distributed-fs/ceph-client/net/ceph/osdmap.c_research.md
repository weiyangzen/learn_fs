# sources/distributed-fs/ceph-client/net/ceph/osdmap.c

## Purpose
`osdmap.c` decodes and owns the in-kernel representation of Ceph OSD maps and CRUSH maps, then answers placement questions for libceph clients. It maps objects to raw PGs, raw PGs to actual PGs, PGs to up and acting OSD sets, and PGs to primaries or erasure-coded shards. It also manages pool metadata, OSD state arrays, primary affinity, temporary mappings, upmap overrides, CRUSH location parsing, and incremental map application.

## Important APIs, types, and functions
- Map lifecycle APIs are `ceph_osdmap_alloc()`, `ceph_osdmap_decode()`, `osdmap_apply_incremental()`, and `ceph_osdmap_destroy()`.
- Pool lookup helpers are `ceph_pg_pool_by_id()`, `ceph_pg_pool_name_by_id()`, `ceph_pg_poolid_by_name()`, and `ceph_pg_pool_flags()`.
- Object identity helpers include `ceph_oloc_copy()`, `ceph_oloc_destroy()`, `ceph_oid_copy()`, `ceph_oid_printf()`, `ceph_oid_aprintf()`, and `ceph_oid_destroy()`.
- Placement APIs include `ceph_object_locator_to_pg()`, `__ceph_object_locator_to_pg()`, `ceph_pg_to_up_acting_osds()`, `ceph_pg_to_primary_shard()`, and `ceph_pg_to_acting_primary()`.
- Interval-change helpers include `ceph_pg_compare()`, `ceph_spg_compare()`, `ceph_pg_is_split()`, `ceph_is_new_interval()`, `ceph_osds_changed()`, and `ceph_osds_copy()`.
- CRUSH locality APIs include `ceph_parse_crush_location()`, `ceph_compare_crush_locs()`, `ceph_clear_crush_locs()`, and `ceph_get_crush_locality()`.
- Core data structures are `struct ceph_osdmap`, `struct ceph_pg_pool_info`, `struct ceph_pg_mapping`, `struct ceph_osds`, `struct ceph_object_locator`, `struct ceph_object_id`, `struct workspace_manager`, and decoded CRUSH map/bucket/rule structures.

## Control flow
Full map decode starts with wrapper/client-data version parsing in `get_osdmap_client_data_v()`. `osdmap_decode()` then reads FSID, epoch, timestamps, pools, pool names, pool max, flags, max OSD, OSD state/weight/address arrays, `pg_temp`, `primary_temp`, primary affinity, CRUSH payload, and optional upmap structures. It allocates and resizes arrays through `osdmap_set_max_osd()` and installs a decoded CRUSH map through `osdmap_set_crush()`, which also seeds the CRUSH workspace manager.

Incremental decode in `osdmap_apply_incremental()` validates the next epoch, handles embedded full maps, optionally replaces CRUSH, updates flags/pool max/max OSD, applies new/removed pools and names, applies OSD up/state/weight changes in a deliberate order, and then updates temporary mappings, primary affinity, erasure-code profile skips, and upmap changes. `decode_new_up_state_weight()` first scans encoded sections, applies new weights, then state xors, then up-client addresses so cases that both mark an OSD up and remove existence land in the intended final state.

CRUSH decode in `crush_decode()` validates magic, allocates buckets/rules, decodes bucket algorithms, names, tunables, class metadata skips, and choose-arg maps. `crush_finalize()` calculates per-map workspace size. Placement later borrows workspaces from `workspace_manager`, allocating up to roughly one per online CPU and otherwise waiting for an idle workspace.

Object-to-PG mapping starts in `__ceph_object_locator_to_pg()`, which hashes either object name alone or namespace plus separator plus object name. `raw_pg_to_pg()` stable-mods the raw seed to the pool PG count. `raw_pg_to_pps()` derives the placement seed, either using `HASHPSPOOL` hashing or legacy pool-plus-seed arithmetic.

PG-to-OSD mapping starts with `pg_to_raw_osds()`: find a CRUSH rule for pool ruleset/type/size, run CRUSH with the placement seed and pool-specific choose args, and remove nonexistent OSDs. `apply_upmap()` applies exact `pg_upmap` and item replacement overrides while ignoring targets marked out. `raw_to_up_osds()` removes down OSDs or substitutes `CRUSH_ITEM_NONE` depending on replicated versus erasure-coded pool behavior. `apply_primary_affinity()` probabilistically chooses a different primary when configured. `get_temp_osds()` overlays `pg_temp` and `primary_temp` to produce the acting set. `ceph_pg_to_up_acting_osds()` composes those steps and validates the result.

CRUSH locality parsing stores user-specified type/name pairs in an rbtree. Locality lookup walks upward from an OSD through CRUSH bucket membership using a linear parent search and returns the closest matching bucket type id, or `-1` if no requested location matches.

## State and persistence behavior
All map state is in memory and replaced or mutated from monitor-provided binary maps. `struct ceph_osdmap` owns arrays for OSD state, weights, addresses, optional primary affinity, rbtrees for pools and PG mappings, the CRUSH map, and CRUSH workspaces. Pool names and object ids may allocate dynamic memory; object locators hold refcounted `ceph_string` namespaces. Destroy paths empty every rbtree, release CRUSH and workspace memory, and `kvfree()` array allocations.

## Dependencies and integration points
`osd_client.c` relies on this file for every target recalculation and resend decision. The file depends on Ceph decode helpers for wire-format bounds checking, CRUSH mapper/hash code for placement, rbtree helper macros for ordered maps, `string_table.c` for pool namespace references, messenger address decoders for OSD address vectors, and CephFS/RBD callers through exported object locator and placement APIs.

## Risks and edge cases
- Decode is compatibility-heavy; wrong version handling or skipped-field length handling can corrupt the cursor and poison the map.
- `osdmap_set_max_osd()` resizes several parallel arrays; partial allocation or primary-affinity resizing failures need careful cleanup expectations.
- Incremental map ordering is security and correctness sensitive because state, weight, and address sections can conflict.
- Placement behavior differs for replicated pools that can shift OSDs and erasure-coded pools that preserve shard positions with `CRUSH_ITEM_NONE`.
- Upmap item replacement explicitly does not support bidirectional swaps; tests should lock in that behavior.
- Primary affinity changes the order of replicated up sets and must stay consistent with interval-change detection in `osd_client.c`.
- CRUSH locality parent lookup is linear and ambiguous for items present in multiple buckets.
- `ceph_oid_printf()` BUGs when formatted names do not fit inline storage; callers with unbounded names must use `ceph_oid_aprintf()`.

## Test signals
High-value tests include decoding full maps and incremental maps across supported struct versions, resizing `max_osd`, adding/removing pools, pool name lookup, OSD up/down/exists/weight transitions, primary affinity decode and placement effects, `pg_temp` and `primary_temp`, `pg_upmap` and `pg_upmap_items`, replicated versus erasure-coded acting set behavior, PG split detection, object namespace hashing, CRUSH choose args, fallback choose args, address-vector decode under msgr2, malformed map bounds checks, and CRUSH location parse/compare/locality cases.
