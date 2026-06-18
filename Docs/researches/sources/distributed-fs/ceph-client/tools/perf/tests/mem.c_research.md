# sources/distributed-fs/ceph-client/tools/perf/tests/mem.c

## Purpose
Tests human-readable formatting of memory data source snoop and level fields.

## Important APIs, Types, and Functions
- `check(union perf_mem_data_src data_src, const char *string)` allocates `mem_info`, stores the data source, formats snoop and level strings using `perf_mem__snp_scnprintf()` and `perf_mem__lvl_scnprintf()`, and compares against expected output.
- `test__mem()` constructs several `union perf_mem_data_src` cases for L4 hit, remote L4 hit, PMEM miss, remote PMEM miss, and forwarded remote RAM miss.

## Control Flow
The suite zeroes a data source, mutates fields across scenarios, and ORs together `check()` return values. Each `check()` creates a new mem_info object, formats into a fixed 100-byte buffer, releases the object, and asserts exact string equality.

## State and Persistence
No persistent state. Each scenario uses stack-local data and a short-lived `mem_info`.

## Dependencies and Integration Points
Exercises `util/mem-events.h`, `util/mem-info.h`, `union perf_mem_data_src`, and formatting helpers used by perf mem reports. Registered as `DEFINE_SUITE("Test data source output", mem)`.

## Risks and Edge Cases
- Expected strings are exact, so small display wording changes will fail the test.
- The same `src` object is mutated across cases; fields not explicitly reset can carry forward intentionally, such as snoop-forward on the final RAM case.
- Buffer size is sufficient for these cases but not a general formatter stress test.

## Test Signals
Passing means selected local/remote, hit/miss, PMEM/RAM, and snoop-forward combinations render as expected.
