# sources/distributed-fs/ceph-client/tools/perf/tests/mem2node.c

## Purpose
Tests address-to-NUMA-node lookup built from perf environment memory-node metadata.

## Important APIs, Types, and Functions
- `test_nodes[]` describes node ids and CPU bitmap strings.
- `get_bitmap()` converts a CPU map string into a Linux bitmap via `perf_cpu_map__new()` and `__set_bit()`.
- `test__mem2node()` builds a `perf_env` with three `memory_node` entries and memory block size `0x100`, initializes `mem2node`, queries selected addresses, and tears down.

## Control Flow
For each synthetic node, the test sets node id, size `10`, and CPU bitmap. It initializes `mem2node__init(&map, &env)`, then checks addresses in block 0 map to node 0, blocks 1 and 2 to node 1, blocks 5 and 6 to node 3, and holes/out-of-range addresses return `-1`. It frees each bitmap and exits the map.

## State and Persistence
State is stack-local environment and `mem2node` map plus heap-allocated bitmaps. No files or global state are modified.

## Dependencies and Integration Points
Uses perf CPU maps, Linux bitmaps, `perf_env`, `memory_node`, and `mem2node` APIs. Registered as `DEFINE_SUITE("mem2node", mem2node)`.

## Risks and Edge Cases
- Node `size` is fixed to 10 for all entries, and the CPU bitmap positions are used as memory block indexes for the test.
- The test covers holes and one out-of-range high address but not overlapping node bitmaps.
- Allocation failure in `get_bitmap()` fails via test assertions before map initialization.

## Test Signals
Passing confirms `mem2node__node()` maps block-aligned addresses to expected node ids and returns `-1` for unmapped blocks.
