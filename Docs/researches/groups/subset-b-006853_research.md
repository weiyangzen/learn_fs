# subset-b-006853 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksm_tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksm_tests.c

## Purpose

`ksm_tests.c` is a Linux mm kselftest executable for Kernel Samepage Merging. It validates basic page merge and unmerge behavior, zero-page merging, NUMA-aware merging, and timing-oriented KSM performance paths. The same program can exercise both VMA-level `MADV_MERGEABLE` opt-in and process-wide `PR_SET_MEMORY_MERGE` opt-in.

## Important APIs, Types, and Functions

The main state type is `struct ksm_sysfs`, a snapshot of `/sys/kernel/mm/ksm` tunables that the test modifies and later restores. `enum ksm_merge_type` chooses `madvise(MADV_MERGEABLE)` versus `prctl(PR_SET_MEMORY_MERGE)`. `enum ksm_test_name` selects the command-line test mode.

Key helpers are `ksm_write_sysfs()`/`ksm_read_sysfs()`, `allocate_memory()`, `ksm_do_scan()`, `ksm_merge_pages()`, `ksm_unmerge_pages()`, `assert_ksm_pages_count()`, `ksm_save_def()`, and `ksm_restore()`. Test bodies are `check_ksm_merge()`, `check_ksm_unmerge()`, `check_ksm_zero_page_merge()`, `check_ksm_numa_merge()`, `ksm_merge_time()`, `ksm_merge_hugepages_time()`, `ksm_unmerge_time()`, and `ksm_cow_time()`.

## Control Flow

`main()` parses flags, verifies that KSM sysfs exists, saves current tunables, forces an aggressive scan configuration, runs one selected test, restores the original sysfs values, and returns the kselftest status. Merge tests allocate duplicate anonymous pages, opt them into KSM, start scanning by writing `run=1`, wait for enough `full_scans`, then compare `pages_shared` and `pages_sharing` against the expected sharing model. Unmerge tests write into merged pages and wait for KSM to observe the change. Timing paths measure scan, unmerge, or COW duration using `CLOCK_MONOTONIC_RAW`.

## State and Persistence Behavior

The test mutates persistent kernel tunables under `/sys/kernel/mm/ksm`: `run`, `pages_to_scan`, `sleep_millisecs`, `merge_across_nodes`, `use_zero_pages`, `max_page_sharing`, and `stable_node_chains_prune_millisecs`. It attempts to restore them before exit. Runtime allocations are anonymous mappings or NUMA allocations and are unmapped/freed in normal paths. `PR_SET_MEMORY_MERGE` process state is cleared where used.

## Dependencies and Integration Points

It depends on kselftest helpers, `vm_util.h`, `thp_settings.h`, libnuma, KSM sysfs, `/proc/self/ksm_stat`, `/proc/self/pagemap`, and transparent hugepage support for the hugepage timing mode. It integrates with the mm selftests Makefile as an opt-in executable that often requires root or writable KSM sysfs.

## Risks and Edge Cases

The `ksm_save_def()` and `ksm_restore()` expressions mix `||` with a ternary around `numa_available()`, which is subtle and easy to misread. Tests can leave sysfs tunables changed if they fail before restore. Timing tests are noisy and depend on scan speed, THP availability, NUMA topology, and page count. `assert_ksm_pages_count()` accounts for `max_page_sharing` groups and a leftover-page corner case. Hugepage counting includes a duplicated increment after `allocate_transhuge()` success in the visible code, so printed hugepage counts should be treated as diagnostic rather than a strict oracle.

## Test Signals

Pass signals are exact KSM counter relationships, successful unmerge to zero shared pages, zero-page behavior matching `use_zero_pages`, NUMA merge behavior matching `merge_across_nodes`, and timing output for merge/unmerge/COW scenarios. Skip signals include missing KSM, missing NUMA, insufficient NUMA nodes, or disabled THP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksm_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/madv_populate.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/madv_populate.c

## Purpose

`madv_populate.c` tests `MADV_POPULATE_READ` and `MADV_POPULATE_WRITE` on private anonymous memory. It verifies protection checks, hole handling, pagemap population, and soft-dirty semantics.

## Important APIs, Types, and Functions

The file uses `madvise()`, `mmap()`, `munmap()`, `/proc/self/pagemap`, `clear_softdirty()`, `softdirty_supported()`, `pagemap_is_populated()`, and `pagemap_is_softdirty()`. Helpers include `sense_support()`, `range_is_populated()`, `range_is_not_populated()`, `range_is_softdirty()`, and `range_is_not_softdirty()`.

## Control Flow

`main()` sets a plan of 16 tests, adds five more when soft-dirty is available, probes support with one-page `madvise()` calls, then runs protection, hole, population, and soft-dirty cases. `test_prot_read()` expects read population to work on `PROT_READ` and write population to fail with `EINVAL`. `test_prot_write()` expects the inverse for `PROT_WRITE`. `test_holes()` creates an unmapped page in a 2 MiB range and expects `ENOMEM` for middle, beginning, and end holes. Populate tests confirm initially absent PTEs become present. The soft-dirty test confirms read population does not dirty pages while write population does.

## State and Persistence Behavior

The test uses transient anonymous mappings and closes pagemap file descriptors after each scan. It writes to the process soft-dirty reset interface through `clear_softdirty()` and observes per-page bits through pagemap, but it does not persist data outside the process.

## Dependencies and Integration Points

It depends on `linux/mman.h` definitions for the populate advice constants, `kselftest.h`, and `vm_util.h`. The test is part of the mm selftest suite and exercises kernel page fault/population paths without requiring external files or hardware topology.

## Risks and Edge Cases

The test assumes private anonymous mappings and 2 MiB fixed test size. Pagemap visibility may be restricted by kernel configuration or permissions. Old kernels skip at support probing. Hole tests rely on `munmap(addr + pagesize, pagesize)` creating a true unmapped gap inside a previously contiguous area.

## Test Signals

Success is reported through individual `ksft_test_result()` checks for expected return values, `errno`, pagemap population state, and soft-dirty state. Any accumulated failure causes `ksft_exit_fail_msg()` at the end.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/madv_populate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/map_fixed_noreplace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/map_fixed_noreplace.c

## Purpose

`map_fixed_noreplace.c` validates `MAP_FIXED_NOREPLACE`: mappings must fail if any requested page overlaps an existing VMA and must succeed when merely adjacent.

## Important APIs, Types, and Functions

The file uses `mmap()`, `munmap()`, `sysconf(_SC_PAGE_SIZE)`, `errno`, and kselftest result helpers. `find_base_addr()` reserves and immediately releases a five-page address window to produce a likely free base. `dump_maps()` prints `/proc/<pid>/maps` for failure diagnostics.

## Control Flow

`main()` finds a base address, verifies a five-page mapping can be established there, unmaps it, maps the middle three pages, then tests five-page, contained, end-overlap, start-overlap, start-adjacent, and end-adjacent requests. Overlap cases must return `MAP_FAILED`; adjacency cases must succeed. The final five-page unmap validates cleanup.

## State and Persistence Behavior

All state is process-local VMA layout. The test intentionally creates and removes anonymous `PROT_NONE` mappings at fixed addresses. It does not write persistent files.

## Dependencies and Integration Points

The test integrates with the mm selftest suite and directly exercises kernel VMA collision detection for `MAP_FIXED_NOREPLACE`, a flag used by allocators and runtimes that require deterministic address placement without clobbering existing mappings.

## Risks and Edge Cases

The free base address is discovered by a reservation/unmap race against the same process, but other mappings could still appear between discovery and testing. The test treats unexpected success on overlap as fatal because that would imply the flag replaced a mapping. It does not assert the exact `errno`, only success/failure behavior.

## Test Signals

There are nine planned pass results covering initial mapping, four overlap failures, two adjacency successes, and final unmap success. Failure paths dump maps to make address layout visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/map_fixed_noreplace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/map_hugetlb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/map_hugetlb.c

## Purpose

`map_hugetlb.c` is a simple hugetlb mapping smoke test. It maps a large anonymous `MAP_HUGETLB` area, writes a deterministic byte pattern, reads it back, and unmaps with a hugepage-aligned length.

## Important APIs, Types, and Functions

The test uses `default_huge_page_size()` from `vm_util.h`, `mmap(MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB)`, optional `MAP_HUGE_SHIFT` size selection, `munmap()`, and kselftest helpers. `write_bytes()` fills every byte with `(char)i`; `read_bytes()` verifies the pattern.

## Control Flow

`main()` chooses a default 256 MiB length, raises it to at least one default huge page if needed, optionally overrides length in MiB and hugepage shift from argv, maps the region, logs the returned address, writes and validates all bytes, and unmaps.

## State and Persistence Behavior

The only state is a transient hugetlb-backed anonymous mapping. The test consumes reserved hugetlb pages while running and releases them on successful `munmap()`.

## Dependencies and Integration Points

It depends on configured huge pages in the system pool and mm selftest helpers. It exercises hugetlb allocation, access, and strict hugepage-aligned unmap behavior.

## Risks and Edge Cases

The test fails rather than skips when no huge pages are available. Large byte-by-byte validation can be slow. Argument parsing with `atol()`/`atoi()` is minimal. `shift` handling relies on Linux hugepage flag encodings.

## Test Signals

The single planned result is successful readback of the written pattern. Setup or teardown failures exit with detailed messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/map_hugetlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/map_populate.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/map_populate.c

## Purpose

`map_populate.c` verifies that `MAP_PRIVATE | MAP_POPULATE` faults private file-backed pages without turning them into shared views of later file updates. It protects copy-on-write semantics for populated private mappings.

## Important APIs, Types, and Functions

The test uses `tmpfile()`, `ftruncate()`, `mmap(MAP_SHARED)`, `mmap(MAP_PRIVATE | MAP_POPULATE)`, `msync()`, `socketpair()`, `fork()`, and kselftest counters. `parent_f()` coordinates a file-backed shared update, while `child_f()` validates the private populated mapping.

## Control Flow

The parent creates a one-page temporary file, shared-maps it, writes `0xdeadbabe`, and forks. The child maps the same fd as private+populate, verifies the initial value, then waits. The parent overwrites the shared mapping with `0x22222BAD` and syncs. The child confirms its private mapping still contains the original value and does not observe the parent update.

## State and Persistence Behavior

State is held in an unnamed temporary file and per-process VMAs. The socketpair enforces deterministic ordering. The parent copies child kselftest pass/fail counters out of the exit status because normal kselftest counters are process-local.

## Dependencies and Integration Points

It depends on normal file truncation support and skips through `skip_test_dodgy_fs()` if `ftruncate()` hits a known unsuitable filesystem. It integrates with mm COW and readahead/populate behavior.

## Risks and Edge Cases

The child returns the number of passed child assertions as an exit code, so the plan assumes only two child checks. Filesystems with unusual temporary file semantics can alter setup. The test validates one machine word in one page rather than a broad range.

## Test Signals

Success is the child observing the original `0xdeadbabe` after the parent writes and syncs `0x22222BAD`, with two child-side pass results surfaced to the parent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/map_populate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mdwe_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mdwe_test.c

## Purpose

`mdwe_test.c` tests Memory Deny Write Execute prctl behavior. It validates prctl argument checks, monotonic flag changes, inheritance behavior across fork, and mmap/mprotect behavior when executable permission is gained.

## Important APIs, Types, and Functions

The file uses `PR_SET_MDWE`, `PR_GET_MDWE`, `PR_MDWE_REFUSE_EXEC_GAIN`, `PR_MDWE_NO_INHERIT`, `mmap()`, `mprotect()`, and kselftest harness fixtures. `FIXTURE_VARIANT(consecutive_prctl_flags)` covers repeated prctl combinations. `FIXTURE_VARIANT(mdwe)` covers stock, enabled, inherited, and no-inherit process states. `executable_map_should_fail()` centralizes expected denial rules.

## Control Flow

The standalone `prctl_flags` test asserts that invalid flag and nonzero unused arguments fail with `EINVAL`. The consecutive-prctl fixture checks that MDWE can be kept but not weakened or retroactively changed to add/remove `NO_INHERIT`. The `mdwe` fixture optionally enables MDWE, optionally forks, and then runs mapping tests. `mmap(PROT_READ|PROT_EXEC)` and staying executable are allowed; write+exec mappings and adding exec to a writable mapping are denied when MDWE applies. `MAP_FIXED` replacement is expected to work because it unmaps before mapping. The arm64 BTI test verifies `PROT_BTI` can be added to executable mappings when hardware supports it.

## State and Persistence Behavior

MDWE state is per-process prctl state and may be inherited by fork unless `PR_MDWE_NO_INHERIT` is set. Test VMAs are unmapped in fixture teardown. Parent processes in forked fixture variants exit with the child result.

## Dependencies and Integration Points

It depends on kernel MDWE prctl support in `linux/prctl.h`, architecture BTI support on arm64, and kselftest harness. It integrates with executable mapping policy, JIT hardening, and W^X enforcement paths.

## Risks and Edge Cases

Unsupported MDWE appears as fixture assertion failure rather than a broad up-front skip. Forked fixture control flow exits from the parent inside setup, which is intentional but unusual. BTI is architecture-conditional and skipped unless `HWCAP2_BTI` is present.

## Test Signals

Passes require exact `errno` for invalid prctl calls, exact `PR_GET_MDWE` flag values after valid calls, and expected mmap/mprotect success or denial for each fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mdwe_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/memfd_secret.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/memfd_secret.c

## Purpose

`memfd_secret.c` tests the `memfd_secret` syscall and secretmem access restrictions. It verifies mlock accounting, disabled file I/O, blocked `vmsplice`, blocked `process_vm_readv`, and blocked ptrace reads.

## Important APIs, Types, and Functions

The file wraps `syscall(__NR_memfd_secret)` in `memfd_secret()`. It uses `mmap(MAP_SHARED)`, `ftruncate()`, `RLIMIT_MEMLOCK`, libcap `cap_set_proc()` to drop capabilities, `vmsplice()`, `process_vm_readv()`, `ptrace(PTRACE_ATTACH/PTRACE_PEEKDATA)`, pipes, and fork. Core test functions are `test_mlock_limit()`, `test_file_apis()`, `test_vmsplice()`, `test_process_vm_read()`, and `test_ptrace()`.

## Control Flow

`prepare()` captures page size and memlock limits, raises too-small limits to at least a page for test calculations, and drops capabilities with a bounded `RLIMIT_MEMLOCK`. `main()` creates a secret memfd, truncates it to one page, then runs six tests. Remote-access tests fork a child, pass the parent's mapped secret address through a pipe, and consider failure, skip, or signal termination as evidence that remote reads were blocked.

## State and Persistence Behavior

The secret fd and mappings are transient. The process modifies its own rlimit and drops capabilities, which persists for the remainder of the process. Pipes coordinate parent-child timing. Secret memory contents are filled with `PATTERN` to make unintended reads meaningful.

## Dependencies and Integration Points

It depends on `__NR_memfd_secret`, secretmem kernel support, `sys/capability.h`, and kselftest. It integrates with GUP-fast, pipe splice, ptrace, cross-process memory APIs, and memlock enforcement.

## Risks and Edge Cases

When `__NR_memfd_secret` is not defined or returns `ENOSYS`, the test skips. Some remote-access failures are intentionally broad because the child may exit with pass or be signaled. `test_mlock_limit()` assumes mapping twice the hard memlock limit fails after capability dropping.

## Test Signals

There are six planned checks: mlock limit respected, file I/O blocked, `vmsplice` blocked on a fresh page, `vmsplice` blocked on an existing page, `process_vm_readv` blocked or skipped if unsupported, and ptrace blocked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/memfd_secret.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/memory-failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/memory-failure.c

## Purpose

`memory-failure.c` is a kselftest harness suite for memory poisoning behavior. It injects hard and soft memory failures into anonymous, clean page-cache, and dirty page-cache pages and validates signals, page replacement, hardware-corrupted accounting, and kpageflags state.

## Important APIs, Types, and Functions

`enum inject_type` selects `MADV_HWPOISON` or `MADV_SOFT_OFFLINE`; `enum result_type` captures expected outcomes by mapping type. The fixture stores page size, original PFN, original `HardwareCorrupted` size, pagemap and kpageflags fds, and a trigger flag. Helpers include `madv_hard_inject()`, `madv_soft_inject()`, `sigbus_action()`, `prepare()`, `check_memory()`, `check()`, `cleanup()`, `prepare_file()`, and `get_fs_type()`.

## Control Flow

Fixture setup installs a SIGBUS handler and opens `/proc/self/pagemap` and `/proc/kpageflags`. Each test maps and initializes one page, records its PFN and current corruption accounting, injects poison once, then forces a read. Hard poisoned anonymous and dirty page-cache pages are expected to raise `SIGBUS` and leave a swapped/hwpoison entry. Soft-offlined anonymous and page-cache cases, plus hard clean page-cache, are expected not to signal and to preserve contents while changing PFN. Cleanup unpoisons the original PFN and checks the hardware-poison flag and accounting are restored.

## State and Persistence Behavior

The test directly changes kernel hardware-poison state for a PFN and relies on `unpoison_memory()` to clear it. It creates and unlinks temporary page-cache test files. It also reads global `/proc` accounting, so concurrent memory-failure activity can affect assertions.

## Dependencies and Integration Points

It depends on `vm_util.h` helpers for PFN, flags, corruption size, and unpoisoning, plus permission to read pagemap/kpageflags and use poison madvise operations. Page-cache tests skip unsupported filesystems such as tmpfs.

## Risks and Edge Cases

This is high-privilege and kernel-stateful. Failure before cleanup can leave a poisoned page until external recovery. The test excludes tmpfs page-cache cases because semantics differ. It assumes exact `HardwareCorrupted` growth by `page_size / 1024`, so system-wide noise can break it.

## Test Signals

Success requires correct SIGBUS metadata for hard failures, unchanged data and PFN replacement for recoverable cases, `KPF_HWPOISON` set after injection, and cleared poison plus restored accounting after cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/memory-failure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/merge.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/merge.c

## Purpose

`merge.c` is a broad VMA merge regression suite. It validates when adjacent VMAs should merge or remain separate across `mprotect()`, `mremap()`, `MREMAP_DONTUNMAP`, forked anonymous-vma state, KSM process-wide merge flags, uprobes, and `mseal()`.

## Important APIs, Types, and Functions

The test uses kselftest harness fixtures, `mmap()`, `mprotect()`, `munmap()`, `mremap()`, `prctl(PR_SET_MEMORY_MERGE)`, `perf_event_open()` for uprobes, `sys_mseal()`, and `procmap` query helpers from `vm_util.h`. `map_carveout()` reserves a 30-page `PROT_NONE` arena. `do_fork()` forks and reopens the procmap fd in the child. Fixtures `merge` and `merge_with_fork` share page size, carveout, and procmap state.

## Control Flow

The early tests create page-aligned carveout subregions, use `mprotect()` to split VMAs into RO/RW regions, fault selected subranges to attach anonymous VMA state, then change protections back and assert a single merged VMA via `find_vma_procmap()`. Fork tests ensure forked anonymous-vma chains inhibit unsafe merging. The uprobe test creates a file-backed executable mapping with a perf uprobe and moves subranges with `mremap()` to exercise merged executable VMA metadata. KSM tests toggle `PR_SET_MEMORY_MERGE` and verify newly adjacent anonymous mappings still merge. The mremap series moves unfaulted/faulted chunks around and checks merge boundaries. The `merge_with_fork` variants compare forked versus unforked results for `MREMAP_DONTUNMAP` moves into adjacent unfaulted/faulted regions.

## State and Persistence Behavior

All mappings live inside per-test carveout regions and are cleaned by fixture teardown. Some tests fork and only the child performs VMA assertions. `PR_SET_MEMORY_MERGE` is cleared unconditionally in teardown. The uprobe test creates and removes `./foo`. `mseal()` tests intentionally create sealed VMAs that cannot be unmapped individually, so they use a separate carveout and avoid normal teardown expectations for that mapping.

## Dependencies and Integration Points

It depends on `PROCMAP_QUERY` helpers, KSM prctl support, `__NR_mseal` where available, perf uprobe support under `/sys/bus/event_source/devices/uprobe/type`, and kernel VMA merge internals. It is tightly integrated with mm regressions around `anon_vma`, `vm_pgoff`, merge eligibility, sealed mappings, and multi-process VMA lineage.

## Risks and Edge Cases

The suite encodes precise expected VMA boundaries; small kernel semantic changes in merge eligibility can flip assertions. Forked tests use parent-return/child-continue control flow through `do_fork()`. Uprobe setup may skip if sysfs support is absent. Sealed VMA tests cannot always clean mappings after success. The fixture comments note that close of procmap may fail in parent after fork.

## Test Signals

Primary signals are procmap start/end assertions after each operation. Negative signals are expected non-merges for forked or incompatible VMAs. Skip signals cover absent KSM process merge support, missing uprobe event source, or missing `mseal`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/merge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/migration.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/migration.c

## Purpose

`migration.c` stress-tests page migration entries by moving pages between NUMA nodes while other threads or processes continuously access the same memory. It covers private/shared anonymous pages, THPs, and hugetlb pages.

## Important APIs, Types, and Functions

The fixture records worker thread/process arrays, available task CPUs, and two NUMA nodes. `migrate()` loops for `RUNTIME` seconds calling `move_pages(..., MPOL_MF_MOVE_ALL)` and alternates target nodes. `access_mem()` repeatedly performs a forced read and cancellation point. Test cases use `pthread_create()`, `fork()`, `prctl(PR_SET_PDEATHSIG)`, `madvise(MADV_HUGEPAGE)`, and `MAP_HUGETLB`.

## Control Flow

Fixture setup locates at least two NUMA nodes and allocates worker arrays. Each test maps a 2 MiB region, initializes it, starts concurrent access from threads for private mappings or forked processes for shared mappings, runs `migrate()` between nodes, then cancels threads or kills child processes. THP tests align the address and request huge pages; hugetlb tests use `MAP_HUGETLB`.

## State and Persistence Behavior

State is transient mapped memory and live worker tasks. `move_pages()` changes physical NUMA placement of pages. Child processes use `PR_SET_PDEATHSIG` to reduce orphan risk. The mappings are not explicitly unmapped in each test body, relying on process teardown.

## Dependencies and Integration Points

It depends on libnuma, multiple NUMA nodes, sufficient CPUs, optional transparent hugepage support, and hugetlb reservations for hugetlb cases. It integrates with kernel migration entry wait paths at PTE and PMD levels.

## Risks and Edge Cases

Migration is best-effort; `migrate()` tolerates up to `MAX_RETRIES` positive failures before failing. Systems without enough NUMA nodes/threads skip. Hugetlb allocation failures are hard assertion failures. Long runtime and concurrent readers make this intentionally stress-oriented and timing-sensitive.

## Test Signals

Each case passes if repeated migration succeeds for the runtime while concurrent access continues without faulting or hanging. Harness timeouts are set to twice the migration runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/migration.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mkdirty.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mkdirty.c

## Purpose

`mkdirty.c` verifies that kernel paths which set PTE or PMD dirty bits in read-only VMAs do not accidentally make those mappings writable. It covers forced ptrace writes, THP paths, page migration, PTE-mapped THPs, and userfaultfd copy.

## Important APIs, Types, and Functions

The program uses `/proc/self/mem`, `/proc/self/pagemap`, `mprotect()`, `mbind(MPOL_MF_MOVE)`, THP helpers, `userfaultfd`, and signal-based SIGSEGV recovery. Key helpers are `do_test_write_sigsegv()`, `mmap_thp_range()`, `test_ptrace_write()`, `test_ptrace_write_thp()`, `test_page_migration()`, `test_page_migration_thp()`, `test_pte_mapped_thp()`, and `test_uffdio_copy()`.

## Control Flow

`main()` detects page and PMD sizes, opens `/proc` files, sets the plan dynamically, and runs scenarios that place or migrate dirty pages into read-only mappings. After each dirty-bit-producing operation, `do_test_write_sigsegv()` attempts a normal write, catches SIGSEGV via `sigsetjmp()`, and checks the byte did not change.

## State and Persistence Behavior

The test uses transient anonymous mappings, optional THPs, an open `/proc/self/mem` fd for forced writes, and an optional userfaultfd. Signal handler state is process-global during each write check and restored to default afterward.

## Dependencies and Integration Points

It depends on pagemap visibility, `/proc/self/mem` writes, THP availability for THP cases, `mbind()` migration support, and `__NR_userfaultfd` for the UFFD case. It integrates with dirty-bit propagation in GUP/FOLL_FORCE, migration, PMD split, and userfaultfd.

## Risks and Edge Cases

Many scenarios skip if THP population, migration, or userfaultfd setup is unavailable. The signal handler reports any non-SIGSEGV as a distinct failure. Forced writes through `/proc/self/mem` intentionally bypass VMA permissions for setup, so the final ordinary write is the actual permission oracle.

## Test Signals

Success is a SIGSEGV on ordinary write and unchanged memory after every setup path. Skip signals indicate unavailable THP, migration, or userfaultfd support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mkdirty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mlock-random-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mlock-random-test.c

## Purpose

`mlock-random-test.c` randomly exercises `mlock()` and `mlock2(MLOCK_ONFAULT)` on regions inside and outside a reduced `RLIMIT_MEMLOCK`. It validates both successful locking and failure without side effects.

## Important APIs, Types, and Functions

The file uses `setrlimit(RLIMIT_MEMLOCK)`, libcap `cap_set_proc()` to drop `CAP_IPC_LOCK`, `mlock()`, the local `mlock2_()` wrapper, `munlock()`, `/proc/self/status` `VmLck`, and `/proc/self/smaps` `MMUPageSize` through `seek_to_smaps_entry()`. Helpers are `set_cap_limits()`, `get_proc_locked_vm_size()`, `get_proc_page_size()`, `test_mlock_within_limit()`, and `test_mlock_outof_limit()`.

## Control Flow

`main()` drops privileges to a 256 KiB memlock limit, runs a 128 KiB within-limit allocation through 100 random lock ranges, unlocks and frees it, then runs a 384 KiB allocation where randomly chosen lock ranges always exceed the limit and must fail. The within-limit path checks final locked bytes are bounded by aligned allocation size plus a page. The out-of-limit path checks `VmLck` is unchanged after repeated failures.

## State and Persistence Behavior

The process permanently reduces its memlock rlimit and capabilities. Memory comes from `malloc()` and is unlocked/freed between tests. The test reads kernel accounting from `/proc/self/status` and `/proc/self/smaps`.

## Dependencies and Integration Points

It depends on libcap, `mlock2.h`, kselftest, and procfs. It integrates with memory locking accounting and on-fault locking paths.

## Risks and Edge Cases

Random seeds use `time(NULL)` in each test, which can repeat if calls happen in the same second. `mlock2_()` in the header maps syscall return values unusually by assigning `errno = ret`, so negative syscall error handling can be misleading. The test assumes no unrelated locked memory in the process.

## Test Signals

There are two planned results: all random in-limit locks succeed and leave bounded `VmLck`, while all out-of-limit random locks fail and leave `VmLck` unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mlock-random-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mlock2-tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mlock2-tests.c

## Purpose

`mlock2-tests.c` validates `mlock2()` and `mlockall()` lock-on-fault behavior using `/proc/self/maps` and `/proc/self/smaps` observations. It verifies immediate locking, on-fault locking, unlock cleanup, and VMA split/merge behavior.

## Important APIs, Types, and Functions

The file uses `mlock2_()`, `mlockall()`, `munlock()`, `munlockall()`, `mmap()`, `/proc/self/maps`, and `/proc/self/smaps`. Helpers include `get_vm_area()`, `is_vmflag_set()`, `get_value_for_name()`, `is_vma_lock_on_fault()`, `lock_check()`, `unlock_lock_check()`, `onfault_check()`, `unlock_onfault_check()`, and `test_vma_management()`.

## Control Flow

`main()` first probes `mlock2(MLOCK_ONFAULT)` on a three-page mapping and exits finished if the syscall is unavailable. It then runs 13 planned checks. Immediate lock mode should set the `lo` VmFlag and make RSS equal VMA size. On-fault mode should mark the VMA locked while only faulting one page. `munlockall()` cases clear both immediate and on-fault locks. VMA management locks three pages, unlocks the middle page to force VMA splitting, then unlocks the full range to verify merging.

## State and Persistence Behavior

The tests alter process memory-lock state and VMA attributes, then clean them with `munlock()`, `munlockall()`, and `munmap()`. Observed state is read from procfs. No persistent files are written.

## Dependencies and Integration Points

It depends on the local `mlock2.h` wrapper and procfs smaps parsing. It integrates with mm VMA flag handling, RSS accounting, and VMA split/merge behavior for locked ranges.

## Risks and Edge Cases

The plan count is 13 even though some helper tests emit multiple results; this matches the existing code but makes result counting sensitive to helper behavior. Procfs text parsing assumes stable labels such as `VmFlags:`, `Size:`, and `Rss:`. The header wrapper's errno handling is nonstandard.

## Test Signals

Success is indicated by `lo` VmFlag presence/absence, RSS equal or less than VMA size as appropriate, and expected maps boundaries after split and merge operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mlock2-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mlock2.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mlock2.h

## Purpose

`mlock2.h` provides small shared helpers for mlock selftests: a direct `mlock2` syscall wrapper and a `/proc/self/smaps` positioning helper.

## Important APIs, Types, and Functions

`mlock2_()` calls `syscall(__NR_mlock2, start, len, flags)` and returns 0 or -1. `seek_to_smaps_entry()` opens `/proc/self/smaps`, scans VMA header lines, and returns a `FILE *` positioned at the entry containing the requested address.

## Control Flow

The wrapper performs one syscall and maps any nonzero return to `-1`. The smaps helper loops through lines, parses start/end/perms/offset/dev/inode/path fields, and stops once `start <= addr < end`; the caller continues reading subsequent lines for attributes.

## State and Persistence Behavior

The only persistent state is the returned open `FILE *`, which callers must close. The function frees temporary line storage and closes the file when no matching entry is found.

## Dependencies and Integration Points

The header assumes inclusion from kselftest files that provide `ksft_exit_fail_msg()` and standard headers for `size_t`/`strerror()`. It is included by `mlock-random-test.c` and `mlock2-tests.c`.

## Risks and Edge Cases

`mlock2_()` assigns `errno = ret`, but Linux syscall failure returns `-1` and sets errno through libc `syscall()`, so this code can overwrite errno with `-1`. `seek_to_smaps_entry()` has permissive parsing and a fixed `path` buffer, but it only needs address ranges. Returning a file positioned after the header is intentional.

## Test Signals

This header has no standalone tests. Its signals are the correctness of mlock syscall behavior and smaps parsing in the two including tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mlock2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mrelease_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mrelease_test.c

## Purpose

`mrelease_test.c` tests `process_mrelease()` on a killed child process and validates negative cases for bad pidfds, invalid flags, and live processes without pending `SIGKILL`.

## Important APIs, Types, and Functions

The file uses `pidfd_open`, `process_mrelease`, `kill(SIGKILL)`, `waitpid()`, pipes, `mmap()`, and `psize()` from `vm_util.h`. Helpers are `alloc_noexit()`, `run_negative_tests()`, and `child_main()`.

## Control Flow

`main()` first checks `process_mrelease(-1, 0)` returns `EBADF` or skips on `ENOSYS`. It forks a child that allocates and faults a configurable amount of memory, signals readiness through a pipe, and waits to be killed. The parent obtains a pidfd, runs negative tests while the child is alive, sends `SIGKILL`, calls `process_mrelease(pidfd, 0)`, waits for the child, and retries with doubled memory if the child exited too quickly and `ESRCH` was returned.

## State and Persistence Behavior

Child memory is anonymous and transient. The parent creates pidfds and pipes and closes them after each attempt. The retry loop increases child allocation from 1 MiB up to 1024 MiB to widen the window for successful release.

## Dependencies and Integration Points

It depends on `__NR_process_mrelease`, `__NR_pidfd_open`, Linux pidfd semantics, and mm process teardown. It integrates with userspace OOM-killer style memory reaping.

## Risks and Edge Cases

The positive case is inherently racy because `process_mrelease()` must run after `SIGKILL` but before the process fully exits. The retry logic handles `ESRCH` only; other failures are fatal. Memory allocation can grow to 1 GiB, which may be expensive on constrained systems.

## Test Signals

Success is one planned pass result reporting the allocation size at which child memory was reaped. Skips occur when the syscall is not implemented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mrelease_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mremap_dontunmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mremap_dontunmap.c

## Purpose

`mremap_dontunmap.c` validates `MREMAP_DONTUNMAP`: page tables move to a destination while the source virtual range remains mapped and faults back to zero pages or, for shmem, still observes backing contents.

## Important APIs, Types, and Functions

The program uses `mremap(MREMAP_DONTUNMAP | MREMAP_MAYMOVE)`, `MREMAP_FIXED`, `memfd_create()`, `ftruncate()`, `mmap()`, and `munmap()`. Helpers are `kernel_support_for_mremap_dontunmap()`, `check_region_contains_byte()`, `mremap_dontunmap_simple()`, `mremap_dontunmap_simple_shmem()`, `mremap_dontunmap_simple_fixed()`, `mremap_dontunmap_partial_mapping()`, and `mremap_dontunmap_partial_mapping_overwrite()`.

## Control Flow

`main()` probes support using a one-page `PROT_NONE` move and exits finished if unsupported. It allocates a page-sized comparison buffer, then runs five cases: simple anonymous move, shared memfd move, fixed-destination overwrite, partial source-range move, and fixed partial overwrite into the beginning of a larger destination.

## State and Persistence Behavior

Mappings are transient. Anonymous source PTEs are expected to be removed after move, causing zero-filled faults on source reads. Shared memfd source still reads original contents because the backing object remains. The global `page_buffer` is used for page-by-page memcmp expectations.

## Dependencies and Integration Points

It depends on `MREMAP_DONTUNMAP`, `memfd_create`, and Linux mm remap behavior. It integrates with page-table movement, fixed remap overwrite semantics, anonymous faulting, and shmem backing behavior.

## Risks and Edge Cases

The shmem case silently returns without a pass result if an older kernel rejects shared `MREMAP_DONTUNMAP` with `EINVAL`, even though the plan is fixed at five. Pointer arithmetic on `void *` relies on GNU extensions. Failure paths dump process maps.

## Test Signals

Success requires destination bytes matching moved source data, anonymous source ranges reading as zero after PTE removal, shmem source retaining data, and untouched destination tail bytes surviving fixed partial overwrite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mremap_dontunmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mremap_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mremap_test.c

## Purpose

`mremap_test.c` is a comprehensive `mremap()` functional and performance selftest. It validates alignment constraints, large-region remaps at PTE/PMD/PUD granularities, data preservation, VMA merge behavior, multi-VMA moves, `MREMAP_DONTUNMAP`, userfaultfd-invalid multi-move handling, and optional 1 GiB performance comparisons.

## Important APIs, Types, and Functions

`struct config` captures source alignment, destination alignment, region size, overlap, and destination preamble size. `struct test` adds a name and expected failure. Core helpers are `get_sqrt()`, `is_remap_region_valid()`, `get_mmap_min_addr()`, `is_range_mapped()`, `get_source_mapping()`, `remap_region()`, and `run_mremap_test_case()`. Scenario helpers include `mremap_expand_merge()`, `mremap_expand_merge_offset()`, `mremap_move_within_range()`, `mremap_move_multiple_vmas()`, `mremap_shrink_multiple_vmas()`, `mremap_move_multiple_vmas_split()`, `mremap_move_multi_invalid_vmas()`, and `mremap_move_1mb_from_start()`.

## Control Flow

`main()` parses validation threshold and random seed, precomputes a random byte buffer, builds 15 functional cases and three optional 1 GiB performance cases, and sets the plan to include alignment tests, merge tests, and miscellaneous multi-VMA tests. Each normal test maps a source at a requested non-coincidental alignment, copies a validation pattern, chooses a destination that avoids existing mappings unless overlap is expected, optionally maps a preamble before the destination, times `mremap(MREMAP_MAYMOVE | MREMAP_FIXED)`, verifies moved bytes and preamble bytes, and cleans mappings. Misc tests use `/proc/self/maps` to assert merge or movement behavior across gaps and invalid UFFD-registered VMAs.

## State and Persistence Behavior

All state is anonymous process mappings and an optional userfaultfd. The test reads `/proc/sys/vm/mmap_min_addr` to avoid forbidden low addresses and `/proc/self/maps` for mapping validation. It uses deterministic random data derived from the printed seed.

## Dependencies and Integration Points

It depends on Linux `mremap`, `MAP_FIXED_NOREPLACE`, procfs, and optional `userfaultfd`. It integrates with page table move optimizations, VMA merge logic, destination overwrite semantics, multi-VMA remapping, and data-integrity validation.

## Risks and Edge Cases

The test can map very large virtual ranges up to 2 GiB and optionally validate 1 GiB moves fully when `-t 0` is used. Address search can be slow or fail in crowded address spaces. Some code contains duplicated `goto error` and duplicated comments, but behavior remains clear. UFFD tests skip or partially validate based on permission and syscall support.

## Test Signals

Pass signals include expected xfail for overlapping or misaligned cases, successful data preservation for aligned cases, single-VMA merge after expansion, non-corruption of adjacent ranges, successful multi-VMA move/shrink/split operations, and correct `EFAULT` plus partial movement behavior for UFFD-invalid multi-VMA moves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mremap_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mseal_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mseal_helpers.h

## Purpose

`mseal_helpers.h` provides assertion/reporting macros and fallback pkey constants for `mseal_test.c`.

## Important APIs, Types, and Functions

`FAIL_TEST_IF_FALSE()` emits a failing kselftest result with function and line number, then returns from the current void test function. `SKIP_TEST_IF_FALSE()` emits a skip result and returns. `REPORT_TEST_PASS()` emits a pass result using the current function name. The header defines fallback `PKEY_DISABLE_ACCESS`, `PKEY_DISABLE_WRITE`, `PKEY_BITS_PER_PKEY`, `PKEY_MASK`, and `u64`.

## Control Flow

The macros are designed for single test functions that should stop on the first failed precondition or assertion. They do not abort the whole process, allowing the large mseal suite to continue after individual test failures.

## State and Persistence Behavior

The header has no state. It relies on kselftest global counters manipulated by `ksft_test_result_*()`.

## Dependencies and Integration Points

It assumes inclusion after `kselftest.h` and is used by `mseal_test.c`. The pkey constants support architectures or libc headers that do not provide the names used in the test.

## Risks and Edge Cases

The macros return without cleanup, so test functions that allocate mappings before a failure may leak VMAs until process exit. `u64` is conditionally defined as `unsigned long long`, which could conflict if included after another incompatible typedef.

## Test Signals

Signals are the pass, fail, or skip kselftest result lines emitted by the macros in `mseal_test.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mseal_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mseal_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mseal_test.c

## Purpose

`mseal_test.c` is a large functional test suite for the `mseal` syscall. It verifies that sealed VMAs resist destructive or permission-changing operations while nonsealed controls still behave normally. It covers sealing ranges across VMA boundaries, invalid inputs, `mprotect`, `munmap`, `mremap`, fixed `mmap`, `madvise`, pkeys, and merge/split behavior.

## Important APIs, Types, and Functions

The file uses direct syscall wrappers for `mseal`, `mprotect`, `pkey_mprotect`, `munmap`, `madvise`, `mremap`, and `pkey_alloc`. It has pkey register helpers for x86 PKRU (`__read_pkey_reg()`, `__write_pkey_reg()`, `set_pkey_bits()`, `set_pkey()`). Mapping helpers include `get_vma_size()`, `setup_single_address()`, `setup_single_address_rw()`, `clean_single_address()`, `seal_single_address()`, `seal_support()`, and `pkey_supported()`.

## Control Flow

`main()` probes sealing support, prints pkey availability, sets a plan of 88, and runs paired control/sealed versions for most operations. Initial tests cover adding seals, unmapped start/middle/end ranges, multiple VMAs, split-at-start/end, invalid flags, unaligned addresses, overflow, zero length, duplicate sealing, and address zero. `mprotect` tests check full, partial, unaligned-length, cross-VMA, gap, merge, and split cases. `munmap` tests cover full ranges, multiple VMAs, gaps, partial sealed tails, and already-freed start/middle/end regions. `mremap` tests cover shrink, expand, move, fixed move, fixed zero address, and `MREMAP_DONTUNMAP`. `mmap` tests cover fixed overwrite, expansion, and shrink. `madvise` tests distinguish discard-like operations on sealed read-only anonymous memory from nondiscard advice and from RW, pkey-writable, shared, or file-backed mappings. `test_seal_merge_and_split()` performs detailed VMA size checks after repeated seal splits and merges.

## State and Persistence Behavior

The suite creates many anonymous and memfd-backed mappings. Sealed mappings intentionally cannot be unmapped by normal cleanup, so failures can leave VMAs until process exit. Pkey tests allocate protection keys and modify PKRU state. The zero-address test maps address 0 with `MAP_FIXED`, seals it, and verifies protection changes fail.

## Dependencies and Integration Points

It depends on `__NR_mseal`, 64-bit kernel support, `mseal_helpers.h`, kselftest, optional x86 pkeys, `memfd_create`, and `/proc/self/maps` parsing. It integrates with core mm VMA mutation paths: permission changes, unmapping, remapping, fixed mapping replacement, advice that discards contents, VMA merge/split logic, and pkey write permission evaluation.

## Risks and Edge Cases

The test uses direct syscalls and void-pointer arithmetic under GNU C. Some test names are invoked twice, and one duplicate function signature appears in the source around `test_seal_mmap_overwrite_prot`, which should be watched in builds. Macro-based early returns can skip cleanup. The fixed zero mapping can be blocked by low-address policy on some systems. Pkey behavior is architecture- and CPU-dependent and skipped if unsupported.

## Test Signals

Success requires sealed ranges to reject `mprotect`, `munmap`, destructive `mremap`, fixed overwrite/resize `mmap`, and discard-style `madvise` where applicable, usually with `EPERM`; unsealed controls must succeed. VMA size/protection checks from `/proc/self/maps` verify split and merge outcomes. Pkey tests verify discard denial depends on effective write permission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mseal_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/on-fault-limit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/on-fault-limit.c

## Purpose

`on-fault-limit.c` verifies that `mlockall(MCL_ONFAULT | MCL_FUTURE)` still respects the process memlock limit when a future `MAP_POPULATE` mapping would fault and lock more memory than allowed.

## Important APIs, Types, and Functions

The test uses `getrlimit(RLIMIT_MEMLOCK)`, `mlockall()`, `mmap(MAP_POPULATE)`, `munmap()`, `munlockall()`, and kselftest helpers. `test_limit()` contains the single behavior check.

## Control Flow

`main()` sets a one-test plan. Root is skipped because privileged locking can bypass the intended limit. Non-root runs `test_limit()`, which enables future on-fault locking and attempts to map twice the hard memlock limit with populate. The expected result is `MAP_FAILED`.

## State and Persistence Behavior

The test sets process-wide mlockall state and clears it with `munlockall()`. If the mapping unexpectedly succeeds, it is unmapped.

## Dependencies and Integration Points

It depends on normal-user execution and kernel support for `MCL_ONFAULT`. It integrates with memlock rlimit enforcement during populate faults.

## Risks and Edge Cases

If `rlim_max` is unlimited or extremely large, the requested mapping can be impractical or overflow size expectations. Running as root always skips. The test checks failure but not a specific `errno`.

## Test Signals

The single pass signal is that the populated mapping fails while future on-fault locking is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/on-fault-limit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/page_frag/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/page_frag/Makefile

## Purpose

This Makefile builds the `page_frag_test.ko` kernel module used to test page fragment cache behavior.

## Important APIs, Types, and Functions

It defines `PAGE_FRAG_TEST_DIR`, `KDIR`, verbosity variable `Q`, `MODULES = page_frag_test.ko`, and `obj-m += page_frag_test.o`. Targets are `all` and `clean`, both delegating to the kernel build system with `make -C $(KDIR) M=$(PAGE_FRAG_TEST_DIR)`.

## Control Flow

`all` builds external modules from the page_frag test directory. `clean` runs the kernel module clean target for the same directory. `KDIR` defaults to the kernel tree root relative to the selftests directory or to `$(O)` when an out-of-tree output directory is provided.

## State and Persistence Behavior

The Makefile creates kernel module build artifacts in the module directory or configured output tree and removes them on `clean`. It does not run the module.

## Dependencies and Integration Points

It depends on a configured kernel build tree and kbuild external module support. It integrates `page_frag_test.c` into the mm selftest build flow as a loadable module.

## Risks and Edge Cases

Incorrect `KDIR` or `O` settings cause build failures. Module build products are generated files outside the source logic. Verbosity is controlled by `V=1`.

## Test Signals

Successful `make` produces `page_frag_test.ko`; successful `clean` removes module artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/page_frag/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/page_frag/page_frag_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/page_frag/page_frag_test.c

## Purpose

`page_frag_test.c` is a loadable kernel test module for the page fragment cache. It stress-tests fragment allocation and freeing between producer and consumer kthreads, optionally validating cacheline alignment from `page_frag_alloc_align()`.

## Important APIs, Types, and Functions

The module uses `struct page_frag_cache`, `page_frag_cache_init()`, `page_frag_alloc()`, `page_frag_alloc_align()`, `page_frag_free()`, `page_frag_cache_drain()`, `struct ptr_ring`, `ptr_ring_init()`, `__ptr_ring_produce()`, `__ptr_ring_consume()`, kthreads, completions, atomics, CPU placement, and module parameters. Thread functions are `page_frag_push_thread()` and `page_frag_pop_thread()`. Entry and exit points are `page_frag_test_init()` and `page_frag_test_exit()`.

## Control Flow

On module load, parameters are validated, the fragment cache and pointer ring are initialized, producer and consumer kthreads are created on selected CPUs, and both are started. The producer allocates fragments until `nr_test` pushes succeed or `force_exit` is set; if `test_align` is enabled it checks returned addresses against `SMP_CACHE_BYTES`. The consumer removes objects from the ring and frees them until `nr_test` pops complete. The init function waits in 10-second intervals, detecting lack of progress and forcing exit. It logs duration on success, cleans the ring and fragment cache, and returns `-EAGAIN` so insertion completes the test but does not leave the module loaded.

## State and Persistence Behavior

Global module state includes the ring, fragment cache, counters, completion, force-exit flag, and module parameters (`nr_test`, `test_align`, `test_alloc_len`, `test_push_cpu`, `test_pop_cpu`). Fragments are allocated from kernel memory and freed by the consumer or immediately on ring-full producer failure. The cache is drained before exit.

## Dependencies and Integration Points

It depends on kernel module loading, active selected CPUs, `page_frag_cache` APIs, ptr_ring, scheduler/kthread support, and kbuild output from the page_frag Makefile. It integrates with mm/network-style page fragment allocation code paths.

## Risks and Edge Cases

Counters are plain `int` shared between kthreads, so this is a stress test rather than a strict data-race-free accounting example. Invalid CPU or allocation length parameters fail load with `-EINVAL`. If producer or consumer stalls, the wait loop sets `force_exit` and emits a warning. Returning `-EAGAIN` is intentional but may look like module insertion failure to generic tooling.

## Test Signals

Kernel log output is the primary signal: progress lines, duration on success, and warnings with `page_frag_test failed:` on alignment or progress failures. Successful completion drains resources and returns `-EAGAIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/page_frag/page_frag_test.c -->
