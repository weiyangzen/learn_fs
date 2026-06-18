# File Research: sources/block-storage/linux-dm/drivers/md/dm-ps-io-affinity.c

## Purpose

`dm-ps-io-affinity.c` implements the `io-affinity` multipath selector. It chooses paths according to the CPU currently issuing I/O, with NUMA-local and any-valid fallback.

## State And Path Mapping

The selector owns a `path_map` array indexed by CPU, a `path_mask` of CPUs with mappings, and a `map_misses` counter. Each path has a `dm_path`, cpumask, refcount, and failed flag.

Each path requires exactly one cpumask argument. `ioa_add_path()` parses it, assigns unmapped CPUs to the path, warns about duplicate CPU mappings, ignores CPU IDs beyond `nr_cpu_ids`, and uses a refcount to free a path only after all CPU mappings referencing it are released.

## Selection Algorithm

`ioa_select_path()` pins the current CPU with `get_cpu()`, tries that CPU’s mapped path if present and not failed, increments `map_misses` on absent direct mapping, then searches paths mapped to the local NUMA node, then any mapped path in `path_mask`. It returns `NULL` if all mapped paths are failed or absent.

## Failure And Status

Failure and reinstatement toggle the path’s `failed` flag. Per-path table status prints the path cpumask. Per-path info status reports the global `map_misses` counter. Selector-level status reports no selector arguments.

## Invariants And Risks

- CPU-to-path mappings are static after construction; duplicate mappings keep the first path.
- Failed paths remain in `path_map` but are skipped at selection time.
- `path_mask` and `path_map` are freed by walking mapped CPUs and refcounting shared path objects.
- The failed flag is a simple boolean and selection is lockless, so tests should consider concurrent fail/reinstate visibility.
- A path with a cpumask that adds no valid new CPU mappings is rejected.

## Test Focus

Test cpumask parsing, duplicate CPU mappings, out-of-range CPUs, no valid CPU mappings, selection on mapped CPU, local-node fallback, global fallback, all paths failed returning `NULL`, map miss accounting, and destroy refcount cleanup for multi-CPU paths.
