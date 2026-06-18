# sources/distributed-fs/ceph-client/drivers/md/dm-ps-io-affinity.c

## Purpose
Implements the `io-affinity` multipath path selector. It maps CPUs to paths using user-supplied cpumasks so I/O issued on a CPU prefers the path associated with that CPU, falling back to NUMA-local and then any available mapped path when necessary.

## Important APIs, Types, And Functions
`struct selector` contains a per-CPU `path_map`, a `path_mask` of CPUs with mappings, and a `map_misses` counter. `struct path_info` contains the `dm_path`, parsed cpumask, refcount, and failed flag. The selector callbacks are `ioa_create()`, `ioa_destroy()`, `ioa_add_path()`, `ioa_fail_path()`, `ioa_reinstate_path()`, `ioa_select_path()`, and `ioa_status()`.

## Control Flow
Creation allocates the selector, an array sized to `nr_cpu_ids`, and a mask of mapped CPUs. Each path must provide one cpumask argument; for each CPU in the mask, the selector installs the path if no mapping already exists and increments the path context refcount. Selection pins the current CPU with `get_cpu()`, checks the direct CPU mapping, then scans CPUs on the same NUMA node, then all mapped CPUs. Failed paths are skipped. Missing direct mappings increment `map_misses`.

Destroy iterates mapped CPUs and drops path references through `ioa_free_path()`, freeing a path context only when the last CPU mapping for it is removed.

## State And Persistence
State is entirely volatile: CPU-to-path mappings, path masks, per-path failed flags, and the map-miss counter. There is no service-time or queue-depth history and no persistent metadata.

## Dependencies And Integration Points
The selector integrates with DM multipath through `dm-path-selector.h` and with kernel CPU topology through cpumasks, `cpu_to_node()`, and `cpumask_of_node()`. Userspace must supply cpumask strings in the table path arguments, and status emits the table cpumask via `%*pb`.

## Risks
There is no explicit lock around `path_map` lookup or `failed` flag updates, relying on multipath path-selector call context and simple boolean updates. CPU hotplug/topology changes after table load can make mappings suboptimal. Duplicate CPU mappings are ignored with a warning, so table order silently decides ownership. A path with an empty or out-of-range mask fails to add.

## Test Signals
Test cpumask parsing, duplicate mappings, missing CPU mappings, failed-path fallback, reinstate behavior, and NUMA-local fallback. `map_misses` should increase only when the current CPU has no direct mapping. Table status should reproduce the cpumask for each path.
