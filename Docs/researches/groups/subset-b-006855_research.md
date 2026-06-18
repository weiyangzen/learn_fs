# subset-b-006855 research

Grouped research for subset `subset-b-006855`. Each file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-common.h

## Purpose
Common interface and shared type definitions for userfaultfd selftests. It centralizes includes, error macros, feature flags, memory backend abstractions, global test state, worker argument state, and declarations implemented in `uffd-common.c`.

## Important APIs, Types, and Functions
- Defines `UFFD_FLAGS` as `O_CLOEXEC | O_NONBLOCK | UFFD_USER_MODE_ONLY`.
- `struct uffd_global_test_opts` carries test geometry, mapping pointers, uffd fd/flags, pipes, counters, backend type, shared/private mode, write-protect enablement, and fork readiness.
- `struct uffd_args` carries per-thread CPU id, fault counters, apply-WP flag, global options pointer, and optional custom fault handler.
- `struct uffd_test_ops` abstracts memory allocation, page release, alias address rewriting, and PMD mapping checks.
- `struct uffd_test_case_ops` allows per-test `pre_alloc` and `post_alloc` hooks.
- Declares UFFD helpers, page helpers, stats helpers, open paths, and constants `TEST_ANON`, `TEST_HUGETLB`, and `TEST_SHMEM`.

## Control Flow
This header does not execute logic itself. It defines the contract followed by memory backends and test drivers: callers choose an operation table, set `uffd_test_case_ops` when needed, call `uffd_test_ctx_init()`, register mappings, run worker threads, then call `uffd_test_ctx_clear()`.

## State and Persistence Behavior
The header declares global operation pointers and, as an extern, `uffd_gtest_opts`; actual storage and mutation live in C files. All state is in-process and tied to kernel fds/mappings rather than persistent disk data.

## Dependencies and Integration Points
Includes `kselftest.h` and `vm_util.h`, plus Linux UFFD, mmap, syscall, pthread, poll, signal, wait, atomic, and integer headers. It is an integration point for all userfaultfd tests in this mm selftest area.

## Risks and Edge Cases
Because it exposes global backend pointers, tests must set `uffd_test_ops` before initialization. The error macros always exit, so helper failures are terminal. Compatibility depends on kernel UFFD definitions and architecture support for the included ABI headers.

## Test Signals
Signals are indirect: functions declared here return standard kselftest pass/skip/fail outcomes through their callers. Fatal helper errors print source file and line via `_err()`/`err()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-stress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-stress.c

## Purpose
Stress test for userfaultfd that repeatedly transfers physical memory between source and destination mappings using UFFD fault resolution. It targets concurrency races among faulting mutator threads, UFFD handler threads, and background copy threads over anonymous, shmem, and hugetlb mappings.

## Important APIs, Types, and Functions
- `locking_thread()` randomly or sequentially locks per-page mutexes in `area_dst`, verifies counters, and increments them.
- `uffd_read_thread()` handles blocking-read UFFD mode; `uffd_poll_thread()` from `uffd-common.c` handles poll mode.
- `background_thread()` copies each CPU shard, optionally enabling write protection midway.
- `stress()` creates and joins locking, UFFD, and background workers for one bounce.
- `userfaultfd_stress()` registers ranges, runs bounces, unregisters, verifies counters, swaps source/destination pointers, and reports stats.
- `set_test_type()` and `parse_test_type_arg()` select anonymous, shmem, shmem-private, hugetlb, or hugetlb-private modes and negotiate UFFD features.

## Control Flow
`main()` parses `<test type> <MiB> <bounces>`, arms SIGALRM, computes CPU parallelism capped at 32, validates hugetlb availability, and calls `userfaultfd_stress()`. Each bounce toggles mode bits derived from the decreasing `bounces` counter, sets blocking or nonblocking fd flags, registers destination and alias ranges, drops destination pages, runs worker threads, clears WP if active, unregisters ranges, optionally verifies all counters, swaps mappings, and prints fault totals.

## State and Persistence Behavior
State is held in a heap-allocated global `gopts`, `features`, `bounces`, `zeropage`, and pthread attributes. SIGALRM periodically toggles `test_uffdio_copy_eexist` so copy retry paths are exercised. No durable files are created, but the test consumes hugepage reservations when hugetlb mode is used and heavily mutates VMAs with UFFD ioctls and `madvise`.

## Dependencies and Integration Points
Depends on `uffd-common.h`, `vm_util.c` helpers, UFFD kernel features, `getrandom()`, pthreads, signals, kselftest exit codes, and system hugepage availability. It is built as the `uffd-stress` selftest program and run with explicit test type/size/bounce arguments.

## Risks and Edge Cases
The test deliberately creates races and depends on faulting through `pthread_mutex_lock()`. Too-small memory sizes yield zero pages per CPU and abort. High CPU counts are capped to avoid zero shard size. Hugetlb tests skip when insufficient free hugepages exist. Kernel privilege restrictions on userfaultfd can skip or fail setup.

## Test Signals
Success is process exit 0 after all bounces. Failures are hard exits on memory corruption, unexpected write faults, bad UFFD event/ioctl behavior, worker creation/join errors, or unregister failures. Hugetlb shortage prints a skip message and returns `KSFT_SKIP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-stress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-unit-tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-unit-tests.c

## Purpose
Feature-matrix unit test driver for userfaultfd. It validates API negotiation, registration ioctl availability, zeropage, move, write-protect fork semantics, minor faults, signal delivery, non-cooperative events, poison, mmap-changing races, and backend-specific behavior across anonymous, shmem, shmem-private, hugetlb, and hugetlb-private memory.

## Important APIs, Types, and Functions
- `mem_type_t` maps memory names to backend flags, `uffd_test_ops`, and shared/private mode.
- `uffd_test_case_t` defines the unit-test table: name, function, target memory mask, required UFFD feature bits, and optional allocation hooks.
- `test_uffd_api()` validates syscall and `/dev/userfaultfd` API negotiation, bad API rejection, bad feature rejection, and double-initialization rejection.
- WP/fork coverage is in `uffd_wp_unpopulated_test()`, `uffd_wp_fork_test_common()`, and `uffd_wp_fork_pin_test_common()`.
- Minor-fault coverage is in `uffd_minor_test_common()`.
- Event/signal coverage is in `faulting_process()`, `uffd_sigbus_test_common()`, and `uffd_events_test_common()`.
- Zeropage, poison, and move coverage live in `uffd_zeropage_test()`, `uffd_poison_test()`, and `uffd_move_test_common()`.
- `uffd_mmap_changing_test()` validates ioctl behavior while a mmap-changing event is pending.

## Control Flow
`main()` parses `-f`, `-l`, and `-h`. Unless listing/filtering only, it first checks UFFD availability via both syscall and device paths. It then iterates tests and memory backends, filters unsupported backend/test combinations, checks feature bits via `uffd_get_features()`, initializes a one-thread UFFD test context, executes the test function, and clears the context. The test table is the authoritative control surface for coverage and feature gating.

## State and Persistence Behavior
All state is per-process: `gopts`, counters, UFFD fds, mappings, pagemap fds, gup_test fd state, signal jump buffer, and child process fds from `UFFD_EVENT_FORK`. Tests may interact with `/proc/self/pagemap`, `/sys/kernel/debug/gup_test`, and forked children. They do not intentionally persist files, but they rely on kernel debugfs and VM state.

## Dependencies and Integration Points
Depends on `uffd-common.h`, `vm_util.h`, `kselftest.h`, Linux `gup_test.h`, UFFD feature flags, `/proc/self/pagemap`, debugfs `gup_test`, pthreads, fork/wait, signals, and `madvise` behavior. It integrates with kselftest by manually maintaining pass/skip/fail counters and returning `KSFT_PASS` or `KSFT_FAIL`.

## Risks and Edge Cases
Feature gating is critical because many tests require newer UFFD features such as MOVE, POISON, WP_UNPOPULATED, EVENT_FORK, EVENT_REMAP, EVENT_REMOVE, and minor fault support. GUP pin tests skip if debugfs support or privilege is missing. Some paths intentionally rely on swap/pageout behavior, PMD collapse, or hugetlb limitations and may skip when unavailable. Error-injection tests expect exact errno/result-field behavior.

## Test Signals
The final line reports pass/skip/fail counts. Individual tests print `Testing <case> on <mem>... done`, `skipped`, or `failed`. Hard errors use `err()` for impossible internal states. The process returns fail if any kselftest failure counter is nonzero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-unit-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-wp-mremap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-wp-mremap.c

## Purpose
Kselftest validating that UFFD write-protect markers are cleared after `mremap()` when `UFFD_FEATURE_EVENT_REMAP` is not enabled. It exercises base pages, transparent huge pages, swapped pages, shared/private mappings, and hugetlb pages across detected supported sizes.

## Important APIs, Types, and Functions
- `detect_thp_sizes()` reads THP supported orders and computes supported THP sizes.
- `mmap_aligned()` creates manually aligned mappings for large folio sizes.
- `alloc_one_folio()` allocates and populates a base page, THP, or hugetlb folio.
- `check_uffd_wp_state()` reads `/proc/self/pagemap` and validates the `PM_UFFD_WP` bit on each base page.
- `range_is_swapped()` validates successful `MADV_PAGEOUT`.
- `test_one_folio()` is the core scenario runner for one size/private/swapout/hugetlb combination.

## Control Flow
`main()` detects base page size, THP sizes, and hugetlb sizes, disables THP globally for the test when needed, sets the kselftest plan to the number of size/testcase combinations, opens pagemap, and calls `test_one_folio()` for each case. Each case allocates a folio, registers it for UFFD-WP, applies write protection, optionally pages it out, confirms WP bits are set, moves the mapping to a new aligned address with `mremap(MREMAP_FIXED | MREMAP_MAYMOVE)`, and confirms WP bits are cleared.

## State and Persistence Behavior
State includes global page-size arrays, pagemap fd, and temporary THP settings via `thp_settings.h`. THP settings are saved, pushed, and restored. Mappings are unmapped and UFFD fds closed per case. Swapout state is transient kernel VM state.

## Dependencies and Integration Points
Uses `uffd-common.h`, `vm_util.h`, `thp_settings.h`, Linux UFFD and mmap ABI, `/proc/self/pagemap`, THP sysfs, hugetlb size detection, and kselftest plan/result APIs.

## Risks and Edge Cases
Cases can skip when userfaultfd is unavailable, THP or hugetlb allocation fails, swap is unavailable, or `MADV_PAGEOUT` does not actually swap the range. The aligned mapping logic assumes power-of-two folio sizes. Hugetlb swapout is explicitly disallowed by assertion.

## Test Signals
Each `test_one_folio(...)` emits a kselftest pass, fail, or skip line. Final exit is `ksft_exit_pass()` unless any failures are counted, in which case it reports the number failed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-wp-mremap.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/write_hugetlb_memory.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/write_hugetlb_memory.sh

## Purpose
Small wrapper that places the current shell process into a memory cgroup and invokes `write_to_hugetlbfs` with parameters used by hugetlb charge/reservation tests.

## Important APIs, Types, and Functions
- Accepts positional arguments for size, populate/write flags, cgroup name, hugetlb path, allocation method, private/shared mode, sleep behavior, and reservation mode.
- Writes `$$` to `${cgroup_path:-/dev/cgroup/memory}/$cgroup/cgroup.procs`.
- Runs `./write_to_hugetlbfs -p "$path" -s "$size" "$write" "$populate" -m "$method" "$private" "$want_sleep" "$reserve"`.

## Control Flow
The script enables `set -e`, parses positional variables, moves itself into the requested cgroup, prints the allocation method, disables `set -e`, then exec-style invokes the helper binary with translated flags.

## State and Persistence Behavior
It mutates cgroup membership by writing `cgroup.procs`. It does not clean up cgroups or hugetlb files itself; those responsibilities are in the surrounding test harness and helper program.

## Dependencies and Integration Points
Depends on bash, a writable cgroup v1 memory hierarchy by default, and the compiled `write_to_hugetlbfs` helper. Used by higher-level hugetlb memory charge tests rather than as a complete standalone test.

## Risks and Edge Cases
The script assumes the cgroup directory exists and is writable. Positional argument order is strict. Disabling `set -e` before the helper lets the helper return errors without immediate shell abort, so the caller must inspect exit status/output.

## Test Signals
Prints the target cgroup and method. The meaningful pass/fail signal is the helper program's exit code and output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/write_hugetlb_memory.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/write_to_hugetlbfs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/write_to_hugetlbfs.c

## Purpose
Helper program that reserves, maps, optionally populates, writes, and optionally holds hugetlb memory using hugetlbfs files, anonymous `MAP_HUGETLB`, or SysV shared memory. It supports scenarios needed by hugetlb cgroup charge/reservation tests.

## Important APIs, Types, and Functions
- `enum method` selects `HUGETLBFS`, `MMAP_MAP_HUGETLB`, or `SHM`.
- `exit_usage()` reports accepted flags: path, size, method, sleep, private, populate, write, and no-reserve.
- `sig_handler()` cleans up SysV shared memory on SIGINT.
- `main()` parses options, validates path/size/method, maps using the selected method, optionally `memset()`s the range, and optionally sleeps forever after printing `DONE`.

## Control Flow
After option parsing, the program prints selected behavior. For hugetlbfs it opens/creates the target path and mmaps it. For `MAP_HUGETLB` it maps anonymous or shared huge pages. For SysV SHM it tries key 0 and then key 1, attaches with `shmat()`, and records global cleanup pointers. It writes the range if requested and either exits or holds memory until signaled.

## State and Persistence Behavior
Hugetlbfs mode creates or opens a file at the provided path and maps it. SysV mode creates a shared memory segment and removes it on SIGINT cleanup. Sleep mode intentionally keeps hugepage reservations/charges alive. The program does not unlink hugetlbfs files on normal exit.

## Dependencies and Integration Points
Uses hugetlbfs, `MAP_HUGETLB`, `MAP_POPULATE`, `MAP_NORESERVE`, SysV SHM with `SHM_HUGETLB`, signals, and standard mmap/file APIs. It is invoked by `write_hugetlb_memory.sh` and larger hugetlb accounting tests.

## Risks and Edge Cases
Requires hugepage availability and usually elevated privileges/configuration. The `-r` case formatting is unusual but sets private mode. SysV cleanup is only implemented for SIGINT; other termination paths may leave segments until system cleanup or manual removal. Path length is capped by the fixed 256-byte buffer.

## Test Signals
Prints allocation choices, returned addresses or SHM ids, `Writing to memory`, and `DONE` when holding memory. Failures use `err()`/`perror()` with nonzero exit codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/write_to_hugetlbfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/module/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/module/Makefile

## Purpose
Kselftest makefile for module-loading selftests. It declares a shell-only test program and avoids building binaries.

## Important APIs, Types, and Functions
- `all:` is intentionally empty so an argument-less make does not run tests.
- `TEST_PROGS := find_symbol.sh` registers the runtime test.
- Includes `../lib.mk` for kselftest build/run plumbing.
- `clean:` is empty because there are no generated artifacts.

## Control Flow
Kselftest infrastructure reads `TEST_PROGS` and runs `find_symbol.sh`. No compilation or cleanup work is performed in this makefile.

## State and Persistence Behavior
No local state. It does not generate files.

## Dependencies and Integration Points
Integrates with `tools/testing/selftests/lib.mk` and the module `config` file in this directory.

## Risks and Edge Cases
The empty `all` target is a deliberate guard against unexpected test execution during plain make. Any future generated binaries would need corresponding clean rules.

## Test Signals
Signals are delegated to `find_symbol.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/module/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/module/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/module/config

## Purpose
Kernel configuration fragment for the module selftest.

## Important APIs, Types, and Functions
- Requires `CONFIG_TEST_RUNTIME=y`.
- Requires `CONFIG_TEST_RUNTIME_MODULE=y`.
- Requires `CONFIG_TEST_KALLSYMS=m`.

## Control Flow
No executable flow; kselftest build/config tooling consumes these symbols to ensure required test modules are available.

## State and Persistence Behavior
Static configuration metadata only.

## Dependencies and Integration Points
Pairs with `find_symbol.sh`, which loads `test_kallsyms_*` modules and depends on those modules being buildable/loadable.

## Risks and Edge Cases
If the kernel is not built with these options, the shell test will skip or fail when modules cannot be loaded.

## Test Signals
No runtime signal from the config file itself.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/module/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/module/find_symbol.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/module/find_symbol.sh

## Purpose
Stress script for kallsyms `find_symbol()` behavior by repeatedly loading a test module while the module symbol namespace is empty or polluted with other test modules.

## Important APIs, Types, and Functions
- `test_reqs()` verifies `modprobe`, `kmod`, `perf`, and root privileges.
- `load_mod()` times or profiles module loading; on x86_64 it uses `perf stat` with duration, user/system time, and page faults.
- `remove_all()` removes `test_kallsyms_b` and test modules `a` through `d`.

## Control Flow
After requirement checks, the script gets the module loader path from `/proc/sys/kernel/modprobe`, removes existing test modules, loads `test_kallsyms_b`, removes all modules, then repeats the load with namespace pollution from `test_kallsyms_c`, and finally with both `test_kallsyms_c` and `test_kallsyms_d`.

## State and Persistence Behavior
It mutates kernel module state by loading and unloading test modules. No repository files are changed. The script attempts to clean module state before and between scenarios.

## Dependencies and Integration Points
Depends on the configured test modules from this directory's `config`, root privilege, `modprobe`, `kmod`, optionally x86_64 `perf`, and kernel module loading support.

## Risks and Edge Cases
Non-x86_64 path uses `time` and exits 1 after the first module load, which makes non-x86 behavior intentionally limited or failing. `set -e` means any failed modprobe removal/load aborts. Root and tool availability are required.

## Test Signals
Missing requirements exit with kselftest skip code 4. Successful completion exits 0. `perf stat` output is the main performance/behavior signal for each load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/module/find_symbol.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount/Makefile

## Purpose
Build and register classic mount namespace selftests for unprivileged remount behavior and `MS_NOSYMFOLLOW`.

## Important APIs, Types, and Functions
- Sets `CFLAGS = -Wall -O2`.
- `TEST_PROGS := run_unprivileged_remount.sh run_nosymfollow.sh`.
- `TEST_GEN_FILES := unprivileged-remount-test nosymfollow-test`.
- Includes `../lib.mk`.

## Control Flow
The makefile compiles two C helpers and registers two shell wrappers as test programs. Kselftest invokes the wrappers, not the helpers directly.

## State and Persistence Behavior
Generated binaries are build artifacts managed by kselftest. No runtime state is defined here.

## Dependencies and Integration Points
Depends on kselftest `lib.mk` and the directory `config` requesting user namespaces.

## Risks and Edge Cases
The wrappers assume binaries are in the current test execution directory. Compiler flags are minimal and do not include special kernel headers.

## Test Signals
Build success produces `unprivileged-remount-test` and `nosymfollow-test`; runtime signals come from the wrappers/helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount/config

## Purpose
Kernel configuration fragment for mount namespace selftests.

## Important APIs, Types, and Functions
- Requires `CONFIG_USER_NS=y`.

## Control Flow
No executable flow. Kselftest config tooling consumes it before running mount tests.

## State and Persistence Behavior
Static metadata only.

## Dependencies and Integration Points
Supports `nosymfollow-test.c` and `unprivileged-remount-test.c`, both of which create user namespaces.

## Risks and Edge Cases
If user namespaces are disabled by kernel config or runtime policy, wrappers skip or helpers fail during `unshare(CLONE_NEWUSER)`.

## Test Signals
None directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/nosymfollow-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount/nosymfollow-test.c

## Purpose
Validates `MS_NOSYMFOLLOW` remount semantics in an unprivileged user/mount namespace. It confirms symlink traversal is blocked after remount while `readlink()` and `realpath()` behavior and `statfs()` flags remain correct.

## Important APIs, Types, and Functions
- Namespace helpers `create_and_enter_ns()`, `write_file()`, and `maybe_write_file()`.
- `setup_symlink()` creates `/tmp/data` and `/tmp/symlink`.
- `test_link_traversal()` expects successful open without nosymfollow and `ELOOP` with nosymfollow.
- `test_readlink()`, `test_realpath()`, and `test_statfs()` validate unaffected symlink inspection and flag reporting.
- `run_tests()` runs the four checks for the current mount state.

## Control Flow
The program enters a new user namespace, maps current uid/gid to root, enters a new mount namespace, mounts ramfs on `/tmp`, creates the symlink setup, runs tests without nosymfollow, remounts `/tmp` with `MS_REMOUNT | MS_NOSYMFOLLOW`, and runs tests again expecting traversal denial and `ST_NOSYMFOLLOW`.

## State and Persistence Behavior
All filesystem changes are in a private mount namespace on `/tmp`. It creates `DATA` and `LINK` paths inside the ramfs. No intended host persistence occurs once the namespace exits.

## Dependencies and Integration Points
Requires user namespaces, mount namespaces, ramfs, mount/remount support, and the kernel `MS_NOSYMFOLLOW`/`ST_NOSYMFOLLOW` ABI. Invoked by `run_nosymfollow.sh`.

## Risks and Edge Cases
The test uses fixed `/tmp` paths inside the new namespace after mounting ramfs, so failure to isolate would be dangerous; namespace setup must succeed first. `realpath()` is expected to resolve the symlink even though later open traversal is denied under nosymfollow.

## Test Signals
Success exits 0. Any unexpected syscall result prints a detailed message and exits failure through `die()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/nosymfollow-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/run_nosymfollow.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount/run_nosymfollow.sh

## Purpose
Minimal kselftest wrapper that runs the compiled `nosymfollow-test` binary.

## Important APIs, Types, and Functions
- Executes `./nosymfollow-test`.

## Control Flow
No branching; the script delegates all logic and exit status to the C helper.

## State and Persistence Behavior
No state beyond the helper's namespace-local filesystem work.

## Dependencies and Integration Points
Requires the helper binary to be built in the current directory.

## Risks and Edge Cases
If the binary is missing or not executable, the wrapper fails directly.

## Test Signals
Exit code and output are from `nosymfollow-test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/run_nosymfollow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/run_unprivileged_remount.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount/run_unprivileged_remount.sh

## Purpose
Kselftest wrapper that runs `unprivileged-remount-test` when user namespace mapping support is visible.

## Important APIs, Types, and Functions
- Defines `ksft_skip=4`.
- Checks for `/proc/self/uid_map`.
- Executes `./unprivileged-remount-test` or prints a warning and exits skip.

## Control Flow
The script gates the C helper on uid-map availability, then delegates execution and exit status to the helper.

## State and Persistence Behavior
No direct state changes beyond running the helper.

## Dependencies and Integration Points
Requires `/proc/self/uid_map` and the compiled helper. Registered by the mount `Makefile`.

## Risks and Edge Cases
The presence of `/proc/self/uid_map` does not guarantee `unshare(CLONE_NEWUSER)` is permitted by runtime policy, so the helper can still fail.

## Test Signals
Missing uid map exits 4. Otherwise the helper's exit code is returned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/run_unprivileged_remount.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/unprivileged-remount-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount/unprivileged-remount-test.c

## Purpose
Validates which mount flags unprivileged users can preserve or reject across nested user and mount namespaces. It ensures security-sensitive flags and atime policy changes behave correctly when remounting bind mounts without initial privileges.

## Important APIs, Types, and Functions
- Namespace/mapping helpers `create_and_enter_userns()`, `write_file()`, and `maybe_write_file()`.
- `read_mnt_flags()` converts `statvfs()` flags into mount flag bits and rejects unknown flags.
- `test_unpriv_remount()` is the core child-process scenario for mounting, entering a second user/mount namespace, remounting with valid flags, then verifying invalid flags fail.
- `test_unpriv_remount_simple()` and `test_unpriv_remount_atime()` specialize common cases.
- `test_priv_mount_unpriv_remount()` bind-mounts `/dev` and verifies remount preserves original flags.

## Control Flow
`main()` runs a sequence of cases for `MS_RDONLY`, `MS_NODEV`, `MS_NOSUID`, `MS_NOEXEC`, and multiple atime combinations. Each case forks so namespace and mount mutations are isolated. The child creates a privileged-in-namespace mount, enters another user/mount namespace, remounts `/tmp` as a bind mount with allowed flags, verifies an invalid remount is rejected, and exits. The final case ensures a privileged source mount's flags do not unexpectedly change after unprivileged bind remount.

## State and Persistence Behavior
State is isolated in child user/mount namespaces and on `/tmp` mounts. Parent process only observes child exit codes. No persistent repository or host filesystem files are intentionally changed.

## Dependencies and Integration Points
Requires user namespaces, mount namespaces, ramfs, devpts for one case, bind mounts, `statvfs`, and mount flag ABI definitions. Invoked by `run_unprivileged_remount.sh`.

## Risks and Edge Cases
Mount namespace/user namespace restrictions can cause hard failures. The test intentionally dies on unknown `statvfs` flags, so newer flags may require updates. It relies on `/tmp` being usable as a mount target in isolated namespaces.

## Test Signals
Success exits 0. Each failed scenario calls `die()` with a descriptive message; wrapper may skip if uid maps are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/unprivileged-remount-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/Makefile

## Purpose
Builds the modern mount API selftest program `mount_setattr_test`.

## Important APIs, Types, and Functions
- `CFLAGS = -g $(KHDR_INCLUDES) -Wall -O2 -pthread`.
- Adds local header dependency `../filesystems/wrappers.h`.
- `TEST_GEN_PROGS := mount_setattr_test`.
- Includes `../lib.mk`.

## Control Flow
Kselftest builds the single harness-based test binary with pthread support and kernel header includes.

## State and Persistence Behavior
Only build artifacts are generated.

## Dependencies and Integration Points
Uses kselftest `lib.mk`, kernel headers, pthreads, and wrappers for modern filesystem/mount syscalls.

## Risks and Edge Cases
If kernel headers lack newer mount constants, the C file contains fallback definitions for many of them. Missing wrapper header would break the build.

## Test Signals
Build success creates `mount_setattr_test`; runtime results are emitted by the kselftest harness in the C file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/config

## Purpose
Kernel configuration fragment for `mount_setattr` selftests.

## Important APIs, Types, and Functions
- Requires `CONFIG_USER_NS=y`.

## Control Flow
Static configuration metadata only.

## State and Persistence Behavior
No runtime state.

## Dependencies and Integration Points
Supports the test binary's repeated use of unprivileged user namespaces and mount namespaces.

## Risks and Edge Cases
Runtime policy can still disable unprivileged user namespaces even if the config symbol exists.

## Test Signals
None directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/mount_setattr_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/mount_setattr_test.c

## Purpose
Large kselftest harness suite for the `mount_setattr()` and related modern mount APIs. It validates mount attribute changes, recursive behavior, writer rollback, propagation, namespace permissions, idmapped mount restrictions, `MOUNT_ATTR_NOSYMFOLLOW`, `open_tree_attr()`, detached mount trees, and anonymous mount namespace lifetime rules.

## Important APIs, Types, and Functions
- Syscall wrappers `sys_mount_setattr()` and `sys_open_tree_attr()` plus wrappers from `../filesystems/wrappers.h` for `open_tree`, `move_mount`, `fsopen`, `fsconfig`, and `fsmount`.
- Namespace helpers `create_and_enter_userns()` and `prepare_unpriv_mountns()`.
- Flag helpers `read_mnt_flags()` and `is_shared_mount()`.
- Fixture `mount_setattr` creates a layered `/mnt` and `/tmp` tree with tmpfs, ramfs, devpts, bind mounts, and symlink targets.
- Fixture `mount_setattr_idmapped` additionally creates an ext4 loop image and mount for idmapped mount tests.
- User namespace fd helpers `map_ids()`, `do_clone()`, `get_userns_fd()`, and `expected_uid_gid()` support idmap cases.

## Control Flow
The primary fixture enters an unprivileged user/mount namespace, makes `/` private, mounts controlled filesystems under `/tmp` and `/mnt`, creates nested bind mounts, and prepares symlink test data. Tests then call `mount_setattr()` with valid and invalid attribute structures, recursive and nonrecursive flags, writer-held mounts, mixed option trees, time policy transitions, multithreaded calls, wrong namespace contexts, and nosymfollow toggling. Detached mount tests clone trees with `open_tree`, attach them via `move_mount`, check mount-root and unique mount IDs with `statx`, and verify invalid namespace or subtree operations fail.

## State and Persistence Behavior
Most state is isolated in private user/mount namespaces. The idmapped fixture creates `/mnt/C/ext4.img`, formats it with `mkfs.ext4`, and loop-mounts it at `/mnt/D` inside the test namespace. Tests mutate mount flags, propagation groups, anonymous mount namespaces, detached tree fds, and idmap state. Fixture teardown detaches `/mnt/A` and `/tmp`, but many effects are namespace-scoped.

## Dependencies and Integration Points
Requires user namespaces, mount namespaces, tmpfs, ramfs, devpts, ext4 tooling (`mkfs.ext4`), loop mounting, modern mount syscalls, `statx` mount attributes, pthreads, and kselftest harness macros. It integrates directly with kernel mount API compatibility and permission semantics.

## Risks and Edge Cases
The suite is sensitive to kernel support; unsupported `mount_setattr` is skipped through `SKIP`/`XFAIL`. The idmapped fixture is heavier than most selftests because it creates and formats a 2 GiB sparse image. Recursive changes must be atomic on failure when writers exist; the tests explicitly check rollback. Namespace ownership, detached tree roots, and anonymous namespace lifetimes are subtle and heavily validated.

## Test Signals
Uses `TEST_F`/`ASSERT_*`/`EXPECT_*` kselftest harness output. Skips occur when syscalls are unsupported. Failures include mismatched flags, unexpected errno values, symlink traversal behavior, mount-root identity problems, idmap uid/gid mismatches, and invalid detached tree operations succeeding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/mount_setattr_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/Makefile

## Purpose
Builds the `move_mount_set_group_test` kselftest binary for `MOVE_MOUNT_SET_GROUP`.

## Important APIs, Types, and Functions
- `CFLAGS = -g $(KHDR_INCLUDES) -Wall -O2`.
- `TEST_GEN_FILES += move_mount_set_group_test`.
- Includes `../lib.mk`.

## Control Flow
Kselftest compiles the single C helper and runs it as a generated test file.

## State and Persistence Behavior
Only build artifacts are created.

## Dependencies and Integration Points
Depends on kernel headers and kselftest `lib.mk`.

## Risks and Edge Cases
No pthread flag is needed here. Runtime support is checked inside the C test.

## Test Signals
Build success creates `move_mount_set_group_test`; runtime signals come from the harness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/config

## Purpose
Kernel configuration fragment for the `MOVE_MOUNT_SET_GROUP` selftest.

## Important APIs, Types, and Functions
- Requires `CONFIG_USER_NS=y`.

## Control Flow
No executable behavior.

## State and Persistence Behavior
Static metadata only.

## Dependencies and Integration Points
Supports the C test's unprivileged namespace setup.

## Risks and Edge Cases
Kernel config does not guarantee the `MOVE_MOUNT_SET_GROUP` flag is implemented; the test probes that at runtime.

## Test Signals
None directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/move_mount_set_group_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/move_mount_set_group_test.c

## Purpose
Kselftest for `move_mount(..., MOVE_MOUNT_SET_GROUP)`, validating that sharing/propagation group state can be copied from one mount to another across nested namespace scenarios.

## Important APIs, Types, and Functions
- Namespace helpers `create_and_enter_userns()` and `prepare_unpriv_mountns()`.
- `is_shared_mount()` parses `/proc/self/mountinfo` to detect a `shared:` propagation tag for a path.
- `move_mount_set_group_supported()` builds a temporary mount setup and probes `__NR_move_mount` with `MOVE_MOUNT_SET_GROUP`.
- `get_nestedns_mount_cb()` creates a nested unprivileged mount namespace, optionally marks a mount shared, and returns user/mount namespace fds and a mount fd through shared clone memory.
- `complex_sharing_copying` is the core harness test.

## Control Flow
Fixture setup enters an unprivileged private mount namespace, probes support, remounts `/tmp`, and mounts tmpfs at `/tmp/A`. The test creates two cloned child contexts sharing memory/files: one with `/tmp/A` marked shared and one private. It then calls `move_mount` with source and target empty-path fds plus `MOVE_MOUNT_SET_GROUP`, enters the target mount namespace, and verifies `/tmp/A` is shared there.

## State and Persistence Behavior
All mount changes are namespace-local. The test opens namespace and mount fds from child contexts and uses them after the child exits. It detaches `/tmp` in fixture teardown.

## Dependencies and Integration Points
Requires user/mount namespaces, tmpfs, `move_mount` syscall, `MOVE_MOUNT_SET_GROUP`, `setns`, clone with `CLONE_VFORK | CLONE_VM | CLONE_FILES`, and kselftest harness.

## Risks and Edge Cases
Runtime flag support is not assumed. Passing fds through clone-shared memory is concise but sensitive to clone flags and child completion. The test validates propagation through mountinfo parsing, which depends on stable mountinfo optional field formatting.

## Test Signals
Unsupported flag is skipped/XFAIL. Assertions validate setup, syscall success, namespace switch, and final shared propagation state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/move_mount_set_group_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/Makefile

## Purpose
Builds POSIX message queue correctness and performance selftests.

## Important APIs, Types, and Functions
- `CFLAGS += -O2`.
- `LDLIBS = -lrt -lpthread -lpopt`.
- `TEST_GEN_PROGS := mq_open_tests mq_perf_tests`.
- Includes `../lib.mk`.

## Control Flow
Kselftest compiles both C programs and links realtime, pthread, and popt libraries.

## State and Persistence Behavior
Only build artifacts are generated.

## Dependencies and Integration Points
Requires POSIX mqueue library support, pthreads, popt, and kselftest infrastructure.

## Risks and Edge Cases
The runtime tests need root to adjust mqueue sysctls and resource limits; build success alone does not imply they can run fully.

## Test Signals
Build creates `mq_open_tests` and `mq_perf_tests`; runtime output comes from those programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/mq_open_tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/mq_open_tests.c

## Purpose
Correctness test for POSIX `mq_open()` behavior under different system defaults, maxima, resource limits, attributes, and effective user IDs.

## Important APIs, Types, and Functions
- Global sysctl paths cover `/proc/sys/fs/mqueue/msg_default`, `msgsize_default`, `msg_max`, and `msgsize_max`.
- `shutdown()` restores sysctls, closes/unlinks the queue, and exits.
- `get()`, `set()`, `getr()`, and `setr()` read/write sysctls and `RLIMIT_MSGQUEUE`.
- `validate_current_settings()` adjusts defaults/maxima if current limits are too low for testing.
- `test_queue()` creates a queue and treats failure as fatal.
- `test_queue_fail()` attempts queue creation where failure may be expected.

## Control Flow
`main()` normalizes the queue path, skips if not root, opens sysctl files, saves current sysctl and rlimit state, prints initial settings, validates/adjusts settings, then runs two broad series. Series 1 tests behavior when `mq_open()` is called without attributes, including default knobs and defaults greater than maxima/rlimit. Series 2 tests explicit attributes that exceed rlimit or maxima first as euid 0 and then after dropping to euid 99.

## State and Persistence Behavior
The program mutates mqueue sysctls and `RLIMIT_MSGQUEUE`, creates/unlinks a POSIX message queue, and temporarily changes effective uid. `shutdown()` restores saved sysctls and unlinks the queue on normal and error paths.

## Dependencies and Integration Points
Requires root, writable mqueue sysctls, POSIX mqueue support, `mq_open`, `mq_getattr`, `mq_unlink`, and kselftest skip support. Linked by the mqueue makefile with realtime/pthread/popt libraries, though this file mainly uses librt mqueue APIs.

## Risks and Edge Cases
The test prints PASS/FAIL text for subconditions but does not consistently increment kselftest counters. `shutdown()` must be reached to restore sysctls; abrupt termination may leave changed settings. Some kernels may not expose separate default sysctls, and the code handles both default-supported and legacy tied-to-max behavior.

## Test Signals
Root absence exits with kselftest skip. The test prints PASS/FAIL lines for each scenario and exits 0 through `shutdown(0, "", 0)` unless a fatal syscall/sysctl error occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/mq_open_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/mq_perf_tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/mq_perf_tests.c

## Purpose
Performance and stress benchmark for POSIX message queues, focused on large queue depths, send/receive latency, priority ordering patterns, and optional continuous cache-thrashing workloads pinned to selected CPUs.

## Important APIs, Types, and Functions
- Command-line options use popt: `--continuous/-c`, `--fake/-f`, and `--path/-p`.
- `shutdown()` frees CPU sets, stops worker threads, closes/unlinks the queue, and restores sysctls.
- `increase_limits()` raises `RLIMIT_MSGQUEUE`, grows mqueue maxima as far as accepted, and raises process priority.
- `open_queue()` creates the global queue and records actual attributes.
- Continuous workers: `cont_thread()` repeatedly fills and drains one message; `fake_cont_thread()` busy loops without mqueue operations.
- Benchmark worker `perf_test_thread()` times send/receive on an empty queue and near-full queue with constant, increasing, decreasing, and random priorities.

## Control Flow
`main()` requires root, parses CPU/path options, allocates a CPU set, opens and saves mqueue sysctls/limits, installs signal handlers, raises limits, opens the queue unless fake mode is selected, and creates CPU-pinned worker threads. Non-continuous mode runs one `perf_test_thread()` on the last online CPU and exits through cleanup. Continuous mode sleeps forever while worker threads run until signaled.

## State and Persistence Behavior
The program mutates mqueue sysctls, process rlimits, process nice value, CPU affinity, signal handlers, and a POSIX message queue. Cleanup restores sysctls and unlinks the queue, but it does not restore the nice value. Continuous mode intentionally persists until killed.

## Dependencies and Integration Points
Requires root, POSIX mqueue support, writable `/proc/sys/fs/mqueue` controls, pthread CPU affinity APIs, popt, realtime clocks, and scheduler/resource-limit syscalls. Built by the mqueue makefile.

## Risks and Edge Cases
`increase_limits()` loops until sysctls stop accepting larger values; behavior depends on kernel caps. Continuous fake mode does not open a queue and just consumes CPU. Signal-driven cleanup is important because worker threads can run forever. The CPU parser ignores out-of-range CPUs and rejects duplicate CPUs.

## Test Signals
Output includes initial/adjusted system state, queue attributes, timing totals, and nanoseconds per message for each workload. Root absence exits skip. Fatal errors call `shutdown()` with nonzero exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/mq_perf_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/Makefile

## Purpose
Builds the `sysmap_is_sealed` selftest for mseal-protected system mappings.

## Important APIs, Types, and Functions
- `CFLAGS += -std=c99 -pthread -Wall $(KHDR_INCLUDES)`.
- `TEST_GEN_PROGS := sysmap_is_sealed`.
- Includes `../lib.mk`.

## Control Flow
Kselftest compiles one generated test program with C99, pthreads, warnings, and kernel header includes.

## State and Persistence Behavior
Only build artifacts are produced.

## Dependencies and Integration Points
Depends on kselftest `lib.mk`, kernel headers, pthread support, and the corresponding source file outside this subset.

## Risks and Edge Cases
The makefile assumes the `sysmap_is_sealed` source exists in the directory. Runtime behavior depends on mseal system mapping support requested by config.

## Test Signals
Build success creates the `sysmap_is_sealed` binary; runtime signals come from that binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/config

## Purpose
Kernel configuration fragment for mseal system mapping selftests.

## Important APIs, Types, and Functions
- Requires `CONFIG_MSEAL_SYSTEM_MAPPINGS=y`.

## Control Flow
No executable flow; consumed by kselftest config tooling.

## State and Persistence Behavior
Static metadata only.

## Dependencies and Integration Points
Supports the `sysmap_is_sealed` test built by the directory makefile.

## Risks and Edge Cases
If the kernel lacks system mapping mseal support, the runtime test cannot validate the intended behavior.

## Test Signals
None directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/config -->
