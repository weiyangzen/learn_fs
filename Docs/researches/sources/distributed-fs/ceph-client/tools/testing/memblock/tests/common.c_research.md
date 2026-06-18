# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/common.c

## Purpose
`common.c` implements shared support for the memblock test binaries: resetting memblock state, allocating fake physical memory, setting up NUMA layouts, parsing command-line options, and emitting verbose kselftest-style pass/fail labels.

## Important APIs, Types, And Functions
Key exported helpers are `reset_memblock_regions()`, `reset_memblock_attributes()`, `setup_memblock()`, `setup_numa_memblock()`, `dummy_physical_memory_init()`, `dummy_physical_memory_cleanup()`, `dummy_physical_memory_base()`, `parse_args()`, `test_fail()`, `test_pass()`, `test_print()`, and the prefix stack operations. Global test state includes `static struct test_memory memory_block`, `static const char *prefixes[PREFIXES_MAX]`, `static int nr_prefixes`, `static int verbose`, and `bool movable_node_enabled`.

## Control Flow
`parse_args()` handles `--help`, `--movable-node`, and `--verbose`; help exits immediately. `setup_memblock()` resets region arrays, registers a `MEM_SIZE` range at the allocated dummy base, and fills dummy memory with byte value `1`. `setup_numa_memblock()` splits the dummy memory into eight node fractions expressed in basis points and sets hotplug flags unless `movable_node_enabled` simulates the `movable_node` kernel parameter. Prefix helpers build nested test names consumed by verbose pass/fail output.

## State And Persistence
All state is process-local. `dummy_physical_memory_init()` allocates `PHYS_MEM_SIZE` bytes with `malloc()` and `dummy_physical_memory_cleanup()` frees it. `reset_memblock_regions()` zeroes only the active portions of `memblock.memory.regions` and `memblock.reserved.regions`, then restores counts, max values, and totals. `reset_memblock_attributes()` restores names, allocation direction, and current limit.

## Dependencies And Integration Points
The file depends on Linux memblock and memory-hotplug headers, `getopt_long_only()`, `assert()`, `malloc/free`, kselftest output helpers, and the `movable_node_is_enabled()` stub behavior in the broader test harness. Tests in `basic_api.c` and allocation suites rely on this file to keep global memblock state deterministic.

## Risks
Because the helpers operate on the real global `memblock` object, missed cleanup can cascade into later tests. `reset_memblock_regions()` clears only `cnt` entries, so corruption outside the active count would persist. `setup_numa_memblock()` trusts the caller-provided fractions to add up sensibly; it asserts each fraction is at most 10000 but does not assert the sum equals 10000. Verbose output preserves `errno` around `vprintf()`, which avoids one class of test interference.

## Test Signals
Failures in shared setup usually surface as downstream assertion failures. Verbose mode adds kselftest pass/fail lines with nested prefixes, improving localization of a failed memblock API scenario.
