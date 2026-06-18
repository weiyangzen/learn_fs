<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-common.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-common.c

## Purpose
Shared implementation for the userfaultfd selftests. It abstracts the memory backends used by `uffd-stress` and `uffd-unit-tests`, initializes test mappings and accounting data, opens/configures userfaultfd handles, and provides the common page-fault handlers for missing, write-protect, minor, copy, move, fork, remove, and remap events.

## Important APIs, Types, and Functions
- Exports backend operation tables `anon_uffd_test_ops`, `shmem_uffd_test_ops`, and `hugetlb_uffd_test_ops`, consumed through the global `uffd_test_ops`.
- `area_mutex()` and `area_count()` define the per-page data layout used by stress and verification paths: a `pthread_mutex_t` at page offset zero and an aligned counter after it.
- `uffd_test_ctx_init()` allocates source/destination mappings, runs optional test-case hooks, opens userfaultfd, initializes per-page counters, drops destination pages, and creates per-worker pipes.
- `uffd_test_ctx_clear()` closes pipes and uffd fds, frees counters, and unmaps all primary/alias/remap areas.
- `userfaultfd_open()`, `uffd_open_sys()`, `uffd_open_dev()`, `uffd_open()`, and `uffd_get_features()` cover both syscall and `/dev/userfaultfd` open paths.
- `uffd_poll_thread()`, `uffd_read_msg()`, and `uffd_handle_page_fault()` implement the event loop and default page-fault resolution logic.
- `wp_range()`, `continue_range()`, `copy_page()`, `__copy_page()`, and `move_page()` wrap the key UFFD ioctls.

## Control Flow
Backend allocation is selected before initialization by assigning `uffd_test_ops`. Anonymous mappings use plain private anonymous `mmap`; hugetlb and shmem allocate a memfd-backed source/destination pair, optionally with shared aliases for minor-fault tests. `uffd_test_ctx_init()` populates `area_src`, makes `area_dst` empty, and prepares pipes that let poll threads terminate without cancellation. Fault-handling threads poll/read the uffd descriptor, dispatch page faults to the handler, update fork fds on `UFFD_EVENT_FORK`, unregister removed ranges on `UFFD_EVENT_REMOVE`, and update `area_dst` after `UFFD_EVENT_REMAP`.

## State and Persistence Behavior
State is process-local in `uffd_global_test_opts_t`: mapping pointers, aliases, `uffd`, pipes, counters, feature flags, and coordination flags. The file creates temporary memfds for shmem/hugetlb backing and closes them after mapping; no durable files are intentionally left behind. It mutates memory mappings through `mmap`, `madvise`, `munmap`, `mremap` event handling, and UFFD ioctls.

## Dependencies and Integration Points
Depends on Linux UFFD ABI headers, memfd/fallocate/madvise, `pthread`, `poll`, `fcntl`, and helpers from `vm_util.c` such as `read_pmd_pagesize()`, `check_huge_shmem()`, and UFFD register wrappers. It is compiled with the userfaultfd test programs rather than run standalone.

## Risks and Edge Cases
The code intentionally exercises racy `-EEXIST` paths for `UFFDIO_COPY` and `UFFDIO_CONTINUE`. Correct alias mapping is critical for shmem/hugetlb shared minor faults. Several checks rely on Linux/glibc details, such as a read fault during `pthread_mutex_lock()`. Privilege or kernel configuration gaps can make UFFD open/feature negotiation fail, and hugetlb paths depend on available huge pages.

## Test Signals
Pass/fail signals come from callers. This file emits hard failures through `err()` when memory corruption, unexpected UFFD events, incorrect ioctl results, short reads, failed wakeups, or cleanup failures occur. Fault counters reported by `uffd_stats_report()` are used by stress/unit tests to validate expected missing/wp/minor fault counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-common.c -->
