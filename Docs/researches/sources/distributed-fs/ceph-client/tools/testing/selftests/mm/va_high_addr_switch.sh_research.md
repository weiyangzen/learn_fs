<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/va_high_addr_switch.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/va_high_addr_switch.sh

## Purpose
Shell wrapper for `va_high_addr_switch` that verifies 5-level paging and hugepage prerequisites before running the C test's hugetlb path.

## Important APIs, Types, and Functions
- `skip()` exits with kselftest skip code 4.
- `check_supported_x86_64()` reads kernel config and CPU flags for `PGTABLE_LEVELS >= 5` and `la57`.
- `check_supported_ppc64()` checks `PGTABLE_LEVELS`, radix MMU, and existing hugepage support.
- `save_nr_hugepages()`, `restore_nr_hugepages()`, and `setup_nr_hugepages()` preserve and temporarily raise `/proc/sys/vm/nr_hugepages`.

## Control Flow
The script checks architecture-specific requirements, saves the hugepage count, ensures at least six free hugepages, runs `./va_high_addr_switch --run-hugetlb`, restores the original hugepage count, and exits with the C test's status.

## State and Persistence Behavior
It temporarily writes `/proc/sys/vm/nr_hugepages` and restores the original value. It reads `/proc/config.gz`, `/boot/config-$(uname -r)`, `/proc/cpuinfo`, and `/proc/meminfo`. No files in the repository are modified.

## Dependencies and Integration Points
Requires bash, gzip, grep, awk, `/proc` kernel config visibility, and permission to adjust hugepages. Integrated as the kselftest wrapper around the compiled `va_high_addr_switch` binary.

## Risks and Edge Cases
If kernel config is unavailable, page-table levels are too low, CPU support is missing, radix MMU is absent, or hugepages cannot be allocated, the script skips. If the child test is interrupted after hugepage modification, restoration depends on normal script flow.

## Test Signals
Skip messages exit 4. Otherwise the exit code is exactly the `va_high_addr_switch --run-hugetlb` return value after restoring hugepages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/va_high_addr_switch.sh -->
