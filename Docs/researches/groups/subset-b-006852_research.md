# subset-b-006852 research

Grouped research for Linux MM selftests under `sources/distributed-fs/ceph-client/tools/testing/selftests/mm`. Each section is delimited for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/guard-regions.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/guard-regions.c

## Purpose
`guard-regions.c` is a kselftest harness for the `MADV_GUARD_INSTALL` and `MADV_GUARD_REMOVE` VM features. It validates that guard markers behave like inaccessible guard pages while still preserving expected VMA, page-cache, fork, mremap, procfs, pagemap, userfaultfd, and THP interactions. The fixture runs the same core tests against anonymous, shmem/memfd, and local-file-backed mappings.

## Important APIs, types, and functions
The harness uses `FIXTURE(guard_regions)` and variants keyed by `enum backing_type`. `mmap_()` centralizes creation of anonymous private mappings, shmem/shared memfd mappings, and local shared file mappings. Signal recovery is handled by `setup_sighandler()`, `handle_fatal()`, `try_access_buf()`, `try_read_buf()`, and `try_write_buf()`, which convert `SIGSEGV` into boolean access results via `sigsetjmp()`/`siglongjmp()`. File/data helpers include `open_file()`, `set_pattern()`, `check_pattern()`, `check_pattern_offset()`, `is_buf_eq()`, and `local_fs_has_sane_mmap()`. Integration helpers call raw `userfaultfd()`, `process_madvise()` via `sys_process_madvise()`, `/proc/self/pagemap`, `PAGEMAP_SCAN`, `procmap` helpers, `check_vmflag_guard()`, and THP utilities from `vm_util.h`/`thp_settings.h`.

## Control flow
Fixture setup detects page size, installs a `SIGSEGV` handler, creates/truncates a memfd or local temporary file when needed, and fixture teardown restores signals and closes/unlinks backing files. `basic` installs/removes guards at individual and ranged pages and verifies access semantics. `multi_vma` spans holes and incompatible VMAs, expecting `ENOMEM` for gaps but successful modification of mapped subranges. `process_madvise` batches guard operations over several iovecs using `PIDFD_SELF`, skipping when permissions are insufficient. Other tests cover `munmap`, `mprotect`, VMA split/merge, `MADV_DONTNEED`, `mlock`, move/expand/shrink `mremap`, fork inheritance, CoW and `MADV_WIPEONFORK`, `MADV_FREE`, populate/cold/pageout, userfaultfd registration, sequential readahead, `MAP_PRIVATE` file behavior, read-only files, fault-around, truncation, hole punching, memfd write seals, anonymous zero page mappings, pagemap bits, `PAGEMAP_SCAN`, `MADV_COLLAPSE`, and `smaps` VM flags.

## State and persistence behavior
The file deliberately mutates page table state, VMA layout, page cache contents, file length, file seals, and procfs-observable flags. Guard markers are expected to survive operations such as `mprotect`, `MADV_DONTNEED`, `MADV_FREE`, cold/pageout, many VMA splits/merges, and fork in non-wipe mappings. They are expected to disappear when the guarded range is unmapped or when `MADV_WIPEONFORK` creates a child mapping. File-backed sections validate persistence of underlying file data and isolation of shared versus private mappings.

## Dependencies and integration points
The test depends on Linux headers exposing `MADV_GUARD_INSTALL`, `MADV_GUARD_REMOVE`, `PM_GUARD_REGION`, `PAGE_IS_GUARD`, and `PAGEMAP_SCAN`, and on local selftest helpers in `kselftest_harness.h`, `vm_util.h`, `thp_settings.h`, and `../pidfd/pidfd.h`. Some paths require root or relaxed sysctls for `process_madvise()` and `userfaultfd()`. THP collapse coverage depends on transparent hugepage availability and file THP support for some file cases.

## Risks and edge cases
The suite is sensitive to filesystem mmap merge behavior; `local_fs_has_sane_mmap()` avoids asserting merge behavior on filesystems with unusual `.mmap` behavior. Permissions can cause skips for userfaultfd and process_madvise. Signal-based access probing must keep fatal accesses inside the guarded `sigsetjmp()` window. Tests that inspect `smaps`, pagemap, or THP state can be kernel-version and configuration dependent.

## Test signals
Passing signals include successful kselftest assertions that guarded pages fault, unguarded pages remain readable/writable, file data survives guard removal, procfs/pagemap expose guard state, `MADV_COLLAPSE` rejects guarded ranges, and VM flag behavior remains sticky but merge-compatible. Skips are expected for unsupported backing/feature combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/guard-regions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/gup_longterm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/gup_longterm.c

## Purpose
`gup_longterm.c` tests long-term `get_user_pages()`/`pin_user_pages()` behavior for file-backed mappings. It verifies which filesystems and mapping modes allow long-term read-only or writable pins, including fast-GUP variants and optionally `io_uring` fixed-buffer registration.

## Important APIs, types, and functions
The core type is `enum test_type`, covering read-only, read-only fast, read/write, read/write fast, and `io_uring` when `LOCAL_CONFIG_HAVE_LIBURING` is enabled. `get_fs_type()`, `fs_is_unknown()`, and `fs_supports_writable_longterm_pinning()` classify backing filesystems using `statfs` magic values. `do_test()` performs setup, mapping, fault-in, optional `mprotect(PROT_READ)`, and the relevant `PIN_LONGTERM_TEST_START`/`STOP` ioctl or `io_uring_register_buffers()` path. `run_with_memfd()`, `run_with_tmpfile()`, `run_with_local_tmpfile()`, and `run_with_memfd_hugetlb()` provide backing variants. `test_case` entries bind human descriptions to wrapper functions.

## Control flow
`main()` records base page size, detects supported hugetlb page sizes, opens `/sys/kernel/debug/gup_test`, sets a kselftest plan equal to test cases times backing variants, then iterates all test cases. Each run creates a file, truncates and fallocates it to the requested size, maps it shared or private, faults the pages in, and asks the kernel debugfs GUP test driver to pin the range. Return handling distinguishes unsupported ioctls, expected `EFAULT` on unsupported writable shared long-term pins, and failures where a pin should have worked.

## State and persistence behavior
The test creates transient memfds, tmpfiles, local unlinked files, and hugetlb memfds. It mutates file length, allocates blocks, faults mappings, and temporarily holds long-term pins until `PIN_LONGTERM_TEST_STOP`. It does not persist data beyond the lifetime of each file descriptor.

## Dependencies and integration points
This file integrates with the in-kernel `CONFIG_GUP_TEST` debugfs device at `/sys/kernel/debug/gup_test`, `mm/gup_test.h` UAPI structures, hugetlb page-size detection in `vm_util.h`, filesystem magic constants, and optional liburing. It relies on kernel rules that allow writable long-term shared pins only on special filesystems such as tmpfs and hugetlbfs.

## Risks and edge cases
Unknown filesystems are skipped for writable shared cases because expected behavior cannot be asserted safely. `fallocate()` failures can represent unsupported filesystems or insufficient huge pages. Running without debugfs, root, `CONFIG_GUP_TEST`, or enough hugetlb pages produces skips. The io_uring branch intentionally treats several errors as unsupported-resource skips.

## Test signals
Pass conditions are correct accept/reject behavior for each mapping/filesystem/type matrix, successful ioctl start/stop for supported cases, and expected failure for unsupported writable shared long-term pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/gup_longterm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/gup_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/gup_test.c

## Purpose
`gup_test.c` is a command-line kselftest client and benchmark driver for the kernel `gup_test` debugfs interface. It exercises GUP fast, PIN fast, long-term PIN benchmarks, basic GUP/PIN tests, and page dumping.

## Important APIs, types, and functions
The program uses `struct gup_test` and ioctl command constants from `<mm/gup_test.h>`. `cmd_to_str()` formats command names. `gup_thread()` runs one ioctl sequence and reports timing for benchmark commands or completion for functional commands. `main()` parses options such as command selection, size, repeat count, pages per call, thread count, THP hints, file path, shared/private mapping, hugetlb mapping, write flag, and dump-page indices.

## Control flow
`main()` opens the requested file, opens `/sys/kernel/debug/gup_test`, maps the configured size, optionally applies `MADV_HUGEPAGE` or `MADV_NOHUGEPAGE`, faults every base page in from userspace, then starts `nthreads` identical worker threads. Each worker copies the shared `struct gup_test`, sets the current size, runs the selected ioctl, prints timing or completion under `print_mutex`, and emits a kselftest result.

## State and persistence behavior
The file creates or opens a mapping source, modifies the mapped memory to fault pages in, and may create a shared or hugetlb mapping depending on flags. Kernel-side pin/get operations are delegated to the debugfs driver. No durable state is intentionally written except the optional file backing chosen by `-f`.

## Dependencies and integration points
The test requires debugfs mounted at `/sys/kernel/debug`, `CONFIG_GUP_TEST`, and sufficient permissions to open the debugfs node. It uses pthreads, kselftest, `vm_util` page-size helpers, mmap, madvise, and kernel ioctl definitions.

## Risks and edge cases
The default maps 128 MiB, so memory pressure and hugetlb availability can affect runs. Thread output is serialized, but all threads share the same `gup_fd`. The test skips rather than fails when the debugfs interface is unavailable. Some flags are passed through to kernel internals and may only be meaningful for specific ioctl commands.

## Test signals
Each thread produces a kselftest result from the ioctl status. Benchmark commands print get/put microsecond deltas and truncated sizes; functional commands print completion and optional truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/gup_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hmm-tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hmm-tests.c

## Purpose
`hmm-tests.c` is a large kselftest suite for Heterogeneous Memory Management using the `test_hmm` kernel module's private UAPI. It simulates device mirror reads, writes, snapshots, migrations, exclusive access, copy-on-write, hugepage behavior, GUP interaction, and migration benchmark paths for device-private and device-coherent memory.

## Important APIs, types, and functions
The central data structure is `struct hmm_buffer`, which carries a user virtual address, device mirror buffer, byte size, file descriptor, copied page count, and fault count. Two fixture families are used: `hmm` opens one `/dev/hmm_dmirrorN` device and `hmm2` opens two devices. Variants cover private-device and coherent-device modes. `hmm_open()` opens the test device, `hmm_is_coherent_type()` differentiates coherent units, and `hmm_dmirror_cmd()` wraps all `HMM_DMIRROR_*` ioctls. Helpers include `hmm_buffer_free()`, `hmm_create_file()`, `hmm_random()`, `hmm_nanosleep()`, `hmm_migrate_sys_to_dev()`, `hmm_migrate_dev_to_sys()`, `gup_test_exec()`, `hmm_buffer_alloc()`, `run_migration_benchmark()`, and `print_benchmark_results()`.

## Control flow
Fixture setup records page size/shift and opens the requested device, skipping coherent variants when unavailable. Basic tests read/write private anonymous memory, protected memory, shared anonymous memory, file-backed mappings, THP mappings, and hugetlb mappings. Fork tests verify private CoW versus shared propagation when a simulated device writes in a child process. Migration tests move anonymous memory to device memory, fault it back, release it, reject unsupported shared mappings, migrate mixed ranges across two devices, repeat migration cycles, and handle partial unmap/remap cases. Snapshot tests classify holes, zero pages, read-only pages, writable pages, local device pages, and remote device pages. Exclusive tests validate device-exclusive mappings and revocation after CPU faults or mprotect. Later tests integrate with `/sys/kernel/debug/gup_test`, exercise CoW in device pages, validate huge zero/empty/free/fault/error paths, and run a timeout-bounded THP migration benchmark across buffer sizes.

## State and persistence behavior
The suite creates anonymous, shared, hugetlb, and temporary file mappings; mutates memory contents; migrates pages between CPU and simulated device memory; changes VMA protections; forks children; and opens per-process mirror devices. Device migration state is persistent inside the kernel test driver until pages are faulted/released/migrated back or the mapping is destroyed. File-backed cases use unnamed temporary files under `/tmp`.

## Dependencies and integration points
The test depends on `/dev/hmm_dmirror*` nodes from the `test_hmm` module and private `<lib/test_hmm_uapi.h>` constants. It also integrates with `mm/gup_test.h`, `/sys/kernel/debug/gup_test`, hugepage utilities, THP page-size helpers, pthreads, fork/wait, `mremap`, and `madvise`. Device-coherent expectations differ from device-private expectations because CPU access may not fault coherent pages back automatically.

## Risks and edge cases
Many cases require specific kernel configuration, test module loading, device nodes, debugfs, hugetlb resources, and THP behavior. Race tests intentionally unmap memory while device reads are in progress. Hugepage and THP paths rely on alignment to `read_pmd_pagesize()`. The benchmark is performance-observational and prints results rather than asserting improvements. Child paths call `exit()` directly after fixture assertions, so failures propagate through wait status.

## Test signals
Passing tests confirm correct copied-page and fault counts, unchanged or changed memory according to private/shared semantics, expected ioctl errors such as `-EFAULT`, `-EPERM`, `-ENOENT`, or `-EINVAL`, correct snapshot protection flags, preserved data across migration/fault cycles, correct GUP-triggered migration back to system memory, and successful THP migration benchmark iterations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hmm-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugepage-mmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugepage-mmap.c

## Purpose
`hugepage-mmap.c` is a simple functional example and selftest for mapping 256 MiB of hugetlb memory through a `memfd_create(..., MFD_HUGETLB)` file descriptor, writing a byte pattern, and reading it back.

## Important APIs, types, and functions
The test uses `memfd_create`, `mmap(MAP_SHARED)`, `munmap`, `close`, and kselftest plan/result helpers. `write_bytes()` fills `LENGTH`, `read_bytes()` verifies the same modulo-char pattern, and `check_bytes()` prints the first word.

## Control flow
`main()` initializes a one-test plan, creates a hugetlb memfd, maps `LENGTH` with read/write protection, prints the address, writes the pattern, verifies it, unmaps, closes, and reports pass/fail.

## State and persistence behavior
State is limited to a temporary hugetlb memfd and its mapping. The file descriptor is closed at the end; no filesystem path persists.

## Dependencies and integration points
The test requires enough preallocated default hugetlb pages for 256 MiB and kernel support for hugetlb memfds. It integrates with kselftest but not `run_vmtests.sh` directly except as a hugetlb test binary.

## Risks and edge cases
Low hugepage availability causes `mmap()` failure. The byte pattern intentionally wraps via `char`, so verification depends on matching write/read interpretation rather than unique byte values.

## Test signals
The single kselftest result passes when all bytes read back match the generated pattern.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugepage-mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugepage-mremap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugepage-mremap.c

## Purpose
`hugepage-mremap.c` verifies remapping hugetlb memory with `mremap()`, including a fixed remap over a dummy mapping and interaction with userfaultfd registration. It targets PMD sharing/unshare paths when large sizes are requested.

## Important APIs, types, and functions
The file uses `memfd_create(MFD_HUGETLB)`, `mmap(MAP_HUGETLB | MAP_SHARED | MAP_POPULATE)`, `mremap(MREMAP_MAYMOVE | MREMAP_FIXED)`, `userfaultfd`, `UFFDIO_API`, and `uffd_register()`. Pattern helpers mirror `hugepage-mmap.c`. `register_region_with_uffd()` creates a userfaultfd object, creates and registers an anonymous mapping for missing-page tracking, and skips on permission or unsupported kernels.

## Control flow
`main()` parses an optional length in MiB, maps a hugetlb region at a suggested PUD-aligned address, maps a second dummy hugetlb region to encourage PMD sharing, maps an anonymous destination range, registers userfaultfd-related memory, remaps the original hugetlb mapping to the destination, writes and verifies data, unmaps it, then asserts that a later `mremap()` on the unmapped address fails.

## State and persistence behavior
The test creates transient hugetlb and anonymous mappings and a hugetlb memfd. It deliberately replaces the destination mapping with the remapped hugetlb mapping. No state persists after close/unmap.

## Dependencies and integration points
The test depends on hugetlb availability, userfaultfd permission/configuration, and local `vm_util.h` userfaultfd helpers. It is integrated as a hugetlb/mremap regression test in the MM selftest suite.

## Risks and edge cases
Suggested fixed addresses may not be honored if unavailable, and insufficient hugepages can fail early. The helper's `addr` parameter is overwritten by its own mmap, so userfaultfd registration is best understood as auxiliary coverage rather than registration of `haddr` itself. Userfaultfd restrictions commonly produce skips.

## Test signals
Pass signals are successful fixed remap, intact byte pattern after remap, and expected failure when remapping an already-unmapped region.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugepage-mremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugepage-shm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugepage-shm.c

## Purpose
`hugepage-shm.c` demonstrates and tests System V shared memory backed by hugetlb pages using `SHM_HUGETLB`.

## Important APIs, types, and functions
The program uses `shmget()`, `shmat()`, `shmdt()`, and `shmctl(IPC_RMID)` with a 256 MiB segment. It has no kselftest harness wrapper; failures use `perror()` and process exit codes.

## Control flow
`main()` creates a hugepage SysV segment with key `2`, attaches it, writes a deterministic byte pattern across the entire length, verifies every byte, detaches, marks the segment for removal, and exits success.

## State and persistence behavior
A SysV shared memory segment persists until `IPC_RMID`. Error paths attempt cleanup when attach or detach fails. System-wide shared memory limits (`shmmax`, `shmall`) and hugepage pool state determine whether allocation succeeds.

## Dependencies and integration points
Requires hugetlb pages and adequate SysV shared memory limits. It is an example-style selftest rather than a `kselftest.h`-planned test.

## Risks and edge cases
Hard-coded key `2` can conflict with existing IPC state. Large memory use and low `shmmax`/`shmall` commonly fail. Byte values wrap by design.

## Test signals
Success is completing the full write/verify loop and removing the segment without errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugepage-shm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugepage-vmemmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugepage-vmemmap.c

## Purpose
`hugepage-vmemmap.c` verifies that hugetlb pages expose correct compound head/tail flags through `/proc/kpageflags`, including when hugetlb vmemmap optimization is enabled.

## Important APIs, types, and functions
The test maps one default hugepage with `MAP_HUGETLB`, writes into it, translates a virtual address to a PFN using `/proc/self/pagemap` in `virt_to_pfn()`, and checks `/proc/kpageflags` in `check_page_flags()`. It expects the first base page to include `PAGE_COMPOUND_HEAD | PAGE_HUGE` and subsequent base pages to include `PAGE_COMPOUND_TAIL | PAGE_HUGE` without head flags.

## Control flow
`main()` determines base and huge page sizes, maps one anonymous private hugepage, writes bytes to trigger allocation, resolves the PFN, verifies head/tail flags for all base pages in the hugepage, unmaps with hugepage-aligned length, and exits.

## State and persistence behavior
Only a private anonymous hugepage mapping is allocated and released. The test reads procfs kernel accounting but does not mutate persistent sysctls.

## Dependencies and integration points
Requires enough default hugepages and permission to read `/proc/self/pagemap` and `/proc/kpageflags`, which may be restricted on hardened systems. It uses `vm_util.h` for page-size helpers.

## Risks and edge cases
PFN visibility may be masked for unprivileged users. Hugepage pool exhaustion fails `mmap()`. Kernel flag definitions must match the tested kernel.

## Test signals
Success is a valid PFN plus expected head flag on the first base page and tail flags on every subsequent base page.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugepage-vmemmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb-madvise.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb-madvise.c

## Purpose
`hugetlb-madvise.c` tests `MADV_DONTNEED` and `MADV_REMOVE` on anonymous and file-backed hugetlb mappings, with attention to alignment, invalid ranges, private versus shared mappings, and hugepage free-count accounting.

## Important APIs, types, and functions
The test uses `default_huge_page_size()`, `get_free_hugepages()`, `memfd_create(MFD_HUGETLB)`, `mmap(MAP_HUGETLB)`, `fallocate()`, `madvise()`, and `munmap()`. `validate_free_pages()` asserts exact free hugepage counts. `write_fault_pages()` and `read_fault_pages()` force allocation or read faults.

## Control flow
`main()` skips when fewer than 20 free hugepages are available, creates a hugetlb memfd, then runs a sequence: invalid start/end `MADV_DONTNEED` ranges, unaligned start and length alignment behavior, anonymous private `MADV_DONTNEED`, private file mapping behavior before and after CoW, shared file mapping behavior, `MADV_REMOVE` on shared mappings, and combined shared/private mappings of the same file.

## State and persistence behavior
The test allocates and frees hugetlb pages and uses exact free-page counts as the observable state. `MADV_DONTNEED` should free anonymous/private CoW hugepages but not file-backed reserved pages; `MADV_REMOVE` acts like hole punch and frees file pages. Comments document expected historical behavior where hole punching shared file pages also frees private mapping pages.

## Dependencies and integration points
Requires a configured hugetlb pool and kernel hugetlb memfd support. It depends on `vm_util.h` hugepage accounting helpers and kselftest skip codes.

## Risks and edge cases
Exact free-page assertions are fragile if other system activity consumes hugepages concurrently. Filesystem or kernel changes to historical private-page behavior would change expected counts. The test exits on first failed assertion using `exit(1)`.

## Test signals
Passing means every page-count transition matches the expected allocation/free model and invalid/unaligned `madvise()` calls fail or round as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb-madvise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb-read-hwpoison.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb-read-hwpoison.c

## Purpose
`hugetlb-read-hwpoison.c` is a HugeTLB read regression test that verifies ordinary reads and reads around `MADV_HWPOISON`ed subpages of a hugepage. It checks both sequential reads from the start and seeked reads that skip poisoned areas.

## Important APIs, types, and functions
The program defines `enum test_status`, status formatting, chunk pattern helpers `setup_filemap()` and `verify_chunk()`, read helpers `read_hugepage_filemap()` and `seek_read_hugepage_filemap()`, test bodies `test_hugetlb_read()` and `test_hugetlb_read_hwpoison()`, and `create_hugetlbfs_file()` using `memfd_create(MFD_HUGETLB)` plus `fstatfs(HUGETLBFS_MAGIC)`.

## Control flow
`main()` iterates write/read chunk sizes from half a base page through four base pages. For each chunk size it creates a fresh hugetlb memfd, runs the plain read regression, creates another file for a read that should stop after reaching a poisoned page, and creates another for a seeked read that starts past the poisoned subpage. Each test truncates, maps with `MAP_SHARED | MAP_POPULATE`, writes chunk patterns, optionally poisons a base page inside the hugepage, reads, validates content and byte counts, unmaps, truncates back to zero, and closes.

## State and persistence behavior
The test uses temporary hugetlb memfds, populates their page cache, injects hardware-poison state via `MADV_HWPOISON`, and then truncates files back to zero. Poisoning can have system-level side effects on the hugepage pool, so the test assumes a controlled selftest environment.

## Dependencies and integration points
Requires hugetlb memfd support, `MADV_HWPOISON` permission/configuration, and enough hugepages. It relies on standard `read()` behavior for hugetlbfs files around poisoned base pages.

## Risks and edge cases
`MADV_HWPOISON` can require privileges and may be disabled. Pattern validation is sensitive to chunk-size arithmetic. The test returns failure immediately on any `TEST_FAILED` result but treats mapping/setup failures as skipped until final create failure.

## Test signals
Pass conditions are exact total bytes read and byte pattern verification for plain, poisoned, and seek-past-poison read modes across all chunk sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb-read-hwpoison.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb-soft-offline.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb-soft-offline.c

## Purpose
`hugetlb-soft-offline.c` validates `MADV_SOFT_OFFLINE` behavior for HugeTLB pages with `/proc/sys/vm/enable_soft_offline` both enabled and disabled.

## Important APIs, types, and functions
`do_soft_offline()` creates a populated hugetlb mapping and calls `madvise(..., MADV_SOFT_OFFLINE)` on an address inside it. `set_enable_soft_offline()` writes the sysctl using `popen("echo ...")`. `read_nr_hugepages()` reads the relevant sysfs `nr_hugepages` file. `create_hugetlbfs_file()` creates and validates a hugetlb memfd. `test_soft_offline_common()` orchestrates one enabled/disabled case.

## Control flow
`main()` sets a two-test plan, runs the enabled case expecting successful soft offline and one fewer hugepage in `nr_hugepages`, then runs the disabled case expecting `EOPNOTSUPP` and unchanged hugepage count.

## State and persistence behavior
The test changes the global `enable_soft_offline` sysctl and observes persistent hugetlb pool count changes. It creates a temporary hugetlb memfd and resets its size to zero after each mapping. The code does not restore the sysctl to its original value, so callers must run it in a controlled environment.

## Dependencies and integration points
Requires root-like permission to write `/proc/sys/vm/enable_soft_offline`, hugetlb memfd support, and sysfs hugepage counters under `/sys/kernel/mm/hugepages/hugepages-<size>kB/`.

## Risks and edge cases
Global sysctl mutation is invasive. Exact hugepage count comparisons can be disturbed by concurrent hugepage activity. The test checks `errno` after `madvise()` and expects it to match the configured mode.

## Test signals
The two kselftest results pass when the enabled run reduces `nr_hugepages` by one and the disabled run preserves the count while returning the expected unsupported error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb-soft-offline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_dio.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_dio.c

## Purpose
`hugetlb_dio.c` checks for hugepage leaks after direct I/O writes that use a hugetlb page as the user buffer. It verifies that the DIO path unpins the hugetlb buffer after aligned and selected unaligned offset/length cases.

## Important APIs, types, and functions
`get_dio_alignment()` uses `statx(AT_EMPTY_PATH, STATX_DIOALIGN)` to discover direct-I/O alignment. `check_dio_alignment()` skips cases that would fail before exercising the kernel pin/unpin path. `run_dio_using_hugetlb()` allocates one hugetlb page, writes a selected slice to an `O_DIRECT` tmpfile, unmaps the hugepage, and compares free hugepage counts before and after.

## Control flow
`main()` skips without free hugepages, opens an anonymous tmpfile in `/tmp` with `O_DIRECT`, discovers DIO alignment, sets a four-test plan, and runs cases with page-aligned start/end, aligned start with unaligned end, unaligned start with aligned end, and both unaligned. Cases incompatible with DIO alignment are reported skipped.

## State and persistence behavior
The test temporarily consumes one hugepage per case and writes data to an unnamed temporary file. The observed persistent state is the free hugepage count, which should return to the pre-allocation value after `munmap()`.

## Dependencies and integration points
Requires hugetlb availability, a filesystem under `/tmp` supporting `O_TMPFILE` and `O_DIRECT`, `statx` DIO alignment reporting, and `vm_util.h` hugepage counters.

## Risks and edge cases
Direct-I/O alignment constraints can skip unaligned cases. Concurrent hugepage users can make free-count comparison noisy. Filesystems without `O_DIRECT` tmpfile support skip the whole test.

## Test signals
Each executed case passes when `free_hugepages_after_munmap == free_hugepages_before_allocation`, indicating no lingering DIO pin.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_dio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_fault_after_madv.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_fault_after_madv.c

## Purpose
`hugetlb_fault_after_madv.c` is a race regression test for faults against a hugetlb page while another thread repeatedly applies `MADV_DONTNEED`.

## Important APIs, types, and functions
Global state includes `huge_ptr`, `huge_page_size`, a `sigjmp_buf`, and `sigbus_triggered`. `signal_handler()` catches `SIGBUS`. `touch()` repeatedly writes to the hugepage with longjmp recovery, while `madv()` repeatedly calls `madvise(MADV_DONTNEED)`.

## Control flow
`main()` installs a SIGBUS handler, requires exactly one free hugepage, then loops up to 10,000 times. Each iteration maps one anonymous hugetlb page, starts the madvise and touch threads, waits for both, and unmaps. It reports one kselftest result asserting no SIGBUS occurred.

## State and persistence behavior
The test repeatedly allocates and releases the sole available hugepage while racing reservation/free and write faults. The required initial state is exactly one free hugepage.

## Dependencies and integration points
Depends on pthreads, signals, hugetlb support, and `vm_util.h` for hugepage size/free counts. It should be run in an isolated hugepage pool.

## Risks and edge cases
The exact-one-hugepage precondition is strict. Race reproducibility depends on scheduling. Signal handling is global and uses longjmp from the handler to keep the test alive.

## Test signals
The test passes if the entire stress loop completes without `SIGBUS`; any SIGBUS flips the final result to failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_fault_after_madv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_madv_vs_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_madv_vs_map.c

## Purpose
`hugetlb_madv_vs_map.c` tests a race between `MADV_DONTNEED`, writes to an allocated hugetlb page, and a concurrent attempt to map an extra hugetlb page when only one hugepage should be available.

## Important APIs, types, and functions
`touch()` writes repeatedly to the primary hugepage. `madv()` repeatedly discards it with `MADV_DONTNEED`. `map_extra()` repeatedly attempts a second `MAP_HUGETLB` mapping and returns the pointer if allocation succeeds.

## Control flow
`main()` requires exactly one free hugepage and a default hugepage size. It loops ten times, mapping the single hugepage, launching the three racing threads, joining them, failing immediately if `map_extra()` succeeded, and unmapping before the next iteration.

## State and persistence behavior
The single hugepage oscillates between used and reserved/free-like states due to `MADV_DONTNEED`, while the test verifies another mapping cannot steal it. No durable state remains beyond the hugepage pool count.

## Dependencies and integration points
Requires pthreads, hugetlb, and a controlled system with exactly one free hugepage. Uses `vm_util.h` for free count and page size.

## Risks and edge cases
The race is scheduler dependent and intentionally sensitive to hugepage reservation accounting. If other processes use hugepages, the test either skips or becomes unreliable.

## Test signals
Success is returning `KSFT_PASS` after all iterations with no successful extra mapping; any unexpected extra hugepage mapping is a failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_madv_vs_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_reparenting_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_reparenting_test.sh

## Purpose
`hugetlb_reparenting_test.sh` validates hugetlb cgroup accounting and reparenting behavior for cgroup v1 and optionally cgroup v2. It checks that charges remain visible on parent cgroups after child removal and disappear after deleting hugetlbfs files.

## Important APIs, types, and functions
The script defines `cleanup()`, `assert_with_retry()`, `assert_state()`, `setup()`, `get_machine_hugepage_size()`, and `write_hugetlbfs()`. It writes `/proc/sys/vm/nr_hugepages`, mounts cgroup and hugetlbfs filesystems when necessary, moves the current shell into test cgroups, and invokes `./write_to_hugetlbfs`.

## Control flow
After root check and environment detection, it saves the original hugepage count, identifies or mounts the cgroup root, and computes the machine hugepage size. It first tests charge/rmdir/uncharge on a temporary cgroup. For cgroup v1 it also tests parent plus child hugetlb usage, child removal reparenting, and uncharge on file deletion. Finally it tests child-only usage and reparenting in both cgroup modes.

## State and persistence behavior
The script mutates global hugepage pool size, cgroup hierarchy, cgroup membership, and `/mnt/huge` mount state. `cleanup()` removes files, unmounts hugetlbfs, removes cgroups, and restores the original `nr_hugepages`; a final block unmounts temporary cgroup roots.

## Dependencies and integration points
Requires root, cgroup hugetlb and memory controllers, mount permissions, hugetlbfs, `/proc/meminfo`, and the companion `write_to_hugetlbfs` binary. It reads either `usage_in_bytes` for v1 or `current` for v2.

## Risks and edge cases
The test is invasive and can disturb existing cgroup or hugepage configuration. Accounting updates are asynchronous enough to need retry/tolerance. Error cleanup is broad but relies on predictable paths such as `/mnt/huge`.

## Test signals
The script prints `ALL PASS` after every `assert_state` succeeds within tolerance and the original hugepage count is restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_reparenting_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/khugepaged.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/khugepaged.c

## Purpose
`khugepaged.c` is a comprehensive Transparent Huge Page collapse test harness. It compares background `khugepaged` collapse and explicit `MADV_COLLAPSE` across anonymous, file-backed, and shmem mappings, validating collapse eligibility, scan limits, swap/shared constraints, compound-page handling, fork behavior, and file page-cache interactions.

## Important APIs, types, and functions
The core abstraction is `struct mem_ops`, with setup/cleanup/fault/check implementations for anon, file, and shmem. `struct collapse_context` abstracts the collapse engine, either `khugepaged_collapse()` or `madvise_collapse()`. The file also tracks `struct file_info` for file/shmem backing and block-device readahead sysfs path. Helpers include THP settings save/restore via `thp_settings.h`, `get_finfo()`, `check_swap()`, `alloc_mapping()`, `fill_memory()`, `validate_memory()`, `madvise_collapse_retry()`, `alloc_hpage()`, and many `collapse_*` scenarios.

## Control flow
`main()` verifies THP availability, parses `<context>:<mem_type>` and optional anon mTHP order, computes page and PMD hugepage sizes, configures THP/khugepaged settings, and runs a matrix of scenario functions through selected contexts and memory types. Setup functions create fixed-address mappings at `BASE_ADDR`: anonymous mappings, read-only file mappings with page cache drop and disabled readahead, or shared memfd shmem mappings. Collapse functions either mark ranges `MADV_HUGEPAGE` and wait for khugepaged scans or temporarily disable THP and issue `MADV_COLLAPSE` directly.

## State and persistence behavior
The harness deliberately changes global THP and khugepaged sysfs settings, device queue readahead, `/proc/sys/vm/drop_caches`, temporary files, memfds, swap state, and mappings. It saves settings at start and restores them through `atexit()` and signal handlers. Test data uses a deterministic `0xdead0000 + page index` pattern to detect corruption after collapse, split, fork, swap, and remap operations.

## Dependencies and integration points
The file depends on `vm_util.h` and `thp_settings.h`, `/sys/kernel/mm/transparent_hugepage`, `/proc/self/smaps`, `/proc/sys/vm/drop_caches`, file THP support for read-only filesystem collapse, tmpfs `huge=advise` for shmem khugepaged cases, and optional swap for swap tests. File-backed tests require a directory argument and inspect block device sysfs.

## Risks and edge cases
The test runs at a fixed virtual address and can fail if unavailable. It mutates system-wide THP settings and page cache. Khugepaged tests rely on scan timing; `wait_for_scan()` uses a timeout based on `full_scans`. MADV_COLLAPSE can transiently return `EAGAIN`, so the helper retries once. Some scenarios skip tmpfs or non-applicable memory types where semantics differ.

## Test signals
Output is color-coded success/fail/skip and `exit_status` accumulates failures. Passing means collapse succeeds or fails exactly as expected, `check_huge_*()` observes the right PMD mapping count, and `validate_memory()` finds no corruption after every scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/khugepaged.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_compaction.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_compaction.sh

## Purpose
Wrapper entry point for the MM selftest `compaction` category.

## Important APIs, types, and functions
The script is `#!/bin/sh -e` and invokes `./run_vmtests.sh -t compaction`.

## Control flow
Shell startup enables exit-on-error. All behavior is delegated to `run_vmtests.sh`, whose compaction target runs the compaction test for unevictable-page compaction behavior.

## State and persistence behavior
No state is managed by the wrapper. Any sysctl, memory, or log state belongs to `run_vmtests.sh` and the invoked test binaries.

## Dependencies and integration points
Requires execution from the selftests/mm build directory with `run_vmtests.sh` available and executable.

## Risks and edge cases
Because `set -e` is active, any runner failure becomes the wrapper exit status. The wrapper has no argument forwarding or local skip handling.

## Test signals
The wrapper succeeds when `run_vmtests.sh -t compaction` succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_compaction.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_cow.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_cow.sh

## Purpose
Wrapper entry point for the MM selftest `cow` category.

## Important APIs, types, and functions
The entire script is a POSIX shell wrapper with `set -e` semantics through `#!/bin/sh -e`, calling `./run_vmtests.sh -t cow`.

## Control flow
Execution immediately delegates to the VM test runner's copy-on-write category.

## State and persistence behavior
No wrapper-owned state exists.

## Dependencies and integration points
Requires `run_vmtests.sh` and the COW test binaries/configuration it selects.

## Risks and edge cases
No local cleanup exists; failures or skips are governed by the underlying runner.

## Test signals
The wrapper's exit status mirrors the `cow` target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_cow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_gup_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_gup_test.sh

## Purpose
Wrapper entry point for the MM selftest `gup_test` category.

## Important APIs, types, and functions
The script uses `#!/bin/sh -e` and calls `./run_vmtests.sh -t gup_test`.

## Control flow
The runner target executes GUP fast/PIN fast benchmarks, page dump coverage, and `gup_longterm`.

## State and persistence behavior
The wrapper has none. Underlying tests may open `/sys/kernel/debug/gup_test`, map memory, and allocate hugetlb resources.

## Dependencies and integration points
Requires `run_vmtests.sh`, built GUP test binaries, debugfs, and `CONFIG_GUP_TEST` for full coverage.

## Risks and edge cases
Without debugfs or permissions the underlying category may skip. The wrapper does not pass through custom arguments.

## Test signals
Exit status follows `run_vmtests.sh -t gup_test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_gup_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_hmm.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_hmm.sh

## Purpose
Wrapper entry point for the MM selftest `hmm` category.

## Important APIs, types, and functions
The script is a four-line shell wrapper invoking `./run_vmtests.sh -t hmm`.

## Control flow
It delegates to the runner's HMM target, which includes the `hmm-tests` binary when the test module/devices are available.

## State and persistence behavior
No local state is changed by the wrapper.

## Dependencies and integration points
Requires `run_vmtests.sh`, HMM selftest binaries, and loaded `/dev/hmm_dmirror*` test devices for meaningful execution.

## Risks and edge cases
The wrapper cannot distinguish feature skips from failures; it reports the runner's status.

## Test signals
Success is the runner completing the HMM target successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_hmm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_hugetlb.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_hugetlb.sh

## Purpose
Wrapper entry point for the MM selftest `hugetlb` category.

## Important APIs, types, and functions
The script runs `./run_vmtests.sh -t hugetlb` under `#!/bin/sh -e`.

## Control flow
All hugetlb setup, hugepage allocation checks, and test selection are delegated to `run_vmtests.sh`.

## State and persistence behavior
The wrapper has no local state. The hugetlb target can mount filesystems, consume hugepages, and run accounting tests.

## Dependencies and integration points
Requires built hugetlb selftest binaries and a host configured with hugetlb support.

## Risks and edge cases
Many hugetlb tests need root or preallocated pages. Wrapper-level failure handling is only `set -e`.

## Test signals
Exit status is exactly the hugetlb target's exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_hugetlb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_hugevm.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_hugevm.sh

## Purpose
Wrapper entry point for the MM selftest `hugevm` category.

## Important APIs, types, and functions
The wrapper calls `./run_vmtests.sh -t hugevm`.

## Control flow
No local branching exists; execution is delegated to the VM test runner.

## State and persistence behavior
No wrapper-owned state.

## Dependencies and integration points
Requires the runner and huge virtual memory tests it selects.

## Risks and edge cases
Large virtual-memory tests may be environment-sensitive; the wrapper provides no guard beyond the runner.

## Test signals
Successful completion of `run_vmtests.sh -t hugevm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_hugevm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_ksm.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_ksm.sh

## Purpose
Wrapper entry point for the MM selftest `ksm` category.

## Important APIs, types, and functions
The script invokes `./run_vmtests.sh -t ksm` with shell exit-on-error.

## Control flow
Delegates to the runner, which handles KSM tests and sysfs setup.

## State and persistence behavior
No local state; underlying KSM tests may modify `/sys/kernel/mm/ksm` controls.

## Dependencies and integration points
Requires KSM kernel support, runner script, and built KSM test binaries.

## Risks and edge cases
KSM sysfs permission or disabled kernel support can lead to skips/failures in the delegated target.

## Test signals
Wrapper success means the `ksm` target returned success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_ksm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_ksm_numa.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_ksm_numa.sh

## Purpose
Wrapper entry point for the MM selftest `ksm_numa` category.

## Important APIs, types, and functions
The script calls `./run_vmtests.sh -t ksm_numa`.

## Control flow
Delegates to the runner's NUMA-aware KSM tests, including `ksm_tests -N` modes in the runner.

## State and persistence behavior
No wrapper-owned state; delegated tests can affect KSM sysfs state.

## Dependencies and integration points
Requires NUMA/KSM support for full coverage and the runner in the current directory.

## Risks and edge cases
On non-NUMA or restricted systems the underlying target may skip or fail.

## Test signals
The script passes when the `ksm_numa` target passes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_ksm_numa.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_madv_guard.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_madv_guard.sh

## Purpose
Wrapper entry point for the MM selftest `madv_guard` category.

## Important APIs, types, and functions
The wrapper executes `./run_vmtests.sh -t madv_guard`.

## Control flow
The runner's `madv_guard` target invokes the guard-region tests, including `guard-regions`.

## State and persistence behavior
No local state. Underlying tests create mappings, temporary files, memfds, and inspect procfs.

## Dependencies and integration points
Requires kernel support for guard-region madvise operations and the built `guard-regions` binary.

## Risks and edge cases
Feature availability, permissions for userfaultfd/process_madvise, and THP configuration affect delegated results.

## Test signals
Wrapper success mirrors the `madv_guard` runner target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_madv_guard.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_madv_populate.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_madv_populate.sh

## Purpose
Wrapper entry point for the MM selftest `madv_populate` category.

## Important APIs, types, and functions
The script uses `#!/bin/sh -e` and invokes `./run_vmtests.sh -t madv_populate`.

## Control flow
Delegates to runner-managed tests for `MADV_POPULATE_READ` and `MADV_POPULATE_WRITE` behavior.

## State and persistence behavior
The wrapper has no state; underlying tests control their mappings.

## Dependencies and integration points
Requires `run_vmtests.sh` and built populate selftest binaries.

## Risks and edge cases
Kernel support and memory pressure affect delegated results.

## Test signals
Exit status follows the `madv_populate` target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_madv_populate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mdwe.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mdwe.sh

## Purpose
Wrapper entry point for the MM selftest `mdwe` category.

## Important APIs, types, and functions
It calls `./run_vmtests.sh -t mdwe` under `sh -e`.

## Control flow
Delegates to Memory-Deny-Write-Execute tests selected by the runner.

## State and persistence behavior
No wrapper-owned state.

## Dependencies and integration points
Requires runner and MDWE-capable kernel/test binaries.

## Risks and edge cases
Architecture or kernel support may determine skips in the delegated target.

## Test signals
Successful wrapper exit means the `mdwe` target succeeded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mdwe.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_memfd_secret.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_memfd_secret.sh

## Purpose
Wrapper entry point for the MM selftest `memfd_secret` category.

## Important APIs, types, and functions
The script invokes `./run_vmtests.sh -t memfd_secret`.

## Control flow
All secret-memory test setup and execution is delegated.

## State and persistence behavior
The wrapper has no state. Underlying tests may create secretmem file descriptors and mappings.

## Dependencies and integration points
Requires kernel `memfd_secret` support and runner-managed binaries.

## Risks and edge cases
Feature absence should be represented by delegated skips or failures.

## Test signals
The wrapper passes when `run_vmtests.sh -t memfd_secret` passes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_memfd_secret.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_memory_failure.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_memory_failure.sh

## Purpose
Wrapper entry point for the MM selftest `memory-failure` category.

## Important APIs, types, and functions
The script calls `./run_vmtests.sh -t memory-failure`.

## Control flow
Delegates to memory-failure tests, which may inject or simulate hardware memory failure paths.

## State and persistence behavior
No local state. Delegated tests can affect poisoned-page state and require a controlled environment.

## Dependencies and integration points
Requires `run_vmtests.sh`, built memory-failure binary, and kernel support/permissions for memory-failure operations.

## Risks and edge cases
Hardware-poison or memory-failure tests are inherently invasive and permission-sensitive.

## Test signals
The wrapper status mirrors the `memory-failure` category.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_memory_failure.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_migration.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_migration.sh

## Purpose
Wrapper entry point for the MM selftest `migration` category.

## Important APIs, types, and functions
It delegates with `./run_vmtests.sh -t migration`.

## Control flow
No local logic beyond runner invocation.

## State and persistence behavior
No wrapper state; underlying migration tests may move pages across nodes or memory types.

## Dependencies and integration points
Requires runner and migration-related test binaries/configuration.

## Risks and edge cases
NUMA and memory-hotplug capabilities can influence delegated behavior.

## Test signals
Pass/fail follows the `migration` target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_migration.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mkdirty.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mkdirty.sh

## Purpose
Wrapper entry point for the MM selftest target named `mkdirty`.

## Important APIs, types, and functions
The script calls `./run_vmtests.sh -t mkdirty`; the filename uses `mkdirty`, while the runner target string is `mkdirty`.

## Control flow
Delegates directly to the runner's dirty-page marking test.

## State and persistence behavior
No local state.

## Dependencies and integration points
Requires the runner target spelling `mkdirty` and its built test binary.

## Risks and edge cases
The target-name mismatch between filename and runner argument is intentional in this file and should not be silently renamed without checking `run_vmtests.sh`.

## Test signals
Successful exit from `run_vmtests.sh -t mkdirty`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mkdirty.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mlock.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mlock.sh

## Purpose
Wrapper entry point for the MM selftest `mlock` category.

## Important APIs, types, and functions
Runs `./run_vmtests.sh -t mlock` using shell exit-on-error.

## Control flow
Delegates locked-memory test execution to the runner.

## State and persistence behavior
No wrapper-owned state.

## Dependencies and integration points
Requires runner and mlock-related test binaries; underlying tests may depend on `RLIMIT_MEMLOCK`.

## Risks and edge cases
Memory-lock limits and privileges affect delegated results.

## Test signals
The wrapper succeeds if the `mlock` target succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mlock.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mmap.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mmap.sh

## Purpose
Wrapper entry point for the MM selftest `mmap` category.

## Important APIs, types, and functions
The script invokes `./run_vmtests.sh -t mmap`.

## Control flow
Delegates mmap-related selftests to the runner.

## State and persistence behavior
No wrapper-owned state.

## Dependencies and integration points
Requires runner and mmap test binaries.

## Risks and edge cases
Underlying tests may depend on architecture, permissions, or vm sysctls.

## Test signals
Exit status mirrors the runner's `mmap` target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mmap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mremap.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mremap.sh

## Purpose
Wrapper entry point for the MM selftest `mremap` category.

## Important APIs, types, and functions
Runs `./run_vmtests.sh -t mremap`.

## Control flow
Delegates mremap regression tests to the runner.

## State and persistence behavior
No wrapper-owned state.

## Dependencies and integration points
Requires runner and mremap test binaries.

## Risks and edge cases
Address-space layout and feature availability can affect delegated tests.

## Test signals
Successful runner completion for `mremap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mremap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_page_frag.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_page_frag.sh

## Purpose
Wrapper entry point for the MM selftest `page_frag` category.

## Important APIs, types, and functions
The script calls `./run_vmtests.sh -t page_frag`.

## Control flow
Delegates page-fragment tests to the runner.

## State and persistence behavior
No local state.

## Dependencies and integration points
Requires runner and page-fragment selftest binary.

## Risks and edge cases
Kernel configuration may determine whether the delegated test exists or skips.

## Test signals
Pass/fail mirrors the `page_frag` target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_page_frag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_pagemap.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_pagemap.sh

## Purpose
Wrapper entry point for the MM selftest `pagemap` category.

## Important APIs, types, and functions
Invokes `./run_vmtests.sh -t pagemap`.

## Control flow
Delegates pagemap and procfs page-state tests to the runner.

## State and persistence behavior
No wrapper state.

## Dependencies and integration points
Requires pagemap-readable environment for full coverage and the runner's test binaries.

## Risks and edge cases
Unprivileged PFN masking or procfs restrictions can cause delegated skips/failures.

## Test signals
Success is the pagemap target returning success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_pagemap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_pfnmap.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_pfnmap.sh

## Purpose
Wrapper entry point for the MM selftest `pfnmap` category.

## Important APIs, types, and functions
The script delegates with `./run_vmtests.sh -t pfnmap`.

## Control flow
No local control flow beyond runner invocation.

## State and persistence behavior
No local state.

## Dependencies and integration points
Requires runner and PFNMAP test support.

## Risks and edge cases
PFN mapping tests may be architecture/configuration sensitive.

## Test signals
Exit status mirrors the `pfnmap` target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_pfnmap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_pkey.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_pkey.sh

## Purpose
Wrapper entry point for the MM selftest `pkey` category.

## Important APIs, types, and functions
The script runs `./run_vmtests.sh -t pkey`.

## Control flow
Delegates protection-key tests to the runner.

## State and persistence behavior
No wrapper-owned state.

## Dependencies and integration points
Requires architecture/kernel support for memory protection keys and the runner-managed binaries.

## Risks and edge cases
Unsupported architectures or disabled pkeys should be handled by the delegated target.

## Test signals
Successful `pkey` target completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_pkey.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_process_madv.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_process_madv.sh

## Purpose
Despite its filename, this wrapper invokes the runner's `mmap` category.

## Important APIs, types, and functions
The script is `#!/bin/sh -e` plus `./run_vmtests.sh -t mmap`.

## Control flow
It delegates to `run_vmtests.sh` exactly like `ksft_mmap.sh`; there is no local call to a `process_madv` target.

## State and persistence behavior
No wrapper-owned state.

## Dependencies and integration points
Requires the `mmap` runner target. If process-madvise tests are expected, this wrapper-to-target mapping should be checked against the broader selftest design.

## Risks and edge cases
The filename/target mismatch is the main maintenance risk. Automated systems may assume it runs process_madvise-specific coverage when it actually requests `mmap`.

## Test signals
Success follows `run_vmtests.sh -t mmap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_process_madv.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_process_mrelease.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_process_mrelease.sh

## Purpose
Wrapper entry point for the MM selftest `process_mrelease` category.

## Important APIs, types, and functions
It calls `./run_vmtests.sh -t process_mrelease`.

## Control flow
Delegates to the runner's `process_mrelease(2)` test.

## State and persistence behavior
No local state.

## Dependencies and integration points
Requires kernel support for `process_mrelease` and runner-managed test binary.

## Risks and edge cases
Process lifecycle and permission behavior are handled by the delegated target.

## Test signals
Success is the `process_mrelease` target returning success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_process_mrelease.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_rmap.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_rmap.sh

## Purpose
Wrapper entry point for the MM selftest `rmap` category.

## Important APIs, types, and functions
Runs `./run_vmtests.sh -t rmap`.

## Control flow
Delegates reverse-map tests to the runner.

## State and persistence behavior
No wrapper state.

## Dependencies and integration points
Requires runner and rmap test binaries/configuration.

## Risks and edge cases
Underlying tests may be kernel-config dependent.

## Test signals
The wrapper passes when the `rmap` target passes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_rmap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_soft_dirty.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_soft_dirty.sh

## Purpose
Wrapper entry point for the MM selftest `soft_dirty` category.

## Important APIs, types, and functions
The script invokes `./run_vmtests.sh -t soft_dirty`.

## Control flow
Delegates soft-dirty tracking tests to the runner.

## State and persistence behavior
No local state; delegated tests may write procfs clear_refs controls and inspect pagemap soft-dirty bits.

## Dependencies and integration points
Requires pagemap/soft-dirty kernel support and runner-managed binaries.

## Risks and edge cases
Procfs permissions and PFN/bit visibility affect delegated behavior.

## Test signals
Success follows the runner's `soft_dirty` target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_soft_dirty.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_thp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_thp.sh

## Purpose
Wrapper entry point for the MM selftest `thp` category.

## Important APIs, types, and functions
The wrapper calls `./run_vmtests.sh -t thp`.

## Control flow
Delegates transparent hugepage tests, including khugepaged-related binaries, to the runner.

## State and persistence behavior
No wrapper state; underlying tests may mutate THP sysfs settings and restore them.

## Dependencies and integration points
Requires THP-capable kernel and built THP selftests.

## Risks and edge cases
THP sysfs permissions, swap availability, and filesystem support affect the delegated target.

## Test signals
Wrapper status mirrors the `thp` target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_thp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_userfaultfd.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_userfaultfd.sh

## Purpose
Wrapper entry point for the MM selftest `userfaultfd` category.

## Important APIs, types, and functions
The script invokes `./run_vmtests.sh -t userfaultfd`.

## Control flow
Delegates unit and stress tests for userfaultfd anon, hugetlb, and shmem modes to the runner.

## State and persistence behavior
No wrapper state. Delegated tests create mappings and userfaultfd descriptors.

## Dependencies and integration points
Requires userfaultfd kernel support, permission/sysctl configuration, and runner-built binaries.

## Risks and edge cases
Userfaultfd is often restricted for unprivileged users, causing skips or failures in delegated tests.

## Test signals
Successful completion of the `userfaultfd` runner target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_userfaultfd.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_vma_merge.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_vma_merge.sh

## Purpose
Wrapper entry point for the MM selftest `vma_merge` category.

## Important APIs, types, and functions
The script calls `./run_vmtests.sh -t vma_merge`.

## Control flow
Delegates VMA merge regression tests to the runner.

## State and persistence behavior
No local state.

## Dependencies and integration points
Requires runner and merge test binary.

## Risks and edge cases
VMA layout and filesystem-specific mmap behavior can affect delegated tests.

## Test signals
Pass/fail follows the `vma_merge` target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_vma_merge.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_vmalloc.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_vmalloc.sh

## Purpose
Wrapper entry point for the MM selftest `vmalloc` category.

## Important APIs, types, and functions
The script invokes `./run_vmtests.sh -t vmalloc`.

## Control flow
Delegates vmalloc smoke testing to the runner, which runs `test_vmalloc.sh smoke` for this category.

## State and persistence behavior
No wrapper state; delegated tests exercise kernel vmalloc behavior.

## Dependencies and integration points
Requires runner and vmalloc test script/binaries.

## Risks and edge cases
Kernel module/configuration requirements belong to the underlying vmalloc tests.

## Test signals
The wrapper passes when the `vmalloc` category passes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_vmalloc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksm_functional_tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksm_functional_tests.c

## Purpose
`ksm_functional_tests.c` validates Kernel Samepage Merging behavior around merging, unmerging, zero pages, discarded PTEs, userfaultfd write protection, process-wide PRCTL controls, fork/exec inheritance, protected mappings, and per-process merge accounting.

## Important APIs, types, and functions
The file uses KSM helpers from `vm_util.h`, `/sys/kernel/mm/ksm` controls, `/proc/self/mem`, `/proc/self/pagemap`, `prctl(PR_SET_MEMORY_MERGE/PR_GET_MEMORY_MERGE)`, `madvise(MADV_MERGEABLE/MADV_UNMERGEABLE/MADV_DONTNEED/MADV_NOHUGEPAGE)`, and optional userfaultfd write-protect ioctls. `range_maps_duplicates()` compares PFNs to infer sharing. `__mmap_and_merge_range()` and `mmap_and_merge_range()` build mergeable ranges under a selected `enum ksm_merge_mode`.

## Control flow
`main()` handles a fork/exec child mode, sets a kselftest plan, initializes global file handles, then runs tests. `test_unmerge`, `test_unmerge_zero_pages`, and `test_unmerge_discarded` validate unmerging normal, zero, and partially discarded ranges. `test_unmerge_uffd_wp` adds UFFD-WP registration and write protection when supported. `test_prot_none` merges a `PROT_NONE` range, modifies half through `/proc/self/mem`, and unmerges the other half. PRCTL tests verify set/get, inheritance across fork, inheritance across exec of the same binary, and unmerge on disabling PRCTL merging. `test_fork_ksm_merging_page_count` ensures `ksm_merging_pages` accounting is not inherited by children.

## State and persistence behavior
The suite actively starts/stops KSM, writes `pages_to_scan` and `sleep_millisecs`, toggles zero-page merging, mmaps private anonymous memory, changes protections, forks/execs children, and reads pagemap PFNs. `stop_ksmd_and_restore_frequency()` restores selected KSM scan frequency values after the fork/exec test, but the suite generally assumes control of KSM sysfs state during execution.

## Dependencies and integration points
Requires KSM support and writable `/sys/kernel/mm/ksm` controls. Some checks require readable `/proc/self/pagemap`; `test_prot_none` requires `/proc/self/mem`; UFFD-WP coverage requires `__NR_userfaultfd` and `UFFD_FEATURE_PAGEFAULT_FLAG_WP`. The fork/exec test expects the binary to be available as `./ksm_functional_tests`.

## Risks and edge cases
PFN visibility may be restricted, causing skips. KSM merge timing is controlled through sysfs frequency but still depends on kernel scanning behavior. PRCTL operations may be unsupported on older kernels and are skipped on `EINVAL`. The child exit status encodes several failure modes that the parent maps to kselftest results.

## Test signals
Passing signals include absence of duplicate PFNs after unmerge operations, correct `ksm_zero_pages` accounting transitions, successful PRCTL set/get and inheritance behavior, no inherited child `ksm_merging_pages`, and expected UFFD-WP unmerge behavior when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksm_functional_tests.c -->
