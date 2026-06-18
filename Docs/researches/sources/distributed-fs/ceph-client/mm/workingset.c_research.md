# sources/distributed-fs/ceph-client/mm/workingset.c

## Purpose
`mm/workingset.c` implements refault-based workingset detection. It records eviction timestamps as xarray shadow entries, compares later refault distance against resident workingset size, and decides whether a faulted folio should be activated or restored as part of the active workingset. It also owns the LRU and shrinker for xarray nodes that contain only shadow entries.

## Important APIs, types, and functions
Public entry points include `workingset_age_nonresident()`, `workingset_eviction()`, `workingset_test_recent()`, `workingset_refault()`, `workingset_activation()`, and `workingset_update_node()`. `pack_shadow()` and `unpack_shadow()` encode/decode memcg id, NUMA node id, eviction timestamp, and workingset bit into xarray value entries. `shadow_nodes` is the global `list_lru` of shadow-only xarray nodes. `workingset_init()` calculates timestamp bucket orders and registers the `mm-shadow` shrinker.

## Control flow
On eviction, the caller supplies a locked, refcount-free folio. With multi-gen LRU enabled, `lru_gen_eviction()` records generation/tier data and returns a packed shadow. Otherwise `workingset_eviction()` samples `lruvec->nonresident_age`, shifts by the bucket order, ages nonresident pages by the folio size, and returns a shadow entry for the page cache or swap table. On refault, `workingset_refault()` records refault statistics, calls `workingset_test_recent()`, and activates/restores the folio when the computed refault distance fits within active/inactive competing pages. `workingset_activation()` ages nonresident counters on ordinary activation.

Shadow node maintenance is synchronous with xarray updates: `workingset_update_node()` adds nodes with only shadow values to `shadow_nodes` and removes nodes once pages reappear or the node is freeing. The shrinker estimates an allowed shadow-node budget and reclaims excess nodes by inverting from the LRU lock into the mapping `i_pages` lock, validating that the node still contains only values, and deleting it.

## State and persistence
All state is volatile: lruvec `nonresident_age`, packed shadow values stored in xarrays, per-lruvec workingset statistics, optional multi-gen LRU histograms, and the `shadow_nodes` list_lru. Memcg ids in shadows may become stale or be recycled; the code handles that as a speculative activation risk rather than persistent identity.

## Dependencies and integration points
The implementation sits between reclaim, page cache xarrays, swap shadow tables, memcg, lruvec accounting, multi-gen LRU, inode shrink/lru behavior, and vmstat counters such as `WORKINGSET_REFAULT_*`, `WORKINGSET_ACTIVATE_*`, `WORKINGSET_RESTORE_*`, `WORKINGSET_NODES`, and `WORKINGSET_NODERECLAIM`.

## Risks and invariants
Shadow packing is bit constrained; changes to `NODES_SHIFT`, memcg id bits, swap count bits, or LRU generation widths can break timestamp range or encoding. Refault decisions are intentionally approximate and can be wrong after counter wrap, memcg deletion, or id reuse. The shrinker relies on xarray node/value invariants under `i_pages` and inode locks; lock ordering and retry paths are critical.

## Test signals
Look for `/proc/vmstat` workingset counters increasing under page-cache and anonymous thrashing workloads, no lockdep reports from shadow-node reclaim, stable behavior with memcg deletion/recreation, multi-gen LRU enabled/disabled coverage, and shrinker activity that reduces `workingset_nodes` without corrupting page cache mappings.
