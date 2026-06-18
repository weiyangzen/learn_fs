# sources/distributed-fs/lustre-release/lnet/lnet/lib-cpt.c

## Purpose

`lib-cpt.c` implements libcfs CPU partition tables for Lustre/LNet. A CPT is a software partition of CPUs and NUMA nodes used for lock sharding, per-partition allocation, NI affinity, message counters, and locality-aware network selection. The file builds the global `cfs_cpt_tab`, exposes query and mutation helpers, parses module parameters, supports per-CPT variable allocation, and registers CPU hotplug warnings.

## Important APIs, Types, and Functions

- `struct cfs_cpu_partition` stores a partition cpumask, nodemask, inter-CPT NUMA distances, spread rotor, and fallback node.
- `struct cfs_cpt_table` stores all partitions, CPU-to-CPT and node-to-CPT maps, global masks, partition count, global distance, and spread rotor.
- Module parameters `cpu_npartitions` and `cpu_pattern` control automatic or user-defined partitioning.
- Exported table lifecycle: `cfs_cpt_table_alloc()`, `cfs_cpt_table_free()`, `cfs_cpu_init()`, `cfs_cpu_fini()`.
- Exported queries: `cfs_cpt_table_print()`, `cfs_cpt_distance_print()`, `cfs_cpt_number()`, `cfs_cpt_weight()`, `cfs_cpt_online()`, `cfs_cpt_cpumask()`, `cfs_cpt_nodemask()`, `cfs_cpt_distance()`, `cfs_cpt_current()`, `cfs_cpt_of_cpu()`, `cfs_cpt_of_node()`, `cfs_cpt_spread_node()`.
- Exported mutation/helpers: `cfs_cpt_set_cpu()`, `cfs_cpt_unset_cpu()`, `cfs_cpt_set_cpumask()`, `cfs_cpt_unset_cpumask()`, `cfs_cpt_set_node()`, `cfs_cpt_unset_node()`, nodemask variants, and core include/exclude helpers.
- `cfs_cpt_bind()` changes current task CPU/memory affinity to a partition.
- `cfs_percpt_alloc()`, `cfs_percpt_free()`, and `cfs_percpt_number()` implement cacheline-aligned arrays indexed by CPT.

## Control Flow

`cfs_cpu_init()` registers CPU hotplug callbacks when enabled, takes `cpus_read_lock()`, then creates `cfs_cpt_tab` either from `cpu_pattern` or automatic partitioning. It logs the resulting NUMA node, CPU core, and partition counts. On failure it unwinds hotplug state and frees any partial table.

Automatic partitioning uses `cfs_cpt_num_estimate()` to choose a default based on online CPUs and hyperthread sibling width, capped more conservatively on 32-bit builds. `cfs_cpt_table_create()` validates requested partitions, allocates the table, then walks online NUMA nodes and calls `cfs_cpt_choose_ncpus()` to distribute CPUs across partitions. `cfs_cpt_choose_ncpus()` prefers CPUs in the same socket/core grouping and updates maps through `cfs_cpt_set_cpu()`.

Pattern creation in `cfs_cpt_table_create_pattern()` supports explicit partition ranges (`0[0-3]`), NUMA ranges (`N 0[0]`), default NUMA layout (`N`), CPU/NUMA relative core exclusion (`C[...]`, `N C[...]`), and processor exclusion (`X[...]`, `N X[...]`). It builds a default layout for exclusion modes, parses bracket ranges with `cfs_expr_list_parse()`, applies set/unset functions, and validates that every partition remains online.

Whenever CPUs or nodes are added/removed, `cfs_cpt_add_node()` and `cfs_cpt_del_node()` maintain node masks, `ctb_node2cpt`, per-partition distance arrays, and the global maximum distance using kernel `node_distance()`.

## State and Persistence Behavior

The global `cfs_cpt_tab` is exported and read-mostly after initialization. It is in-memory kernel state, not persisted externally. Each table owns dynamically allocated cpumasks, nodemasks, per-partition distance arrays, mapping arrays sized by `nr_cpu_ids` and `nr_node_ids`, and partition descriptors.

The per-CPT allocation API hides a `struct cfs_var_array` header immediately before the returned pointer array. Callers receive `void *` pointing at `va_ptrs[0]`; freeing relies on `container_of()`. Each partition buffer is `L1_CACHE_ALIGN(size)` and allocated with CPT-local allocation macros.

CPU hotplug support is intentionally limited. The callbacks do not rebalance the partition table; offline events only warn that performance/stability may be impacted, especially if all siblings in a core go offline.

## Dependencies and Integration Points

This file depends on Linux CPU, cpumask, nodemask, NUMA topology, hotplug, scheduler affinity, and memory policy APIs. It also depends on libcfs allocation wrappers, expression-list parsing, `LASSERT`, and exported symbols consumed by LNet and broader Lustre code.

Integration is broad: `lnet_cpt_table()` users map messages, MD pages, NIDs, counters, resource containers, NI TX queues, monitor queues, and allocations to CPTs. `config.c` uses `cfs_percpt_alloc()` for NI refs/TX queues. `lib-md.c` maps the first MD page to a CPT through `cfs_cpt_of_node()`. `lib-move.c` uses CPT distance to prefer local NIs and per-CPT locks/queues for message processing.

## Risks and Edge Cases

- Several setters, especially `cfs_cpt_set_cpumask()` and node helpers, call low-level add functions directly and can overwrite CPU-to-CPT mappings if given overlapping masks. Pattern validation avoids some cases but generic callers need discipline.
- `cfs_cpt_of_node()` checks `node > nr_node_ids` instead of `node >= nr_node_ids`, so `node == nr_node_ids` indexes past the allocated map.
- `cfs_cpt_bind()` returns after the first online CPU iteration, even if the current affinity is already compatible; this behavior should be tested against expected scheduler semantics.
- Pattern parsing is complex and mixes `node`, `exclude`, and `relative` modes. Invalid partition counts, empty partitions after exclusion, missing brackets, and offline CPUs all need coverage.
- CPU hotplug does not rebuild mappings. After CPU removal, `cfs_cpt_online()` and affinity binding may behave differently than initial partition design.
- `cfs_percpt_free()` assumes the pointer came from `cfs_percpt_alloc()` and cannot validate corrupted or offset pointers.

## Test Signals

Tests should validate table allocation/free under injected allocation failures; automatic partition counts for different CPU/HT topologies; pattern parsing for explicit, NUMA, include, exclude, relative-core, and malformed patterns; CPU/node add/remove distance recalculation; per-CPT allocation alignment/count/free behavior; `cfs_cpt_current()` remapping of unknown CPUs; `cfs_cpt_bind()` success and `-ENODEV`; print helpers returning `-E2BIG`; and hotplug callbacks preserving module stability while warning.
