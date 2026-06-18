<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/vm_util.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/vm_util.c

## Purpose
Shared VM utility implementation for memory-management selftests. It provides pagemap/PAGEMAP_SCAN probes, smaps/status parsing, THP/hugetlb detection, UFFD registration wrappers, procmap query helpers, sysfs helpers, KSM controls, hardware poison helpers, and small filesystem write utilities.

## Important APIs, Types, and Functions
- Pagemap helpers: `pagemap_get_entry()`, `pagemap_is_softdirty()`, `pagemap_is_swapped()`, `pagemap_is_populated()`, and `pagemap_get_pfn()`.
- Hugepage helpers: `read_pmd_pagesize()`, `check_huge_anon()`, `check_huge_file()`, `check_huge_shmem()`, `allocate_transhuge()`, `default_huge_page_size()`, and `detect_hugetlb_page_sizes()`.
- UFFD wrappers: `uffd_register_with_ioctls()`, `uffd_register()`, and `uffd_unregister()`.
- VMA/procmap helpers: `check_vmflag_*()`, `softdirty_supported()`, `open_procmap()`, `query_procmap()`, `find_vma_procmap()`, and `close_procmap()`.
- Kernel control helpers: `write_sysfs()`, `read_sysfs()`, `detect_huge_zeropage()`, KSM getters/start/stop functions, `get_hardware_corrupted_size()`, `unpoison_memory()`, `sys_mremap()`, and `write_file()`.

## Control Flow
Most functions are leaf helpers. Pagemap flag tests first read `/proc/self/pagemap`, then cross-check with `PAGEMAP_SCAN` when supported. Smaps helpers search for the VMA start line and then a named field within that VMA block. UFFD registration builds the mode bitmask from missing/wp/minor booleans and returns negative errno on failure. KSM start waits for two full scans after enabling KSM.

## State and Persistence Behavior
Global cached page size/shift variables live in `vm_util.h`/this file. Helpers read and write `/proc` and `/sys` knobs; `ksm_start()`, `ksm_stop()`, `ksm_use_zero_pages()`, `write_sysfs()`, `unpoison_memory()`, and `write_file()` can change kernel state. Most parsing helpers are read-only.

## Dependencies and Integration Points
Depends on Linux procfs/sysfs/debugfs ABI, `PAGEMAP_SCAN`, `PROCMAP_QUERY`, UFFD ioctls, kselftest fatal reporting, and standard libc file APIs. It is a central integration library for many mm selftests, including the UFFD and high-address tests in this subset.

## Risks and Edge Cases
`PAGEMAP_SCAN` support is probed by intentionally using an invalid vector and checking for `EFAULT`. Several helpers fail the entire test via `ksft_exit_fail_msg()` on parse/read mismatches. Sysfs/debugfs permissions and kernel feature availability vary by environment. Some helpers assume current procfs field names and smaps formatting.

## Test Signals
This file does not produce standalone test results. Callers see hard kselftest failures on unexpected read/parse/ioctl errors, boolean feature results for availability checks, and negative errno returns for helpers designed to be optional.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/vm_util.c -->
