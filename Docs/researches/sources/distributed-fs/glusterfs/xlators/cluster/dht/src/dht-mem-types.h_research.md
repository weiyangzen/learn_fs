# Research: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-mem-types.h

## Purpose

`dht-mem-types.h` declares DHT-specific memory accounting IDs. These IDs extend the common Gluster memory type range and let allocations in the DHT translator be tagged by structure family for diagnostics, leak reports, and memory pool/statistics tooling.

## Important APIs, Types, and Functions

The file contains one enum, `gf_dht_mem_types_`, starting at `gf_common_mt_end + 1` and ending with `gf_dht_mt_end`. Tags cover DHT layout and config objects (`gf_dht_mt_dht_conf_t`, `gf_dht_mt_dht_layout_t`), scalar allocations (`gf_dht_mt_char`, `gf_dht_mt_int32_t`, `gf_dht_mt_xlator_t`), rebalance and defrag structures (`gf_defrag_info_mt`, `gf_dht_mt_container_t`, `gf_dht_mt_miginfo_t`), inode/fd context objects, directory entries, locs, and auxiliary arrays such as node UUIDs and return caches.

## Control Flow and Integration

There is no runtime control flow in this header. It is consumed by C files that pass these enum values to `GF_CALLOC`, `GF_MALLOC`, mem-pool setup, or allocation wrappers. For example, the rebalance code uses tags such as `gf_dht_mt_container_t`, `gf_dht_mt_dirent_t`, `gf_dht_mt_loc_t`, and `gf_dht_mt_octx_t` when creating queue containers and directory crawl metadata.

## State and Persistence Behavior

The enum does not allocate or persist anything by itself. Its values become part of runtime memory accounting state in Gluster's allocator. Ordering is effectively persistent at the diagnostics ABI level: changing or reusing IDs can confuse memory reports and tooling that maps numeric IDs back to names.

## Dependencies and Constraints

The header includes `<glusterfs/mem-types.h>` and relies on `gf_common_mt_end` as the base for component-specific IDs. New DHT allocation categories should be appended before `gf_dht_mt_end`; existing values should not be reordered unless the wider project accepts the diagnostic compatibility impact.

## Risks and Test Signals

The main risk is tag drift: allocating a structure under the wrong tag makes leak reports misleading, while adding allocations without a suitable tag reduces observability. Test signals are mostly indirect: memory accounting output should classify DHT rebalance containers, locs, dirents, inode contexts, and fd contexts under the expected DHT tags during translator init, rebalance, and teardown.
