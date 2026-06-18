# subset-b-009303 Research

Grouped research for the requested LTP syscall test sources. Each file section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mseal/mseal01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mseal/mseal01.c

Purpose: smoke-test the Linux `mseal(2)` syscall by sealing a page-aligned subrange of an anonymous VMA and verifying that prohibited VMA changes fail with `EPERM`. Important APIs/types/functions: raw `tst_syscall(__NR_mseal, start, len, 0)`, `mprotect()`, `pkey_mprotect()`, `madvise(MADV_DONTNEED)`, `munmap()`, `mremap(MREMAP_FIXED)`, `mmap(MAP_FIXED)`, `struct tcase`, and LTP `TST_EXP_*`/`SAFE_*` helpers. Control flow: `setup()` computes page size, total mapping size, and sealed offset; `run()` forks per testcase because seals survive until process exit, maps memory with the required protection, seals one page, invokes the testcase operation, and exits the child. State/persistence: global mapping parameters are process-local; no filesystem persistence; each child owns and discards the sealed VMA. Dependencies/integration: depends on LTP syscall and pkey compatibility headers, fork support, anonymous private mappings, and kernel `mseal`; integrated as a `tst_test` with `.tcnt` and `.forks_child`. Risks: pointer arithmetic on `void *` relies on GNU C; pkey case may be configuration-sensitive; failures distinguish syscall absence/configuration from semantic regressions through LTP wrappers. Test signals: pass means all listed mutation attempts are denied with `EPERM` after a successful seal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mseal/mseal01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mseal/mseal02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mseal/mseal02.c

Purpose: negative errno coverage for `mseal(2)` invalid inputs and unmapped ranges. Important APIs/types/functions: `tst_syscall(__NR_mseal, addr, len, flags)`, `tst_is_compat_mode()`, `SAFE_MMAP()`, `SAFE_MUNMAP()`, `struct tcase` fields for address pointer, length pointer, flags, expected errno, and compat errno. Control flow: `setup()` maps four pages, creates an unaligned address, unmaps the middle page to create holes, and sets lengths for one, two, four, and overflowing ranges; `run()` selects normal or compat expected errno and asserts failure. State/persistence: global address and size variables model several invalid ranges over one mapping; cleanup unmaps the original area. Dependencies/integration: uses LTP raw syscall wrappers and anonymous mappings; integrated through `.tcnt`, `.setup`, and `.cleanup`. Risks: cleanup attempts to unmap the original four-page span after an interior unmap, which can surface cleanup warnings on kernels that reject partially unmapped spans; compat-mode overflow behavior is explicitly accounted for. Test signals: expected `EINVAL` for bad flags, unaligned start, and overflow, and `ENOMEM` for unallocated starts/ends/gaps.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mseal/mseal02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/msync/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/msync/Makefile

Purpose: build leaf for the `msync` syscall tests. Important APIs/types/functions: `top_srcdir ?= ../../../..`, `include $(top_srcdir)/include/mk/testcases.mk`, and `include $(top_srcdir)/include/mk/generic_leaf_target.mk`. Control flow: no custom targets are declared, so LTP's generic test-case make rules discover and build the C files in this directory. State/persistence: no generated state beyond normal object and binary outputs controlled by the included make framework. Dependencies/integration: depends entirely on the common LTP make fragments for compiler flags, installation layout, cleaning, and target enumeration. Risks: any per-test library requirements must be supplied elsewhere; this file intentionally does not add special flags for the legacy and new `msync` cases. Test signals: successful build of the directory means generic LTP leaf target handling is sufficient for `msync01` through `msync04`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/msync/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/msync/msync01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/msync/msync01.c

Purpose: legacy LTP functional test that verifies `msync(MS_ASYNC)` succeeds for a shared file mapping and propagates modified mapped bytes to the backing file. Important APIs/types/functions: old `test.h` harness, `TEST(msync(...))`, `tst_parse_opts()`, `TEST_LOOPING()`, `tst_tmpdir()`, `mmap(MAP_FILE|MAP_SHARED)`, `lseek()`, `read()`, `munmap()`, and `tst_resm()`. Control flow: each loop calls `setup()`, creates and page-fills a temp file, maps one page writable/shared, writes 256 bytes of value `1` at offset 100 through the mapping, calls `msync`, seeks and reads from the file, compares every byte, then cleans up. State/persistence: uses `TEMPFILE` in an LTP temp directory; mapping changes are intended to persist to the file until cleanup deletes the temp directory. Dependencies/integration: old harness supports command-line loop/timing options and signal setup. Risks: `MS_ASYNC` may not provide immediate writeback on all implementations, making the readback check timing-sensitive; `err_flg` is not reset inside the loop after setup. Test signals: pass confirms syscall success and byte-for-byte file visibility of mapped writes.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/msync/msync01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/msync/msync02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/msync/msync02.c

Purpose: verify `msync(MS_INVALIDATE)` succeeds on a shared mapping and invalidates/refetches data written directly to the backing file. Important APIs/types/functions: old LTP `test.h`, `mmap(MAP_FILE|MAP_SHARED)`, `lseek()`, `write()`, `memcmp()`, `msync()`, and cleanup wrappers. Control flow: setup creates a page-sized temp file, maps it shared, writes `"Testing"` at offset 100 through the file descriptor after mapping, then the test calls `msync(addr, page_sz, MS_INVALIDATE)` and checks that the mapping contains the written bytes. State/persistence: temp file content is the persistent source of truth for the invalidation check; mapping and file descriptor are global and removed in cleanup. Dependencies/integration: legacy LTP harness with temp dir, signal handling, and `TEST_PAUSE`. Risks: `tst_buf` is uninitialized when page-filling the file, though content before the targeted offset is not asserted; filesystem/cache behavior influences how quickly invalidated mappings reflect file writes. Test signals: pass means `MS_INVALIDATE` does not fail and the mapping observes the backing-file update.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/msync/msync02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/msync/msync03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/msync/msync03.c

Purpose: negative errno test for `msync(2)` over locked memory, invalid flags/addresses, and unmapped memory. Important APIs/types/functions: old `test.h`, `tso_safe_macros.h`, `SAFE_MMAP(... MAP_SHARED|MAP_LOCKED ...)`, `msync()`, `RLIMIT_DATA`, `sbrk(0)`, and a `test_case_t` table. Control flow: setup creates a temp file, writes one page, maps it locked/shared, derives invalid addresses (`addr+1`, `rlim_max`, and beyond `sbrk`), then the main loop iterates six cases expecting `EBUSY`, `EINVAL`, or `ENOMEM`. State/persistence: one locked shared mapping and temp file persist across test iterations; cleanup unmaps and closes them. Dependencies/integration: requires memory locking semantics, RLIMIT probing, and legacy LTP loop handling. Risks: address-space heuristics (`rlim_max`, `sbrk()+4*page`) can be architecture or limit sensitive; `MAP_LOCKED` may depend on resource limits. Test signals: pass confirms the kernel rejects invalid `msync` calls with the documented errno.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/msync/msync03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/msync/msync04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/msync/msync04.c

Purpose: modern LTP test that writes through an mmaped file, calls `msync(MS_SYNC)`, and verifies the dirty page state clears or the on-disk content proves synchronization. Important APIs/types/functions: `SAFE_OPEN`, `SAFE_MMAP`, `/proc/self/pagemap`, `/proc/kpageflags`, `O_DIRECT`, `SAFE_MEMALIGN`, `TST_EXP_PASS_SILENT`, and `struct tst_test` filesystem metadata. Control flow: create and write `msync04/testfile`, map it shared, alter one byte, inspect the dirty bit; if dirty is visible, call `msync` and assert it clears, otherwise fall back to O_DIRECT content verification. State/persistence: mounted test filesystem contains the file; page dirty state is read from procfs, not stored. Dependencies/integration: needs root for `/proc/kpageflags`, a mounted device, all filesystems except `tmpfs`, and LTP mount orchestration. Risks: kernel pagemap restrictions, O_DIRECT alignment/FS support, and very fast writeback can turn the test into `TCONF` rather than a strict pass. Test signals: pass indicates `MS_SYNC` synchronizes dirty mapped writes on supported filesystems.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/msync/msync04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munlock/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/munlock/Makefile

Purpose: generic LTP build file for `munlock` tests. Important APIs/types/functions: `top_srcdir`, `testcases.mk`, and `generic_leaf_target.mk`. Control flow: includes the standard test-case rules with no local targets or flags. State/persistence: only build artifacts under the standard LTP build tree. Dependencies/integration: integrates `munlock01.c` and `munlock02.c` into the kernel syscall test suite. Risks: no local flags means both tests must compile with common defaults. Test signals: a successful leaf build produces the two `munlock` executables using shared LTP rules.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munlock/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munlock/munlock01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/munlock/munlock01.c

Purpose: positive coverage for `munlock(2)` with several valid address/length sizes. Important APIs/types/functions: `SAFE_MALLOC`, `SAFE_MLOCK`, `TST_EXP_PASS(munlock(...))`, `free()`, `struct tcase`, and `struct tst_test`. Control flow: each testcase allocates a buffer of 1 byte, 1024 bytes, 1 MiB, or 10 MiB, locks it, calls `munlock`, frees it, and clears the global pointer. State/persistence: global `addr` tracks the active allocation for cleanup; no filesystem state. Dependencies/integration: requires root because locking larger memory ranges can exceed unprivileged limits; uses LTP safe memory and locking wrappers. Risks: memory lock limits or overcommit behavior can break setup before `munlock` is reached; malloc alignment means the syscall covers implementation-rounded pages around the buffer. Test signals: pass means `munlock` succeeds on locked user memory for multiple range sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munlock/munlock01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munlock/munlock02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/munlock/munlock02.c

Purpose: verify `munlock(2)` fails with `ENOMEM` when part of the requested range is not mapped. Important APIs/types/functions: `SAFE_MMAP`, `SAFE_MLOCK`, `SAFE_MUNMAP`, `munlock()`, page sizing, and `TST_EXP_FAIL`. Control flow: setup maps eight pages, writes to them, locks the full range, advances `addr` by two pages, unmaps four pages in the middle, and `run()` calls `munlock(addr, len)` expecting `ENOMEM`. State/persistence: mapping state is intentionally fragmented; no cleanup is declared, so process teardown releases remaining VMAs. Dependencies/integration: root needed for memory locking; anonymous private mappings. Risks: modifies the global base pointer after mapping, so only process exit cleans remaining pages; strict cleanup tooling would need original base preservation. Test signals: expected `ENOMEM` confirms partial unmapped-range detection.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munlock/munlock02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munlockall/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/munlockall/Makefile

Purpose: standard LTP build leaf for the `munlockall` syscall test. Important APIs/types/functions: common `testcases.mk` and `generic_leaf_target.mk` includes. Control flow: delegates target discovery and compilation to the LTP make framework. State/persistence: no custom state beyond build outputs. Dependencies/integration: places `munlockall01.c` under the kernel syscall test make hierarchy. Risks: no special capabilities/flags are encoded in the Makefile; runtime metadata in the C file carries test requirements. Test signals: successful build indicates the generic rules compile this single test.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munlockall/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munlockall/munlockall01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/munlockall/munlockall01.c

Purpose: verify `munlockall(2)` clears all memory locks created by `mlockall(MCL_CURRENT|MCL_FUTURE)`. Important APIs/types/functions: `SAFE_FILE_LINES_SCANF("/proc/self/status", "VmLck: %ld", ...)`, `mlockall()`, `munlockall()`, and LTP result macros. Control flow: read initial `VmLck`, require zero, lock current/future memory, require `VmLck` greater than zero, call `munlockall`, then require `VmLck` returns to zero. State/persistence: process memory lock state is inspected via procfs; no file state is created. Dependencies/integration: depends on `/proc/self/status` format and ability to lock memory under the current limits. Risks: environments with pre-existing locked pages or restrictive memlock limits can break before the syscall assertion. Test signals: pass means kernel accounting shows all memory unlocked after `munlockall`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munlockall/munlockall01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munmap/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/munmap/Makefile

Purpose: generic LTP build leaf for `munmap` syscall tests. Important APIs/types/functions: `top_srcdir`, `testcases.mk`, and `generic_leaf_target.mk`. Control flow: no local targets or flags; all test binaries are built through included rules. State/persistence: no runtime or build state beyond standard outputs. Dependencies/integration: integrates `munmap01`, `munmap03`, and `munmap04` into the syscall suite. Risks: test-specific runtime needs such as root and sysctl restoration live in C metadata, not the Makefile. Test signals: successful build means common rules are sufficient for these tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munmap/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munmap/munmap01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/munmap/munmap01.c

Purpose: positive functional test for full and partial `munmap(2)` behavior, including post-unmap access faulting. Important APIs/types/functions: `SAFE_OPEN`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_FORK`, `SAFE_WAIT`, `WIFSIGNALED`, `SIGSEGV`, and `.test_variants`. Control flow: setup creates a three-page file-backed shared mapping; variant 0 unmaps the full mapping, variant 1 unmaps from the second page through the end; a child then writes to the unmapped start and is expected to die with `SIGSEGV`. State/persistence: temp file backs the mapping; globals track base address, target unmap address, and lengths for cleanup. Dependencies/integration: needs a temp directory and fork support. Risks: cleanup has branchy partial-unmap handling and relies on `map_base = NULL` to avoid double unmapping; the test checks access denial through a child to avoid killing the runner. Test signals: pass means unmapped memory is no longer accessible for both full and partial variants.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munmap/munmap01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munmap/munmap03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/munmap/munmap03.c

Purpose: negative errno test for invalid `munmap(2)` arguments. Important APIs/types/functions: `SAFE_MMAP`, `SAFE_GETRLIMIT(RLIMIT_DATA)`, `munmap()`, `TST_EXP_FAIL`, and a testcase table of address/length pairs. Control flow: setup maps two pages, records zero length, and uses `rlim_max` as an out-of-range address; each case calls `munmap` expecting `EINVAL` for out-of-range address, zero length, or unaligned address. State/persistence: one anonymous mapping is retained for cleanup. Dependencies/integration: LTP safe sysconf and rlimit wrappers. Risks: `run()` passes `tc->addr` to `munmap()` rather than `*tc->addr`, so the syscall receives the address of the testcase's pointer storage; the unaligned entry also uses `&map_addr + 1`, making the modeled invalid address less direct than the comment describes. These values are still invalid, but the test may not exercise the intended exact address cases. Test signals: expected `EINVAL` confirms invalid argument rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munmap/munmap03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munmap/munmap04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/munmap/munmap04.c

Purpose: stress negative test for `munmap(2)` returning `ENOMEM` when unmapping the middle of a VMA would require splitting while the process is at the maximum map count. Important APIs/types/functions: `mmap(MAP_FIXED_NOREPLACE)`, `munmap()`, `MAP_MAX_COUNT`, `RLIMIT_AS`, LTP `save_restore` for `/proc/sys/vm/max_map_count`, and root/min-kernel metadata. Control flow: setup allocates many separated three-page `PROT_NONE` VMAs from a fixed base until mapping fails; `run()` attempts to unmap the middle page of `maps[2]`, expecting `ENOMEM` due to VMA split pressure; cleanup unmaps all recorded regions. State/persistence: process VMA table is the tested state; sysctl `vm/max_map_count` is temporarily restored by LTP. Dependencies/integration: requires root, kernel at least 4.17, `MAP_FIXED_NOREPLACE`, and unlimited address space. Risks: fixed address layout can collide with existing mappings and skip addresses; if map-count behavior changes or the chosen map count is not close enough to the real limit, the expected errno may differ. Test signals: pass indicates the kernel refuses a split that would exceed max map count.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/munmap/munmap04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/name_to_handle_at/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/name_to_handle_at/Makefile

Purpose: generic build leaf for `name_to_handle_at` syscall tests. Important APIs/types/functions: standard `testcases.mk` and `generic_leaf_target.mk`. Control flow: delegates compilation and installation to LTP's common make rules. State/persistence: no custom state. Dependencies/integration: covers the three C tests in the directory and relies on their runtime metadata for root/tempdir needs. Risks: no special feature flags are set here; compatibility comes from included LTP headers. Test signals: successful build produces all `name_to_handle_at` test binaries.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/name_to_handle_at/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/name_to_handle_at/name_to_handle_at01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/name_to_handle_at/name_to_handle_at01.c

Purpose: basic success coverage for `name_to_handle_at(2)` combined with `open_by_handle_at(2)` using multiple dirfd/path/flag/open-mode combinations. Important APIs/types/functions: `allocate_file_handle()`, `name_to_handle_at()`, `open_by_handle_at()`, `struct file_handle`, `AT_FDCWD`, `AT_EMPTY_PATH`, `AT_SYMLINK_FOLLOW`, and `SAFE_FSTAT`. Control flow: setup creates a temp directory, chdirs into it, creates files, opens directory and file descriptors, allocates a handle buffer, then each testcase resolves a handle and reopens it by handle before checking stat size. State/persistence: test files live in an LTP temp directory; handles are kernel-exported object identifiers. Dependencies/integration: requires root and a filesystem that supports file handles; uses LTP lapi wrapper definitions. Risks: file-handle support varies by filesystem; the stat check is minimal and treats empty-path cases specially. Test signals: pass means valid handles can be obtained and used for several access modes.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/name_to_handle_at/name_to_handle_at01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/name_to_handle_at/name_to_handle_at02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/name_to_handle_at/name_to_handle_at02.c

Purpose: failure-mode coverage for `name_to_handle_at(2)`. Important APIs/types/functions: `struct file_handle`, `MAX_HANDLE_SZ`, `tst_get_bad_addr()`, invalid dirfd/path/handle/mount-id cases, and LTP `TEST()`/`TST_ERR`. Control flow: setup creates one file and assigns bad-address pointers for path, handle, and mount-id; each testcase zeros the valid handle, calls the syscall, and checks it fails with the expected errno. State/persistence: single temp file plus static handle buffers; no state beyond tempdir. Dependencies/integration: LTP tmpdir and bad-address helpers; no root requirement in this file. Risks: errno can vary for bad fd `0` if stdin characteristics differ, though the testcase expects `ENOTDIR` when treating fd 0 as a directory fd. Test signals: expected `EBADF`, `ENOTDIR`, `EFAULT`, `EOVERFLOW`, `EINVAL`, and `ENOENT` demonstrate argument validation.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/name_to_handle_at/name_to_handle_at02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/name_to_handle_at/name_to_handle_at03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/name_to_handle_at/name_to_handle_at03.c

Purpose: cover newer `name_to_handle_at(2)` handle-type flags `AT_HANDLE_FID` and `AT_HANDLE_CONNECTABLE`. Important APIs/types/functions: `name_to_handle_at()`, `AT_HANDLE_FID`, `AT_HANDLE_CONNECTABLE`, `MAX_HANDLE_SZ`, `struct file_handle`, and `handle_type_supported()`. Control flow: setup creates a test file, allocates a max-sized handle buffer, probes each flag by calling with invalid dirfd and interpreting `EINVAL` as unsupported; run sets `handle_bytes`, calls the syscall with testcase flags, and validates success or expected `EINVAL`. State/persistence: one temp file and a reusable handle buffer. Dependencies/integration: LTP lapi flag definitions and kernel support for commit/tag `48b77733d0db`; tempdir required. Risks: support probing uses errno from a deliberately invalid call and may skip the whole test on older kernels; `/proc/filesystems` is used as an unexportable-file scenario. Test signals: pass confirms FID handles work and connectable FID combinations are rejected as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/name_to_handle_at/name_to_handle_at03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nanosleep/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nanosleep/Makefile

Purpose: build leaf for `nanosleep` tests with per-target realtime library linkage. Important APIs/types/functions: `nanosleep01: LDLIBS+=-lrt`, `nanosleep02: LDLIBS+=-lrt`, plus common `testcases.mk` and `generic_leaf_target.mk`. Control flow: augments linker flags for the timer-based tests before including standard LTP rules. State/persistence: only build artifacts. Dependencies/integration: links tests using LTP timer helpers against librt where needed by platform toolchains. Risks: `nanosleep04` does not get explicit `-lrt`, which is correct for its direct syscall/libc use but matters if helper dependencies change. Test signals: successful build proves the per-target link augmentation is sufficient.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nanosleep/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nanosleep/nanosleep01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nanosleep/nanosleep01.c

Purpose: timer-framework sample test that verifies `nanosleep()` returns success and sleeps for requested durations. Important APIs/types/functions: `tst_timer_test.h`, `tst_timespec_from_us()`, `tst_timer_start()`, `tst_timer_stop()`, `tst_timer_sample()`, `TEST(nanosleep())`, and `struct tst_test` `.scall`/`.sample`. Control flow: the LTP timer framework calls `sample_fn` with clock id and microsecond duration; the function converts to timespec, times the sleep, records the sample, and fails if return is nonzero. State/persistence: no persistent state; timing samples are kept by the harness. Dependencies/integration: requires LTP timer test harness and librt linkage from the Makefile. Risks: scheduler latency affects timing quality, but this function only checks syscall success while the framework evaluates timing bounds. Test signals: pass means `nanosleep` completed normally for sampled intervals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nanosleep/nanosleep01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nanosleep/nanosleep02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nanosleep/nanosleep02.c

Purpose: verify interrupted `nanosleep()` returns `-1/EINTR` and reports a plausible remaining time. Important APIs/types/functions: `SAFE_FORK`, `SAFE_KILL(SIGINT)`, `SAFE_SIGNAL`, `tst_timer_*`, `tst_timespec_diff`, `tst_timespec_abs_diff_us`, and `USEC_PRECISION`. Control flow: parent forks a child, sleeps one second, sends `SIGINT`; child starts a monotonic timer, calls `nanosleep` for about five seconds, checks `EINTR`, confirms it did not oversleep, computes expected remaining time, and compares it with the returned `timerem` within 250 ms. State/persistence: child-local timing and remaining-time structures; no file state. Dependencies/integration: fork and signal delivery, monotonic timer support, and LTP timer helpers. Risks: heavy scheduling delay around signal delivery can widen remaining-time differences; the precision margin is intentionally broad. Test signals: pass confirms correct interruption semantics and useful `rem` accounting.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nanosleep/nanosleep02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nanosleep/nanosleep04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nanosleep/nanosleep04.c

Purpose: negative argument validation for `nanosleep(2)`. Important APIs/types/functions: static `struct timespec` testcase array, `TEST(nanosleep())`, `TST_RET`, `TST_ERR`, and `EINVAL` checks. Control flow: each case passes either negative seconds, nanoseconds equal to one billion, or negative nanoseconds and requires `-1/EINVAL`. State/persistence: no mutable state beyond the testcase index. Dependencies/integration: modern `tst_test` `.tcnt` dispatch. Risks: none significant; uses direct libc wrapper behavior matching kernel validation. Test signals: pass means invalid timespec fields are rejected with `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nanosleep/nanosleep04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/newuname/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/newuname/Makefile

Purpose: generic LTP build leaf for the `newuname`/`uname` test. Important APIs/types/functions: common make includes. Control flow: no local flags or targets; standard rules build `newuname01`. State/persistence: only build products. Dependencies/integration: integrates the raw `uname` syscall test into LTP's kernel syscall suite. Risks: no special handling for architecture-specific machine field is needed at build time. Test signals: successful build indicates common rules compile the test.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/newuname/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/newuname/newuname01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/newuname/newuname01.c

Purpose: verify raw `uname(2)` succeeds and returned UTS fields match Linux and `/proc/sys/kernel` values where practical. Important APIs/types/functions: `tst_syscall(__NR_uname, name)`, `struct utsname`, `TST_EXP_EQ_STR`, `SAFE_FILE_READ_STR`, `PATH_KERN_HOSTNAME`, `PATH_KERN_OSRELEASE`, `PATH_KERN_VERSION`, and `PATH_KERN_DOMAINNAME`. Control flow: buffer allocation is declared via `.bufs`; `run()` invokes the syscall, stops if it fails, compares `sysname` with `"Linux"`, then reads proc sysctl strings and compares nodename, release, version, and domainname. State/persistence: read-only system identity state from kernel/procfs; no writes. Dependencies/integration: requires procfs paths exposed by LTP path macros. Risks: hostname/domainname can change concurrently, and the `machine` field is intentionally not asserted due to architecture complexity. Test signals: pass means raw syscall output agrees with kernel proc identity strings.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/newuname/newuname01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nftw/Makefile

Purpose: custom build file for paired `nftw` and `nftw64` conformance executables. Important APIs/types/functions: `_XOPEN_SOURCE=500`, `_XOPEN_SOURCE_EXTENDED`, `MAKE_TARGETS := nftw01 nftw6401`, `nftw01` object list, `%64.o: CPPFLAGS += -D_LARGEFILE64_SOURCE`, and `nftw01: CPPFLAGS += -D_LARGEFILE_SOURCE`. Control flow: includes common LTP make rules, declares explicit link recipes that combine driver, tools, test functions, tests, and shared library objects, then delegates leaf behavior. State/persistence: build outputs are two executables and object files. Dependencies/integration: uses glibc/XSI feature-test macros to expose `nftw`, `nftw64`, `struct FTW`, `FTW_*` constants, and large-file interfaces. Risks: custom object dependencies must remain in sync between 32-bit and 64-bit variants; duplicate source structure increases drift risk. Test signals: successful build produces `nftw01` and `nftw6401` with the intended feature macros.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/lib.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nftw/lib.c

Purpose: shared negative-path helpers for the 32-bit `nftw` tests, especially pathname length and errno validation. Important APIs/types/functions: `pathconf(_PC_PATH_MAX/_PC_NAME_MAX)`, `malloc`, `execute_function()`, `test_ENAMETOOLONG_path()`, `test_ENAMETOOLONG_name()`, `test_ENOENT_empty()`, `test_ENOTDIR()`, `test_ENOENT_nofile()`, and cleanup helpers. Control flow: helper functions synthesize overlong paths/components or missing/not-directory paths, call a provided callback, require a specific return value, and validate `errno`; failures call `cleanup_function()` and `fail_exit()`. State/persistence: uses global `s2`, `temp`, and files under `./tmp`; cleanup unlinks temporary negative-test files. Dependencies/integration: called by `test24A` to `test28A` in `test.c` through `callback()` from `tools.c`. Risks: path synthesis assumes pathconf values leave enough room for constructed components; callbacks returning sentinel `-752` are treated as callback internal failures even though this file never creates that value. Test signals: pass supports `nftw` errno behavior for long, empty, missing, and non-directory paths.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/lib64.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nftw/lib64.c

Purpose: 64-bit counterpart of `lib.c` for `nftw64` negative-path testing. Important APIs/types/functions: same public helpers as `lib.c`, using `nftw64.h` declarations and callback signatures that eventually call `nftw64()`. Control flow: builds overlong file/path buffers using `pathconf`, executes the callback, compares return value and `errno`, and aborts via LTP failure paths on mismatch. State/persistence: temporary files under `./tmp` model ENOENT and ENOTDIR; global `s2` and `temp` communicate with the driver. Dependencies/integration: consumed by `test64.c` errno tests; paired with `tools64.c` callback. Risks: near-duplicate code can diverge subtly from the 32-bit variant; relies on filesystem path limits and permissions behaving predictably for the nobody user. Test signals: pass indicates the `nftw64` wrapper reports expected errno for invalid paths.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/lib64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/nftw.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nftw/nftw.c

Purpose: main 32-bit `nftw()` conformance driver coordinating a large POSIX/XSI behavior suite. Important APIs/types/functions: global `pathdat[]` filesystem model, `goodlist`, `badlist`, `mnem`, `setup_path()`, `cleanup_function()`, `test1A()` through `test30A()`, `blenter()`, `blexit()`, and old LTP `test.h` reporting. Control flow: setup switches to user `nobody`, creates an LTP tempdir, populates the synthetic tree, then runs 30 blocks covering traversal, symbolic-link behavior, depth/preorder ordering, `FTW_CHDIR`, callback arguments, `FTW_*` classifications, descriptor usage, callback return propagation, and errno failures. State/persistence: extensive global state records path data, visit counts, expected lists, fd probes, and block status; filesystem state lives under `./tmp` and is removed at end. Dependencies/integration: integrates all other 32-bit `nftw` files; depends on `nobody`, POSIX permissions, symlinks, and old harness cleanup. Risks: tests mutate global `badlist` and remove `./tmp/byebye`, so ordering is significant; old permission tests can behave differently as root, hence the setuid to nobody. Test signals: each block reports TPASS/TFAIL, with final `anyfail()` summarizing suite status.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/nftw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/nftw.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nftw/nftw.h

Purpose: shared declarations, constants, and prototypes for the 32-bit `nftw` test program. Important APIs/types/functions: feature headers `<ftw.h>`, filesystem/stat headers, LTP `test.h`, constants such as `MAX_FD`, `MAXOPENDIRS`, `NFTW`, `NFTW2`, `LINK_CNT`, `NO_LINK_CNT`, `pathdata`, `struct list`, and prototypes for driver, callback, tools, and library helpers. Control flow: no executable control flow; it defines the compile-time contract connecting `nftw.c`, `test.c`, `test_func.c`, `tools.c`, and `lib.c`. State/persistence: declares data shapes for synthetic filesystem entries and expected traversal lists. Dependencies/integration: exposes old LTP harness APIs and POSIX nftw types to all 32-bit variant compilation units. Risks: prototypes must match callback signatures exactly; unlike the 64-bit header, some declarations omit `extern`, relying on C declaration rules. Test signals: successful compilation of all 32-bit objects validates this header's integration contract.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/nftw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/nftw64.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nftw/nftw64.c

Purpose: main `nftw64()` conformance driver, mirroring `nftw.c` while exercising large-file-aware stat callback signatures. Important APIs/types/functions: `pathdat[]`, `goodlist`, `badlist`, `mnem` including `FTW_DP` and `FTW_SLN`, `setup_path()`, `test1A()` through `test30A()`, and `TCID = "nftw6401"`. Control flow: runs the same 30 behavior blocks as the 32-bit driver after switching to `nobody` and creating the synthetic tree; debug strings and called test helpers target `nftw64`. State/persistence: same global traversal and filesystem state as `nftw.c`; temporary tree under `./tmp`. Dependencies/integration: links with `test64.c`, `test_func64.c`, `tools64.c`, and `lib64.c`; requires `_LARGEFILE64_SOURCE` from the Makefile. Risks: duplicated driver logic can drift from 32-bit behavior; `nobody` and permission semantics are required for `FTW_DNR`, `FTW_NS`, and EACCES checks. Test signals: block-level TPASS/TFAIL plus final suite pass verifies `nftw64` traversal, metadata, and errno behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/nftw64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/nftw64.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nftw/nftw64.h

Purpose: shared declarations for the `nftw64` test variant. Important APIs/types/functions: same constants and structures as `nftw.h`, but callback prototypes use `const struct stat64 *` and tools expose `nftw64_fn()`. Control flow: no runtime flow; provides the ABI contract among 64-bit variant objects. State/persistence: defines `pathdata` and expected-list structures used to create and validate the test tree. Dependencies/integration: requires feature macros from the Makefile so `struct stat64` and `nftw64()` are visible. Risks: include guard name `_NFTW_H_` matches `nftw.h`, so including both headers in one translation unit would suppress the second; current build never mixes them. Test signals: successful 64-bit variant compilation confirms prototype compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/nftw64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/test.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nftw/test.c

Purpose: implements the 30 individual 32-bit `nftw()` assertions driven by `nftw.c`. Important APIs/types/functions: `nftw()`, `test_func1` through `test_func23`, `test_ENAMETOOLONG_*`, `test_ENOENT_*`, `test_ENOTDIR`, `FTW_PHYS`, `FTW_DEPTH`, `FTW_CHDIR`, `MAX_FD`, `next_fd`, `visit`, and global expected lists. Control flow: early tests validate traversal counts and link following; middle tests validate order, callback path/stat/type/FTW metadata, symlink and unreadable directory classification; later tests verify fd closure/depth limits, propagation of nonzero callback returns, and errno cases. State/persistence: mutates global `visit`, `dirlist`, `badlist`, `next_fd`, and filesystem permissions/links, so execution order is part of the contract. Dependencies/integration: callbacks live in `test_func.c`, negative helpers in `lib.c`, and `callback()` in `tools.c`. Risks: contains legacy duplication/typos and some EACCES tests call `test_ENOTDIR`, making historical behavior brittle; global mutation makes tests hard to isolate. Test signals: failures call cleanup and `fail_exit`; returning normally lets the driver mark each block passed.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/test64.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nftw/test64.c

Purpose: `nftw64()` version of the 30 assertion functions in `test.c`. Important APIs/types/functions: `nftw64()`, `struct stat64` callbacks, `test_func*`, `test_ENAMETOOLONG_*`, `FTW_*` flags, visit counting, descriptor probes, and negative path callbacks. Control flow: mirrors the 32-bit sequence while invoking `nftw64`; validates traversal, symlink policy, order, callback data, descriptor behavior, callback return propagation, and errno handling. State/persistence: same global mutable state and synthetic `./tmp` tree as the 32-bit tests; mutations such as unlinking `byebye` and changing `badlist` are order-dependent. Dependencies/integration: links with `nftw64.c`, `test_func64.c`, `tools64.c`, and `lib64.c`. Risks: duplicated logic can diverge; because it uses large-file feature macros and `stat64` signatures, platform libc exposure is a build risk. Test signals: successful return from each test function produces a passing block in the 64-bit driver.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/test64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/test_func.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nftw/test_func.c

Purpose: callback implementations used by the 32-bit `nftw()` assertion tests. Important APIs/types/functions: callbacks `test_func1`, `test_func3` through `test_func23`, `struct FTW`, `struct stat`, `stat()`, `lstat()`, `getcwd()`, `open()/close()` fd probes, `ftw_mnemonic()`, and helpers `getbase()`/`getlev()`. Control flow: each callback is specialized: record visited paths, detect duplicate symlink targets, stop traversal to test ordering, verify `FTW_CHDIR`, compare callback pathnames/stat fields/type values, inspect `FTW` base/level, check symlink classifications, enforce no descendant traversal for `FTW_DNR`, and validate fd usage. State/persistence: writes global `dirlist`, increments `visit`, reads/mutates expected globals, and opens files transiently. Dependencies/integration: called only by `test.c`; relies on the tree and permissions built by `tools.c`. Risks: returning sentinel values such as 998/999 drives test outcomes; stat comparisons may be sensitive to metadata changes during traversal. Test signals: returning 0 means callback observation matched expectations; 999/998 propagate as test failures or intentional stop signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/test_func.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/test_func64.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nftw/test_func64.c

Purpose: callback suite for `nftw64()` tests, equivalent to `test_func.c` but with `struct stat64` callback arguments. Important APIs/types/functions: `test_func1` through `test_func23`, `struct stat64`, `struct FTW`, `stat()`/`lstat()` comparison, fd probes, global `visit`, `dirlist`, `badlist`, and helper formatters. Control flow: records and validates traversal observations for the same behavior matrix as the 32-bit callbacks: path reporting, metadata, type codes, symlink handling, unreadable directories, base/level fields, descriptor usage, and early stop semantics. State/persistence: transient fd opens plus global counters/lists; no independent filesystem creation. Dependencies/integration: linked into `nftw6401` and called from `test64.c`. Risks: compares `struct stat64` callback data to `struct stat` local data in some paths, which assumes equivalent visible fields; duplicate source is maintenance-heavy. Test signals: callback returns 0 for matching behavior and nonzero sentinel values to fail or intentionally terminate traversal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/test_func64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/tools.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nftw/tools.c

Purpose: filesystem setup, cleanup, utility, and errno callback support for the 32-bit `nftw` suite. Important APIs/types/functions: `cleanup_function()`, `setup_path()`, `nftw_fn()`, `callback()`, `ftw_mnemonic()`, `getbase()`, `getlev()`, `do_info()`, and `fail_exit()`. Control flow: setup creates `./tmp`, iterates `pathdat[]` to make directories/files/symlinks, writes file contents, and adjusts permissions to create unreadable/unsearchable cases; cleanup restores permissions and runs `rm -rf ./tmp`; callback wraps `nftw(path, nftw_fn, 10, FTW_MOUNT)` for errno helper tests. State/persistence: creates and removes the entire synthetic test tree; uses global `ebuf`, `mnem`, and `temp`. Dependencies/integration: used by `nftw.c`, `test.c`, and `lib.c`. Risks: cleanup uses `system("rm -rf ./tmp")` and `wait(NULL)`; permission setup assumes running as `nobody` after driver setup. Test signals: setup success is prerequisite for all traversal assertions; utility mismatches report via `fail_exit`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/tools.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/tools64.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nftw/tools64.c

Purpose: `nftw64` variant of the setup, cleanup, utility, and errno callback support. Important APIs/types/functions: `setup_path()`, `cleanup_function()`, `nftw64_fn()`, `callback()` calling `nftw64(... FTW_MOUNT)`, `ftw_mnemonic()`, `getbase()`, `getlev()`, and `fail_exit()`. Control flow: builds the same synthetic tree from `pathdat[]`, sets permissions for classification/error tests, removes the tree in cleanup, and provides a minimal `nftw64` callback for negative path helpers. State/persistence: filesystem state under `./tmp` plus shared globals; no independent persistent data. Dependencies/integration: linked with the 64-bit driver, tests, callbacks, and lib helpers. Risks: same shell cleanup and permission assumptions as the 32-bit tools; near-duplicate code can drift, but the main semantic difference is `nftw64_fn` and `struct stat64`. Test signals: successful setup enables all `nftw64` traversal and errno blocks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nftw/tools64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nice/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nice/Makefile

Purpose: build leaf for `nice` syscall tests, adding pthread support for `nice05`. Important APIs/types/functions: `nice05: CFLAGS += -pthread`, common LTP make includes. Control flow: applies a target-specific compiler flag before generic target rules. State/persistence: standard build artifacts only. Dependencies/integration: integrates five C tests; `nice05` needs pthread headers and link behavior supplied by the flag/toolchain. Risks: if a platform requires pthread linker flags separately from `CFLAGS`, common LTP make handling must propagate it correctly. Test signals: successful build proves all `nice` tests compile, including the threaded scheduler test.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nice/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice01.c

Purpose: verify root can decrease nice values by passing negative increments to `nice(2)`. Important APIs/types/functions: `nice()`, `SAFE_GETPRIORITY(PRIO_PROCESS, 0)`, `MIN_PRIO`, `MAX()`, LTP `TEST()`, and root metadata. Control flow: for increments `-1`, `-12`, and `-50`, read original priority, call `nice`, compute clamp at `-20`, compare return and actual priority, then restore by applying the delta. State/persistence: process priority changes during each case and is restored. Dependencies/integration: requires root/CAP_SYS_NICE behavior. Risks: return semantics of `nice()` can be confused with `-1` plus errno; this test explicitly checks `TST_ERR` after comparing return. Test signals: pass means privileged priority improvement is honored and clamped correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice02.c

Purpose: verify any user can increase nice value beyond the maximum and it clamps to 19. Important APIs/types/functions: `nice(NICEINC)`, `SAFE_GETPRIORITY()`, `MAX_PRIO`, and LTP result macros. Control flow: call `nice(50)`, assert no error, read current priority, require `19`, report pass, and call `nice(0)` as a no-op sanity operation. State/persistence: changes the process nice value for the duration of the test process. Dependencies/integration: no root requirement; modern `tst_test` `.test_all`. Risks: the final `nice(DEFAULT_PRIO)` with increment zero does not restore priority, but process exit discards the state. Test signals: pass means unprivileged worsening of priority succeeds and saturates at max nice.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice03.c

Purpose: verify a normal process can increase nice by a small positive increment. Important APIs/types/functions: `SAFE_FORK`, `nice(2)`, `SAFE_GETPRIORITY`, `MIN()`, `MAX_PRIO`, and child reaping. Control flow: parent forks; child records original priority, calls `nice(2)`, verifies return/no errno and actual priority equals `min(19, orig+2)`, reports pass, and exits; parent reaps. State/persistence: priority changes are isolated to the child process. Dependencies/integration: fork support through LTP `.forks_child`. Risks: if inherited priority is already at max, expected value remains 19 and still passes. Test signals: pass confirms ordinary priority lowering works without privilege.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice04.c

Purpose: verify an unprivileged user cannot increase process priority with a negative nice increment. Important APIs/types/functions: `SAFE_GETPWNAM("nobody")`, `SAFE_SETUID()`, `nice(-10)`, `EPERM`, and LTP `TEST()`. Control flow: setup switches from root to nobody; run calls `nice(-10)` and requires return `-1` with `EPERM`. State/persistence: effective process credentials are permanently dropped in the test process. Dependencies/integration: requires root to switch users and a `nobody` passwd entry. Risks: systems with unusual capabilities retained after setuid could alter result; typo in failure string is cosmetic. Test signals: pass means unprivileged priority improvement is denied.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice05.c

Purpose: scheduler behavior test asserting a lower nice value thread receives at least as much CPU time as a higher nice value thread when both run on one CPU. Important APIs/types/functions: pthread barriers/create/cancel/join, `nice()`, `pthread_getcpuclockid()`, `clock_gettime()`, CPU affinity macros, `sched_getaffinity()`, `sched_setaffinity()`, and LTP safe pthread/clock helpers. Control flow: setup pins the process to one available CPU; run creates two busy-loop threads with increments `-1` and `-2`, releases them together, sleeps for the runtime, samples per-thread CPU clocks, and compares low-nice CPU time against high-nice. State/persistence: process CPU affinity and thread priorities change during the test; threads are canceled and joined. Dependencies/integration: root for negative nice, pthread build flag, CPU affinity support, and runtime of three seconds. Risks: scheduler noise, CPU isolation/cgroups, or RT policies can make CPU-time ordering flaky; `some_cpu` is not initialized before scanning but is set if affinity has at least one CPU. Test signals: pass means the lower nice thread accumulated more CPU time.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/nice/nice05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/Makefile

Purpose: build leaf for `open(2)` tests with large-file compilation flags. Important APIs/types/functions: common LTP make includes plus `CFLAGS += -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE`. Control flow: standard make rules build all open tests after applying directory-wide large-file macros. State/persistence: standard build outputs only. Dependencies/integration: large-file macros support tests such as `open12` and general 64-bit offsets. Risks: directory-wide feature macros can affect all tests' ABI expectations, but that is intentional for open syscall coverage. Test signals: successful build means all listed open tests compile under large-file mode.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open01.c

Purpose: basic `open(2)` mode-bit checks for file creation and directory opening. Important APIs/types/functions: `open()`, `O_CREAT`, `O_DIRECTORY`, `SAFE_FSTAT`, `S_ISVTX`, `S_IFDIR`, and testcase table. Control flow: setup creates `testdir`; each case opens either a new file with mode `01444` or the directory with `O_DIRECTORY`, stats the fd, verifies the expected bit is set, closes, and unlinks regular files. State/persistence: tempdir contains `testdir` and transient `testfile`. Dependencies/integration: `_GNU_SOURCE` for `O_DIRECTORY`; LTP tmpdir. Risks: comment says sticky bit should not be cleared on Linux, and the code expects it set; behavior differs from some historical POSIX wording. Test signals: pass confirms Linux preserves requested sticky bit on file creation and reports directory mode on directory fd.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open02.c

Purpose: negative `open(2)` checks for missing files without `O_CREAT` and unprivileged `O_NOATIME`. Important APIs/types/functions: `SAFE_TOUCH`, `SAFE_GETPWNAM("nobody")`, `SAFE_SETEUID`, `open()`, `O_NOATIME`, `TST_EXP_FAIL2`, and cleanup credential restore. Control flow: setup creates `test_file2`, switches effective uid to nobody, then cases expect `ENOENT` for opening absent `test_file` with `O_RDWR` and `EPERM` for opening another user's file with `O_RDONLY|O_NOATIME`. State/persistence: temp file exists; effective uid changes during test and cleanup restores root euid. Dependencies/integration: requires root and a nobody account. Risks: `O_NOATIME` permission depends on file ownership/capabilities; retained capabilities after euid switch could affect result. Test signals: pass confirms expected errno for both missing-create and no-atime privilege cases.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open03.c

Purpose: minimal positive `open(2)` test for `O_RDWR|O_CREAT`. Important APIs/types/functions: `TST_EXP_FD(open(...))`, `SAFE_CLOSE`, and `SAFE_UNLINK`. Control flow: create/open `testfile` with mode `0700`, close the returned fd, and unlink it. State/persistence: transient file in LTP tempdir. Dependencies/integration: modern `tst_test` `.needs_tmpdir`. Risks: narrow smoke test only checks that the open returns a valid fd. Test signals: pass means basic create/open/close/unlink workflow succeeds.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open04.c

Purpose: verify `open(2)` fails with `EMFILE` after the per-process fd limit is reached. Important APIs/types/functions: `SAFE_GETRLIMIT(RLIMIT_NOFILE)`, `SAFE_OPEN`, repeated `open()`, `EMFILE`, fd array allocation, and cleanup close loop. Control flow: setup opens one base file, allocates space from first fd to limit, opens unique files until `EMFILE` or limit, records all fds; run attempts one more open expecting `EMFILE`; cleanup closes recorded fds and frees memory. State/persistence: many temp files and open descriptors are created; fd table saturation is the tested state. Dependencies/integration: tempdir and current `RLIMIT_NOFILE`. Risks: huge fd limits can allocate/open many files and take time; if first fd is high, array sizing depends on `fds_limit - first`. Test signals: pass confirms kernel enforces the per-process open fd limit.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open06.c

Purpose: verify nonblocking write-only open of a FIFO with no readers fails with `ENXIO`. Important APIs/types/functions: `SAFE_MKFIFO`, `open(O_NONBLOCK|O_WRONLY)`, and `TST_EXP_FAIL2`. Control flow: setup creates a FIFO in tempdir; run attempts the nonblocking writer open and expects failure. State/persistence: one FIFO in tempdir. Dependencies/integration: filesystem support for FIFOs. Risks: if another process opens the FIFO for reading unexpectedly, result would change, but tempdir isolation makes that unlikely. Test signals: pass confirms FIFO open semantics for no-reader nonblocking writers.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open07.c

Purpose: validate `O_NOFOLLOW` behavior on symlinks and symlinked path prefixes. Important APIs/types/functions: `SAFE_CREAT`, `SAFE_MKDIR`, `SAFE_SYMLINK`, `open(O_NOFOLLOW|O_RDONLY)`, and a testcase table. Control flow: setup creates a file, directory, direct and double symlinks to each, and a real file through a symlinked directory; run expects `ELOOP` when the final component is a symlink and success when only an intermediate directory component is a symlink. State/persistence: tempdir symlink graph. Dependencies/integration: symlink-capable filesystem and GNU `O_NOFOLLOW`. Risks: `O_NOFOLLOW` only constrains the final component, which is exactly the subtle behavior tested. Test signals: pass confirms correct `ELOOP` and success cases.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open07.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open08.c

Purpose: table-driven negative `open(2)` errno coverage. Important APIs/types/functions: `O_CREAT|O_EXCL`, `O_DIRECTORY`, `O_WRONLY`, bad address from `tst_get_bad_addr()`, credential switch to nobody, and expected errors `EEXIST`, `EISDIR`, `ENOTDIR`, `ENAMETOOLONG`, `EACCES`, `EFAULT`. Control flow: setup creates a root-owned restricted file, switches gid/uid to nobody, creates an existing file as nobody, and initializes an unmapped filename pointer; run invokes each case and checks errno. State/persistence: tempdir files and credential state. Dependencies/integration: requires root, nobody account, and `/tmp` directory for the EISDIR case. Risks: the hardcoded long filename must exceed NAME_MAX on the temp filesystem; bad-address behavior is architecture-specific but mediated by LTP. Test signals: pass confirms several documented open failure paths.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open09.c

Purpose: verify access mode restrictions on fds returned by `open(2)`. Important APIs/types/functions: `SAFE_OPEN`, `O_RDONLY`, `O_WRONLY`, `read()`, `write()`, `TST_EXP_FAIL(..., EBADF)`, and `SAFE_CLOSE`. Control flow: setup creates a temp file; testcase 0 opens read-only and expects `write` to fail `EBADF`; testcase 1 opens write-only and expects `read` to fail `EBADF`. State/persistence: one temp file. Dependencies/integration: modern LTP `.tcnt = 2`. Risks: buffer content is irrelevant; the test checks descriptor access mode, not filesystem permissions. Test signals: pass confirms fd mode enforcement for read/write operations.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open10.c

Purpose: verify group ownership and setgid bit behavior for files created by `open(O_CREAT|O_EXCL)`. Important APIs/types/functions: `SAFE_GETPWNAM`, `tst_get_free_gid()`, `SAFE_MKDIR`, `SAFE_CHOWN`, `SAFE_CHMOD`, `SAFE_SETGID`, `SAFE_SETREUID`, `SAFE_OPEN`, `SAFE_STAT`, and `S_ISGID`. Control flow: create one normal directory and one setgid directory owned by nobody/free gid; switch to nobody to create files in each and validate inherited gid/setgid bit; switch back to root to create another setgid file; purge tempdir between loops. State/persistence: directory ownership/mode and created files are the tested state. Dependencies/integration: requires root, a nobody user, free gid discovery, and tempdir. Risks: filesystem-specific setgid inheritance or CVE-related behavior is acknowledged by skipping one setgid bit check. Test signals: pass confirms Linux open-create ownership semantics in setgid and non-setgid directories.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open11.c

Purpose: broad table-driven `open(2)` behavior test across regular files, directories, hard links, symlinks, device nodes, creation, and odd flag combinations. Important APIs/types/functions: `open()`, `O_RDONLY/O_WRONLY/O_RDWR/O_SYNC/O_TRUNC/O_DIRECTORY/O_CREAT`, `SAFE_LINK`, `SAFE_SYMLINK`, `SAFE_MKNOD`, `makedev(1,5)`, and expected errno handling. Control flow: setup creates regular/empty files, hardlink, symlinks, directory, symlinked directory, and a char device on a mounted devfs; each testcase either expects a valid fd, a specific errno, or treats undefined `O_RDONLY|O_TRUNC` behavior as pass if it returns. State/persistence: mounted test point contains device node; tempdir contains link graph and files. Dependencies/integration: root and `.needs_devfs` with mountpoint. Risks: device special file behavior can depend on devfs/container policies; undefined truncation cases intentionally do not assert result. Test signals: pass means the kernel handles the enumerated path/flag combinations without incorrect errno or hangs.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open12.c

Purpose: functional coverage for `O_APPEND`, `O_NOATIME`, `O_CLOEXEC`, and `O_LARGEFILE`. Important APIs/types/functions: `open()`, `lseek()`, `stat()`, `O_DIRECT`-independent large offsets, `fork()`, `execlp("open12_child")`, `linkage to lapi/fcntl.h`, `MS_STRICTATIME`, and all-filesystems metadata. Control flow: setup writes a test file; cases check append moves writes to EOF, no-atime preserves access time after read, close-on-exec prevents the child from writing to inherited fd, and largefile allows seeking/writing past 4 GiB then reopening. State/persistence: mounted filesystem test files, atime metadata, and child exec fd table. Dependencies/integration: needs root, fork, helper binary in PATH/test install, all-filesystems mount with strict atime, and large-file flags from Makefile. Risks: atime can be affected by mount options; sparse large-file behavior depends on filesystem support; helper lookup must find `open12_child`. Test signals: pass confirms these open flags have their documented effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open12_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open12_child.c

Purpose: exec-side helper for `open12` `O_CLOEXEC` verification. Important APIs/types/functions: `atoi()`, `write(fd, argv[1], strlen(argv[1]))`, process exit status, and simple argc validation. Control flow: expects one fd argument, converts it to an integer, attempts to write the fd string to that descriptor, and returns `ret != -1`; this yields exit 0 when write fails because the fd was closed on exec, and exit 1 when it stayed open. State/persistence: only attempts to write to an inherited fd; no files opened itself. Dependencies/integration: launched by `open12.c` via `execlp("open12_child", ...)`. Risks: return convention is inverted for the parent test's pass/fail mapping, so changes must preserve it. Test signals: exit 0 indicates `O_CLOEXEC` worked; exit 1 indicates descriptor leak.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open12_child.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open13.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open13.c

Purpose: validate `O_PATH` descriptors reject operations that require an opened file description. Important APIs/types/functions: `O_PATH`, `SAFE_DUP`, `read`, `write`, `fchmod`, `fchown`, `ioctl(FIGETBSZ)`, `mmap`, optional `fgetxattr`, and `TST_EXP_FAIL(... EBADF)`. Control flow: setup creates a file, reopens it with `O_PATH`, duplicates the fd; run iterates operation wrappers against both original and duplicate descriptors and requires `EBADF`; cleanup closes fds. State/persistence: one temp file and two path-only descriptors. Dependencies/integration: `config.h` gates xattr support; lapi `fcntl.h` supplies `O_PATH` if needed. Risks: some fd-level operations may gain special `O_PATH` support in future kernels, requiring expectation updates. Test signals: pass confirms `O_PATH` fds cannot be used for data/metadata operations in the tested set.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open14.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open14.c

Purpose: functional test for `O_TMPFILE` creation, linking, multiple unlinked temp files, and access modes. Important APIs/types/functions: `open(".", O_TMPFILE|O_RDWR, mode)`, `linkat(... AT_SYMLINK_FOLLOW)` via `/proc/self/fd/<fd>`, `SAFE_MKDIR`, `SAFE_CHDIR`, `SAFE_RMDIR`, `tst_dir_is_empty`, and `umask`. Control flow: setup chdirs to mounted filesystem and checks `O_TMPFILE` support; `test01` writes and links one unnamed file, `test02` creates 100 unnamed files in nested dirs, removes dirs while fds remain open, then verifies data; `test03` links temp files with varied modes and validates permissions. State/persistence: mounted filesystem directories/files; unnamed files persist only by open fd until linked or closed. Dependencies/integration: root, all-filesystems mountpoint, procfs fd links, and filesystem `O_TMPFILE` support. Risks: unsupported filesystems produce `TCONF`; cleanup assumes current directory can move back one level. Test signals: pass confirms unnamed temp files work, remain usable after directory removal, and link with correct modes.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open14.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open15.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open/open15.c

Purpose: verify opening and using a symlink reaches the target file correctly. Important APIs/types/functions: `SAFE_TOUCH`, `SAFE_SYMLINK`, `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_READ`, `SAFE_LSEEK`, `strncmp`, and LTP expression assertions. Control flow: create target and symlink, open target read-only and symlink read/write, write a fixed string through symlink fd, read via both fds, compare target content to expected string and symlink readback to target readback, then close/unlink. State/persistence: transient target and symlink in tempdir. Dependencies/integration: symlink-capable filesystem. Risks: target fd is opened before the write but read afterward; normal shared file state makes that valid. Test signals: pass means symlink open follows to the same underlying file for read/write data visibility.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open/open15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open_by_handle_at/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open_by_handle_at/Makefile

Purpose: generic build leaf for `open_by_handle_at` tests. Important APIs/types/functions: LTP `testcases.mk` and `generic_leaf_target.mk`. Control flow: delegates target discovery/build to standard LTP make infrastructure. State/persistence: standard build artifacts only. Dependencies/integration: pairs with `name_to_handle_at` lapi helpers used by the C files. Risks: no special build flags; runtime capability/filesystem needs are encoded in test metadata. Test signals: successful build produces both open-by-handle tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open_by_handle_at/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open_by_handle_at/open_by_handle_at01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open_by_handle_at/open_by_handle_at01.c

Purpose: positive `open_by_handle_at(2)` coverage using handles obtained relative to directory fd, file fd with `AT_EMPTY_PATH`, and `AT_FDCWD`. Important APIs/types/functions: `allocate_file_handle()`, `name_to_handle_at()`, `open_by_handle_at()`, `struct file_handle`, `SAFE_FSTAT`, `AT_EMPTY_PATH`, and `AT_SYMLINK_FOLLOW`. Control flow: setup creates/chdirs into a test dir, creates files, obtains three handle buffers through different dirfd/path forms, then each testcase opens by handle with read/write modes and checks stat size or empty-path exception. State/persistence: tempdir files and kernel file handles; open fds closed in cleanup. Dependencies/integration: root and filesystem export support for file handles. Risks: the handle pointer declaration is duplicated as a tentative definition, which C accepts but is noisy and easy to misread; filesystem handle support remains the main runtime portability risk. Test signals: pass means handles resolved from different contexts reopen the expected file.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open_by_handle_at/open_by_handle_at01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open_by_handle_at/open_by_handle_at02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open_by_handle_at/open_by_handle_at02.c

Purpose: failure-mode coverage for `open_by_handle_at(2)`. Important APIs/types/functions: `struct file_handle`, high/zero handle sizes, bad address from `tst_get_bad_addr()`, `name_to_handle_at()`, `tst_cap_action()`, `CAP_DAC_READ_SEARCH`, symlink handle, and expected errors `EBADF`, `ESTALE`, `EFAULT`, `EINVAL`, `EPERM`, `ELOOP`. Control flow: setup creates a file and symlink, builds a valid file handle and a symlink handle; each case optionally drops the required capability, calls `open_by_handle_at`, restores capability, and checks failure errno. State/persistence: tempdir file/symlink and handle buffers; temporary capability state around one case. Dependencies/integration: root, capabilities framework, and handle-exporting filesystem. Risks: stale-dfd case depends on fd 0 behavior; capability drops in containerized environments may not map exactly. Test signals: pass confirms argument, capability, and symlink rejection paths.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open_by_handle_at/open_by_handle_at02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open_tree/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open_tree/Makefile

Purpose: generic LTP build leaf for `open_tree` syscall tests in this directory. Important APIs/types/functions: `top_srcdir`, `testcases.mk`, and `generic_leaf_target.mk`. Control flow: includes the common test-case and generic leaf rules with no local overrides. State/persistence: only standard build artifacts. Dependencies/integration: ties any `open_tree` C tests in the directory into the syscall suite; this work item lists only the Makefile. Risks: absence of local flags means syscall number wrappers and feature detection must come from the C files/common headers. Test signals: successful make traversal indicates the directory follows standard LTP build conventions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open_tree/Makefile -->
