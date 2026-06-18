# sources/distributed-fs/ceph-client/mm/mmzone.c

Purpose: provides small but central memory-zone helpers: online node iteration, zone iteration, zonelist filtering by highest zone and optional NUMA nodemask, LRU vector initialization, and optional NUMA balancing cpupid exchange stored in folio flags.

Important APIs/types/functions: `first_online_pgdat`, `next_online_pgdat`, `next_zone`, `__next_zones_zonelist`, `lruvec_init`, and conditional `folio_xchg_last_cpupid`. Key types are `pglist_data`/`pg_data_t`, `zone`, `zoneref`, `nodemask_t`, `lruvec`, `lru_list`, and `folio`.

Control flow: node iteration returns `NODE_DATA(first_online_node)` or advances via `next_online_node`. `next_zone` increments within the current node's `node_zones` array, then moves to the first zone of the next online node. `__next_zones_zonelist` advances through zonerefs until the zone index is at or below the requested highest zone and, when supplied, the zone's node is in the nodemask. `lruvec_init` zeroes the structure, initializes the LRU lock, zswap state, LRU list heads, poisons the unevictable list head by deleting it, and initializes multi-gen LRU state. `folio_xchg_last_cpupid` atomically replaces the cpupid bitfield in folio flags with a cmpxchg loop.

State and persistence: initializes and mutates in-memory memory-management state only. `lruvec_init` prepares locks/list heads and LRU generation state for later reclaim operations. `folio_xchg_last_cpupid` persists a NUMA-balancing hint in folio flags until the next update.

Dependencies and integration points: depends on NUMA node masks and node data macros, zonelist encoding helpers, zswap LRU-vector state, multi-gen LRU initialization, folio flag layout, and optional NUMA balancing configuration. Allocation paths and reclaim code consume these helpers when scanning zonelists or managing per-node/memcg LRUs.

Risks: incorrect zonelist advancement can select zones above the caller's allowed class or outside a NUMA policy. The unevictable LRU list is intentionally poisoned, so callers must honor its special handling. Cpupid bit manipulation must preserve unrelated folio flags and be atomic under concurrent NUMA hinting.

Test signals: NUMA allocation policy tests, memory hotplug/node onlining tests, reclaim/LRU initialization tests, zswap and multi-gen LRU boot coverage, and NUMA balancing workloads that verify cpupid exchange does not corrupt folio flags.
