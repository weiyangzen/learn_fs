<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/vm_util.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/vm_util.h

## Purpose
Public header for memory-management selftest utilities. It defines pagemap bit constants, inline page-size helpers, procmap state, small kselftest logging helpers, and prototypes for VM, UFFD, THP, hugetlb, KSM, sysfs, procmap, and poison helper functions.

## Important APIs, Types, and Functions
- Defines pagemap bits such as `PM_SOFT_DIRTY`, `PM_UFFD_WP`, `PM_SWAP`, and `PM_PRESENT`, plus kpageflags bits.
- `struct procmap_fd` bundles a `/proc/$pid/maps` fd with `struct procmap_query`.
- Inline helpers `psize()`, `pshift()`, `force_read_pages()`, `open_self_procmap()`, `log_test_start()`, `log_test_result()`, and `sz2ord()`.
- Declares all `vm_util.c` helpers and constants `HPAGE_SHIFT`, `HPAGE_SIZE`, `PAGEMAP_PRESENT()`, and `PAGEMAP_PFN()`.

## Control Flow
The header supplies inline helper logic only. Callers use `psize()`/`pshift()` lazily, which populate extern globals on first use. `log_test_start()` stores the current test name in a static buffer and `log_test_result()` reports against it.

## State and Persistence Behavior
Declares extern cached page-size state and defines a header-local static `test_name` buffer for inline logging. It has no durable persistence but exposes functions that can mutate sysfs, KSM, and memory mappings.

## Dependencies and Integration Points
Includes `kselftest.h`, Linux fs/procmap definitions, mmap/unistd/err headers, and standard integer/boolean headers. It is included by UFFD, high-address, THP, soft-dirty, KSM, and related mm tests.

## Risks and Edge Cases
Header-local `static char test_name[1024]` creates one buffer per translation unit, which is intentional for inline logging but not shared. Some macros and constants mirror kernel ABI bits; stale definitions could diverge from newer kernels. Inline `FORCE_READ` relies on volatile access to prevent compiler optimization.

## Test Signals
No standalone signal. It shapes caller output through kselftest logging helpers and fatal declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/vm_util.h -->
