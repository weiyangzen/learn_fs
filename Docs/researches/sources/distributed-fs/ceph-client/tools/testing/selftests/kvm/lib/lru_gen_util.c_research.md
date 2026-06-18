# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/lru_gen_util.c

## Purpose
This helper parses and drives Linux multi-generational LRU debugfs state for KVM selftests that need page-aging behavior tied to a memory cgroup.

## Important APIs, Types, and Functions
`lru_gen_read_memcg_stats()` parses `LRU_GEN_DEBUGFS` into `struct memcg_stats`. `lru_gen_sum_memcg_stats_for_gen()` and `lru_gen_sum_memcg_stats()` aggregate pages. `lru_gen_do_aging()` issues aging commands. `lru_gen_find_generation()` finds a generation containing enough pages. `lru_gen_usable()` validates kernel feature and debugfs availability.

## Control Flow
Parsing is state-machine based through `memcg_stats_handle_searching()`, `memcg_stats_handle_in_memcg()`, and `memcg_stats_handle_in_node()`. It scans for a named memcg, records node IDs, records generation age/anon/file counts, and stops at the next memcg. Aging rereads stats, computes each node's max generation, writes `+ memcg node max_gen 1 force_scan` commands, and rereads updated stats.

## State, Dependencies, and Integration
The file persists no global mutable state except static `force_scan`. It depends on debugfs files, cgroup naming, parser limits (`MAX_NR_NODES`, `MAX_NR_GENS`), and kselftest skip/assert behavior.

## Risks and Test Signals
Input format changes, removed memcgs, missing debugfs, or missing MGLRU features cause clear assertions or skips. The parser mutates line buffers with `strtok_r`, so it duplicates lines when it may need to hand them to another state.
