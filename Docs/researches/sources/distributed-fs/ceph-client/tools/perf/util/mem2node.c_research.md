# sources/distributed-fs/ceph-client/tools/perf/util/mem2node.c

## Purpose

`mem2node.c` builds a physical-address-to-NUMA-node lookup table from `perf_env` memory node bitmaps. It lets memory analysis map sampled physical addresses to NUMA nodes.

## Important APIs, Types, and Functions

The private `struct phys_entry` stores rb-node linkage, start, end, and node id. `mem2node__init()` builds and inserts merged physical ranges. `mem2node__exit()` frees the entries array. `mem2node__node()` searches the rb-tree and returns the node or `-1`.

## Control Flow

Initialization clears the map, counts all set memory-block bits across environment nodes, allocates that many entries, walks node bitmaps in order, converts each set bit to `start = bit * memory_bsize`, merges adjacent blocks from the same node, shrinks the array with `realloc()`, logs ranges, inserts each range into an rb-tree ordered by start, and stores the entry array. Lookup descends the rb-tree by comparing the address with entry start/end.

## State and Persistence Behavior

The map owns one contiguous `entries` allocation and rb-tree nodes embedded in that allocation. It persists until `mem2node__exit()`. The `cnt` field in the header is not populated by this implementation.

## Dependencies and Integration Points

The file depends on `perf_env` memory node data, Linux bitmaps, rbtrees, kernel macros, zalloc, debug output, and warnings. It integrates with perf mem/c2c NUMA locality reporting where physical addresses are available.

## Risks and Edge Cases

If no memory nodes are present, a warning mentions `CONFIG_MEMORY_HOTPLUG`; the `realloc(entries, 0)` path can set `entries` to NULL and still continue safely only because insertion count is zero. Ranges are sorted by iteration order within each node, but nodes themselves may produce interleaved ranges; the rb-tree handles lookup but merge only occurs for adjacent blocks encountered consecutively. The unused `cnt` field may mislead callers if they expect a count.

## Test Signals

Tests should build maps from empty, single-node, multi-node, adjacent, and interleaved bitmaps; verify merged ranges and lookup boundaries; query holes and end addresses; and check cleanup under allocation and zero-node cases.
