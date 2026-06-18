<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/va_high_addr_switch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/va_high_addr_switch.c

## Purpose
Tests virtual address selection around the high-address switch boundary used by architectures with large userspace virtual address spaces. It verifies how `mmap()` treats hints below, at, and above the boundary, both for normal pages and optional hugetlb mappings.

## Important APIs, Types, and Functions
- `struct testcase` describes an address hint, size, flags, message, whether the result must be below the switch hint, and whether to keep the mapping.
- `testcases_init()` computes architecture/page-size-specific boundaries and builds normal and hugetlb testcase arrays.
- `run_test()` executes each mapping, validates returned address placement, touches the mapping, and unmaps unless requested.
- `high_address_present()` probes arm64 high VA availability.
- `supported_arch()` restricts the test to powerpc64, x86_64, and arm64 with high addresses.

## Control Flow
`main()` skips unsupported architectures, initializes test arrays, runs normal mapping cases, and runs hugetlb cases only when invoked with `--run-hugetlb`. Normal cases include hints below the switch boundary, exactly at the boundary, high-address hints, `MAP_FIXED`, `NULL`, and `(void *)-1`. Hugetlb cases mirror important boundary behaviors using default huge page size.

## State and Persistence Behavior
The program allocates testcase arrays dynamically and creates anonymous mappings. Some mappings are intentionally kept across later cases to test repeated allocation behavior and collision handling. There is no file persistence.

## Dependencies and Integration Points
Depends on `vm_util.h` for default hugepage size and kselftest constants. Usually wrapped by `va_high_addr_switch.sh`, which validates platform requirements and provides hugetlb pages before invoking `--run-hugetlb`.

## Risks and Edge Cases
The expected switch hint differs on arm64 depending on page size/LPA2. Hugetlb cases require configured hugepages. Kept mappings can influence later address selection by design; this makes ordering significant. Unsupported architectures return skip rather than failure.

## Test Signals
Each case prints the attempted mapping and `OK` or `FAILED`. The process returns `KSFT_PASS`, `KSFT_FAIL`, or `KSFT_SKIP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/va_high_addr_switch.c -->
