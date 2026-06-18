# subset-b-006854 research

Grouped research report for Linux mm selftest sources under `sources/distributed-fs/ceph-client/tools/testing/selftests/mm`. Each section is bounded by reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pagemap_ioctl.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pagemap_ioctl.c

Purpose: broad regression coverage for the `/proc/self/pagemap` `PAGEMAP_SCAN` ioctl, especially `PAGE_IS_WRITTEN` tracking with userfaultfd asynchronous write protection across anonymous, file-backed, THP, hugetlb, memfd, shmem, unmapped, mprotect, concurrent-fault, and PFN-zero cases.

Important APIs and functions: `pagemap_ioctl()` and `pagemap_ioc()` build `struct pm_scan_arg` and invoke `PAGEMAP_SCAN`; `init_uffd()`, `wp_init()`, `wp_addr_range()`, and `wp_free()` manage `UFFDIO_REGISTER` and `UFFDIO_WRITEPROTECT`; `base_tests()`, `sanity_tests_sd()`, `sanity_tests()`, `hpage_unit_tests()`, `mprotect_tests()`, `transact_test()`, `userfaultfd_tests()`, and `zeropfn_tests()` provide the individual scenarios.

Control flow: `main()` initializes userfaultfd, sets a 117-test TAP plan, opens pagemap, then runs layered suites from low-level argument validation through normal pages, large anonymous ranges, THP, hugetlb variants, file mappings, walk-end behavior, multi-threaded dirty tracking, unmapped address scans, and zero-page detection.

State and persistence: all state is per-process mappings, temporary files/memfds, SYSV shm IDs, the global `pagemap_fd` and `uffd`, and soft-dirty/write-protect metadata in the kernel. Temporary mappings are generally unregistered and unmapped, but `__FILE__.tmp0/tmp2` style files are created in the working directory and not explicitly unlinked.

Dependencies and integration: depends on recent kernel pagemap scan categories (`PAGE_IS_*`), userfaultfd WP features (`UFFD_FEATURE_WP_UNPOPULATED`, `UFFD_FEATURE_WP_ASYNC`, `UFFD_FEATURE_WP_HUGETLBFS_SHMEM`), `vm_util.h`, `kselftest.h`, hugetlb availability, THP size discovery, `/proc/self/pagemap`, and the `run_vmtests.sh` `pagemap` category.

Risks and test signals: high-signal failures are wrong return counts, malformed `page_region` ranges/categories, incorrect `walk_end`, lost concurrent updates, broken hugepage split/clear accounting, and bad `PAGE_IS_PFNZERO` classification. Skips occur if userfaultfd or hugepage prerequisites are missing; concurrency and hugepage availability can make failures environment-sensitive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pagemap_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pfnmap.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pfnmap.c

Purpose: validates core `VM_PFNMAP` behavior for mappings such as `/dev/mem`, ensuring unsupported memory-management operations fail cleanly while splitting, shrinking, moving, and forking mappings remain safe.

Important APIs and functions: `find_ram_target()` parses `/proc/iomem` for a two-page System RAM range; `pfnmap_init()` opens and probes the target file; `test_read_access()` traps `SIGSEGV` with `sigsetjmp`; fixture tests cover disallowed `madvise()`, `munmap()` splits, fixed `mremap()`, shrink/expand behavior, and child access after `fork()`.

Control flow: `main()` optionally accepts an alternate file after `--`, initializes the global fd/offset, then runs the kselftest harness with a fresh mapping per fixture. Setup maps two read-only shared pages, teardown unmaps any secondary mapping.

State and persistence: state is process-local except for the open file descriptor and selected physical/file offset. The test does not modify mapped memory and leaves no files, but it can observe real physical memory through `/dev/mem`.

Dependencies and integration: depends on `kselftest_harness.h`, `vm_util.h` `check_vmflag_pfnmap()`, `/proc/iomem`, `/dev/mem` or a compatible user-supplied PFNMAP file, and privilege/kernel policy that permits mapping and reading the target.

Risks and test signals: expected signals are `EINVAL` for forbidden `madvise()` commands, successful remap/split/fork reads, and failed growth by `mremap()`. The suite commonly skips when `/proc/iomem` hides addresses, `/dev/mem` access is restricted, or the supplied file is not PFNMAP-backed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pfnmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-arm64.h -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-arm64.h

Purpose: supplies arm64-specific protection-key definitions for the generic pkey selftests, mapping Linux pkey operations onto Permission Overlay Extension state in `POR_EL0`.

Important APIs and types: defines syscall numbers, `NR_PKEYS`, `PKEY_MASK`, POE permission encodings, `PKEY_REG_ALLOW_ALL/NONE`, page/hugepage sizing, `__read_pkey_reg()`, `__write_pkey_reg()`, `pkey_bit_position()`, arm64-specific `set_pkey_bits()` and `get_pkey_bits()`, and `aarch64_write_signal_pkey()` for signal frame updates.

Control flow: included by `pkey-helpers.h` on `__aarch64__`; the generic tests call these static inline helpers whenever they read/write pkey register state, inspect CPU support, or repair a signal context after a pkey fault.

State and persistence: no standalone state; it directly reads/writes the per-thread `POR_EL0` register and may mutate the POE context embedded in a signal frame.

Dependencies and integration: depends on `vm_util.h`, arm64 signal test context helpers, Linux `NT_ARM_POE` ptrace handling in `protection_keys.c`, and kernel support for arm64 pkeys/POE.

Risks and test signals: key risks are mismatched POE encodings, signal-frame parsing changes, and the simplified `cpu_has_pkeys()` always returning true. Successful tests indirectly prove register writes, signal recovery, and ptrace-visible POE state behave as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-arm64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-helpers.h -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-helpers.h

Purpose: generic support header for the pkey selftests, providing shared types, debug output, assertion behavior, shadow-register verification, syscall prototypes, alignment helpers, and architecture dispatch.

Important APIs and types: defines `u8/u16/u32/u64`, `PTR_ERR_ENOTSUP`, `sigsafe_printf()`, `dprintf0..4`, `pkey_assert()`, `barrier()`, prototypes for `sys_pkey_alloc/free`, `sys_mprotect_pkey()`, `read_ptr()`, `expected_pkey_fault()`, `mprotect_pkey()`, and `record_pkey_malloc()`, plus generic `set_pkey_bits()`, `get_pkey_bits()`, `read_pkey_reg()`, and `write_pkey_reg()`.

Control flow: architecture headers are included based on compiler target, then generic helpers wrap architecture-specific register access. Tests use `read_pkey_reg()` to assert the hardware register equals `shadow_pkey_reg`, while lower-level `__read_pkey_reg()` bypasses that check in signal paths.

State and persistence: declares external `shadow_pkey_reg`, `test_nr`, `iteration_nr`, and `dprint_in_signal`; no persistent resources are created.

Dependencies and integration: depends on `kselftest.h`, Linux pkey constants, `ucontext.h`, and one of `pkey-x86.h`, `pkey-powerpc.h`, or `pkey-arm64.h`. It is shared by `protection_keys.c`, `pkey_sighandler_tests.c`, and `pkey_util.c`.

Risks and test signals: the shadow-register assertion is a strong invariant but can fail if signal handlers or ptrace intentionally change register state without updating shadow state. `pkey_assert()` exits with line-number status, making failures precise but abrupt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-powerpc.h -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-powerpc.h

Purpose: provides powerpc64-specific protection-key register, permission, page-size, and reserved-key behavior for the generic pkey selftests.

Important APIs and functions: defines AMR access through `mfspr/mtspr 0xd`, `PKEY_DISABLE_ACCESS` and `PKEY_DISABLE_WRITE` encodings, `NR_PKEYS`, reserved-key counts for 4K, PowerNV/KVM 64K, and PowerVM, `arch_is_powervm()`, `get_arch_reserved_keys()`, no-op generation macros, and a powerpc-only `malloc_pkey_with_mprotect_subpage()` that probes `__NR_subpage_prot`.

Control flow: included via `pkey-helpers.h`; generic tests call its inline register helpers, key-bit positioning, execute-only expectations, and optional subpage allocator as one of the allocation backends.

State and persistence: no global state. It reads firmware/device-tree paths to infer PowerVM and writes the per-thread AMR register.

Dependencies and integration: depends on powerpc `ucontext` register layout, syscall numbers for pkeys and subpage protection, `/sys/firmware/devicetree` markers, and the generic test allocator table in `protection_keys.c`.

Risks and test signals: reserved-key math varies by page size and platform, so bad detection can make allocation-exhaustion expectations wrong. Execute-only read faults are intentionally not asserted because userspace cannot restore exec-only key permissions without looping on faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-powerpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-x86.h -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-x86.h

Purpose: x86 and i386 support layer for the generic pkey tests, centered on PKRU register access, XSAVE layout discovery, signal context offsets, and CPUID feature detection.

Important APIs and functions: defines `REG_IP_IDX`, `si_pkey_offset`, `MCONTEXT_*`, `NR_PKEYS`, `PKEY_BITS_PER_PKEY`, `HPAGE_SIZE`, `PAGE_SIZE`, `__read_pkey_reg()`/`__write_pkey_reg()` using RDPKRU/WRPKRU opcodes, `cpu_has_pkeys()`, `cpu_max_xsave_size()`, `pkey_reg_xstate_offset()`, and `expect_fault_on_read_execonly_key()`.

Control flow: included by `pkey-helpers.h` on x86 targets. The main tests use CPUID checks before running, signal handlers use the XSAVE offset to clear PKRU in the saved context, and ptrace tests use the same offsets with `NT_X86_XSTATE`.

State and persistence: no persistent resources; operations mutate the per-thread PKRU and inspect XSAVE state.

Dependencies and integration: requires compiler support for `__cpuid_count` and, for some paths in `protection_keys.c`, XSAVE builtins compiled with suitable flags. Integrates with execute-only memory behavior that consumes a reserved pkey.

Risks and test signals: failures usually indicate missing PKU/OSPKE, bad XSAVE offset handling, or incorrect signal/ptrace PKRU save-restore behavior. The hardcoded si_pkey offsets are sensitive to ABI layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-x86.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey_sighandler_tests.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey_sighandler_tests.c

Purpose: exercises Linux signal delivery and return behavior when pkey 0, which normally protects the process stack and libraries, is disabled or when alternate stacks use different pkeys.

Important APIs and functions: `syscall_raw()` and `clone_raw()` avoid glibc when pkey 0 is inaccessible; `pkey_reg_restrictive_default()` builds restrictive register state; handlers record `siginfo`; tests cover SIGSEGV with pkey 0 disabled, inaccessible stacks, alternate-stack delivery with pkey 1, PKRU/POR preservation after SIGUSR1, and sigreturn from an altstack with pkey 2.

Control flow: `main()` prints TAP, skips without pkey support, then runs five function-pointer tests. Some tests use detached pthreads; others use raw `clone()` to avoid glibc rseq and stack assumptions.

State and persistence: shared state is a mutex/condition variable and global `siginfo`. Mappings for custom stacks and altstacks are process-local; test threads exit through raw syscalls in paths where returning would touch inaccessible stacks.

Dependencies and integration: depends on `pkey-helpers.h`, architecture raw syscall implementations, `pthread`, `sigaltstack`, pkey syscalls, and kselftest TAP. It complements `protection_keys.c` by focusing specifically on signal ABI behavior.

Risks and test signals: passing signals prove handlers run with a safe initial pkey register and sigreturn restores application state. Fragility comes from architecture syscall calling conventions, glibc behavior if raw syscalls are accidentally bypassed, and subtle stack accessibility assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey_sighandler_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey_util.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey_util.c

Purpose: small syscall wrapper translation unit for pkey selftests, isolating direct kernel calls behind names used by shared helpers.

Important APIs and functions: `sys_pkey_alloc()` calls `SYS_pkey_alloc`; `sys_pkey_free()` calls `SYS_pkey_free`; `sys_mprotect_pkey()` calls `__NR_pkey_mprotect`, clears `errno` first, logs details through `dprintf`, and returns the raw syscall result.

Control flow: no standalone entrypoint. The wrappers are linked into pkey binaries and called by `protection_keys.c`, `pkey_sighandler_tests.c`, and helper routines.

State and persistence: no persistent state; effects are kernel pkey allocation/freeing and VMA pkey protection changes requested by callers.

Dependencies and integration: depends on `pkey-helpers.h`, syscall number definitions from libc/kernel headers or architecture headers, and Linux pkey syscall support.

Risks and test signals: wrappers deliberately preserve syscall-style errors so callers can distinguish unsupported pkeys, invalid keys, and permission failures. Any syscall-number mismatch would make all higher-level pkey tests fail or skip incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/prctl_thp_disable.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/prctl_thp_disable.c

Purpose: verifies `PR_SET_THP_DISABLE` and `PR_GET_THP_DISABLE`, including the `PR_THP_DISABLE_EXCEPT_ADVISED` mode, against global THP policies and fork inheritance.

Important APIs and functions: `test_mmap_thp()` allocates a PMD-aligned anonymous range, applies optional `MADV_NOHUGEPAGE`, `MADV_HUGEPAGE`, or `MADV_COLLAPSE`, faults pages, and checks `AnonHugePages`; fixture helpers set process prctl state and temporary sysfs THP policy through `thp_settings`.

Control flow: two fixtures run across `never`, `madvise`, and `always` global policy variants. Each fixture has `nofork` and `fork` tests, proving behavior in the current process and inherited child process.

State and persistence: modifies process prctl state and global THP sysfs settings. `thp_save_settings()`/`thp_restore_settings()` bracket each fixture, but interrupted runs could leave sysfs state changed.

Dependencies and integration: depends on THP availability, PMD size discovery, `MADV_COLLAPSE`, `kselftest_harness.h`, `thp_settings.c`, and `vm_util.h`. Integrated under the `thp` selftest category.

Risks and test signals: expected results distinguish full disable, advised-only disable, and restored global behavior. Failures indicate broken prctl value reporting, incorrect override precedence, or missing fork inheritance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/prctl_thp_disable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/process_madv.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/process_madv.c

Purpose: validates `process_madvise(2)` behavior for self-targeted non-contiguous ranges, remote `MADV_COLLAPSE`, exited pidfds, bad pidfds, invalid vector lengths, and invalid flags.

Important APIs and functions: `sys_process_madvise()` wraps `__NR_process_madvise`; the fixture tracks `PIDFD_SELF`, child PID, and remote pidfd. Tests use `mmap()`, `pidfd_open`, pipes for child address handoff, `MADV_DONTNEED`, and `MADV_COLLAPSE`.

Control flow: each harness test allocates or forks as needed. Parent teardown kills any live child and closes pidfds. The remote collapse test forks a child that faults a hugepage-sized region, sends its address, then pauses while the parent advises it.

State and persistence: all mappings and pidfds are transient. Child processes are cleaned in fixture teardown, and no files are created.

Dependencies and integration: depends on `kselftest_harness.h`, `vm_util.h`, pidfd helpers, kernel support for `process_madvise`, permissions for remote advising, and PMD-size THP support for collapse coverage.

Risks and test signals: success is exact byte counts for advised ranges and expected `ESRCH`, `EBADF`, or `EINVAL` errors. The basic test may skip on `EPERM` or unsupported syscall behavior; remote collapse checks only return semantics, not final hugepage formation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/process_madv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/protection_keys.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/protection_keys.c

Purpose: comprehensive pkey stress/regression test covering memory protection key allocation, VMA assignment, register permission updates, signal recovery, kernel accesses, ptrace, execute-only memory, THP/hugetlb allocations, and unsupported-CPU behavior.

Important APIs and functions: low-level helpers manage tracing, `hw_pkey_get/set()`, `pkey_disable_set/clear()`, SIGSEGV recovery, `alloc_pkey()`, randomized allocation churn, `mprotect_pkey()`, pkey-aware allocation backends, and expected-fault accounting. The `pkey_tests[]` table covers user reads/writes, kernel `read()`, `vmsplice`, futex/GUP paths, syscall error paths, allocation exhaustion, pkey 0 behavior, ptrace data access, and architecture-specific register ptrace modification.

Control flow: `main()` checks pkey support, runs an unsupported-path probe if absent, initializes the shadow register, optionally configures hugetlb pages, then executes all table tests for 22 iterations with a random pkey and rotating allocation backend each time.

State and persistence: important state includes `shadow_pkey_reg`, fault counters, last siginfo pkey, malloc records, test fds, optional ftrace state, hugetlb sysfs changes, child processes, and per-thread pkey registers. Most resources are cleaned per test, but aborts can leave tracing or hugetlb settings requiring manual recovery.

Dependencies and integration: depends on `pkey-helpers.h`, architecture headers, `pkey_util.c`, pkey syscalls, signals, ptrace, futex, vmsplice, hugetlb sysfs, `/etc/passwd` as a readable fd source, and optional root for tracing/hugetlb setup.

Risks and test signals: pass signals are exact pkey-fault counts, siginfo pkey matches, shadow/hardware register consistency, expected syscall failures, and child ptrace observations. It is sensitive to ABI register layouts, execute-only pkey reservation, signal-frame semantics, and root/hugetlb availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/protection_keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/rmap.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/rmap.c

Purpose: reverse-map functional test ensuring page migration of a shared physical page remains visible through a randomly generated process tree for anonymous, POSIX shm, regular file, and KSM-merged mappings.

Important APIs and functions: `propagate_children()` builds a multi-level fork tree and chooses one worker; `try_to_move_page()` uses `move_pages()` with `MPOL_MF_MOVE_ALL`; `move_region()` records the post-migration PFN from pagemap; `has_same_pfn()` validates other processes see the expected PFN; KSM paths use `ksm_start()` and `PR_SET_MEMORY_MERGE`.

Control flow: fixture setup requires NUMA with more than one node, initializes a shared expected-PFN word, semaphore, pipe, random seed, and worker level. Each test configures mapping backend and callbacks, then calls `propagate_children()`.

State and persistence: state spans a process tree, SYSV semaphore, pipe, shared expected-PFN mapping, temp shm/file names, KSM sysfs state, and page migration state. Teardown unmaps regions, removes semaphores, closes pipe ends, and unlinks backing files.

Dependencies and integration: depends on libnuma, `/proc/self/pagemap`, `move_pages(2)`, KSM helpers in `vm_util.h`, POSIX shm, regular files, and sufficient NUMA privileges/capabilities.

Risks and test signals: failures differentiate worker migration failure from checker PFN mismatch. Migration is best-effort and retried, so environment pressure, NUMA policy, missing permissions, or KSM timing can make this suite skip or fail outside suitable hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/rmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/run_vmtests.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/run_vmtests.sh

Purpose: top-level shell orchestrator for mm selftests, providing category selection, TAP output, hugepage preparation/restoration, optional destructive testing, and sequential execution of C binaries and wrapper scripts.

Important APIs and functions: `usage()` documents categories; `test_selected()` filters categories; `run_gup_matrix()` expands GUP combinations; `run_test()` prints banners, performs THP/hugetlb cleanup/compaction, captures exit status, counts pass/skip/fail, and emits TAP lines; helper functions add TAP prefixes and friendly names.

Control flow: parses `-a`, `-t`, `-n`, and intended `-d` options, computes hugepage needs from `/proc/meminfo`, tries to reserve hugetlb pages, detects 64-bit address support, then runs all selected categories in a fixed order. It temporarily creates XFS loopback storage for `split_huge_page_test` when possible and restores hugepage counts at the end.

State and persistence: writes `/proc/sys/vm/nr_hugepages`, `drop_caches`, `compact_memory`, `shmmax`, `shmall`, Yama ptrace scope, optional hwpoison module state, and temporary XFS image/mount. Cleanup restores many values, but abnormal exits can leave system state altered.

Dependencies and integration: depends on root for many categories, compiled selftest binaries, module tools, shell utilities, xfs tooling, kernel modules, and TAP/kselftest skip code semantics. It integrates every listed file through categories such as `pkey`, `soft_dirty`, `pagemap`, `pfnmap`, `process_madv`, `thp`, `hugetlb`, `page_frag`, `vmalloc`, `hmm`, and `rmap`.

Risks and test signals: summary counts and TAP output are the primary signals. Risk is high because the runner mutates global kernel knobs and has a likely option-string bug: `getopts "aht:n"` omits `d` even though destructive mode is documented and handled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/run_vmtests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/soft-dirty.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/soft-dirty.c

Purpose: tests classic pagemap soft-dirty bit semantics for normal pages, VMA reuse, THP, mprotect transitions, file mappings, and VMA merge propagation.

Important APIs and functions: `test_simple()` loops clear/write/observe for 10,000 iterations; `test_vma_reuse()` checks newly allocated or reused VMAs are marked soft-dirty; `test_hugepage()` validates THP soft-dirty behavior; `test_mprotect()` covers anonymous and shared file mappings; `test_merge()` constructs VMA merge scenarios via `mmap()`, `mremap()`, and `mprotect()`.

Control flow: `main()` skips if soft-dirty is unsupported, opens `/proc/self/pagemap`, sets a 19-test TAP plan, and runs each scenario in sequence before closing pagemap.

State and persistence: state is process-local mappings and `/proc/self/clear_refs` effects via `clear_softdirty()`. A temporary file named `soft-dirty-test-file` is created, unlinked immediately, and closed after mapping.

Dependencies and integration: depends on `vm_util.h` helpers such as `softdirty_supported()`, `clear_softdirty()`, and `pagemap_is_softdirty()`, plus `thp_settings.h` for THP availability.

Risks and test signals: failures indicate stale or missing pagemap soft-dirty bits, incorrect VMA-level `VM_SOFTDIRTY` propagation across merge operations, or THP soft-dirty regressions. THP subtests skip when hugepages cannot be allocated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/soft-dirty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/split_huge_page_test.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/split_huge_page_test.c

Purpose: validates debugfs-triggered splitting of PMD THPs, PTE-mapped THPs, file-backed THPs, and large pagecache folios into requested lower orders without data corruption.

Important APIs and functions: `write_debugfs()` writes formatted split requests to `/sys/kernel/debug/split_huge_pages`; `is_backed_by_folio()`, `gather_after_split_folio_orders()`, and `check_after_split_folio_orders()` inspect `/proc/self/pagemap` and `/proc/kpageflags`; split routines cover zero-filled anonymous THPs, arbitrary target orders, PTE-mapped remapped pages, tmpfs file-backed THPs, and pagecache THPs with optional in-folio offset.

Control flow: `main()` requires root and THP, initializes page/PMD sizes and expected-order arrays, opens pagemap/kpageflags, runs all anonymous/file/pagecache split cases, optionally uses a supplied XFS path or temporary directory, then cleans resources.

State and persistence: uses debugfs, temporary tmpfs mounts, optional XFS path, files under `/tmp`, `/proc/sys/vm/drop_caches`, and global fd state. Cleanup unmounts and unlinks on normal paths; failure exits may leave mounts or temp files.

Dependencies and integration: depends on root, THP, debugfs split interface, pagemap PFN visibility, kpageflags, tmpfs `huge=always`, a filesystem that supports large pagecache folios, `vm_util.h`, and `thp_settings.h`.

Risks and test signals: strong signals are preserved byte patterns, expected folio-order histograms, absence of `AnonHugePages`/`FilePmdMapped`, and RSS decrease for zero-filled splits. Risks include privileged interfaces, filesystem support variability, and pageflag interpretation changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/split_huge_page_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/test_hmm.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/test_hmm.sh

Purpose: wrapper script for HMM selftests that loads the `test_hmm` kernel module, runs the `hmm-tests` binary, and unloads the module.

Important APIs and functions: `check_test_requirements()` enforces root, `modprobe`, and `CONFIG_TEST_HMM=m`; `load_driver()` optionally passes `spm_addr_dev0` and `spm_addr_dev1`; `run_smoke()` runs the smoke path; `usage()` documents supported invocations.

Control flow: after requirements pass, `run_test()` accepts only `smoke` with optional SPM addresses. It loads the module, invokes `$(dirname "$BASH_SOURCE")/hmm-tests`, unloads the module, and exits 0 unless requirement checks skip/fail.

State and persistence: transient module load state is the only external state; normal flow unloads with `modprobe -r`.

Dependencies and integration: depends on root, module tools, `test_hmm` module availability, the compiled `hmm-tests` binary, and `run_vmtests.sh` category `hmm`.

Risks and test signals: output is minimal and the script does not propagate the `hmm-tests` status explicitly because the final command path reaches `exit 0`; failures may only be visible in the child command output or module load failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/test_hmm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/test_page_frag.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/test_page_frag.sh

Purpose: wrapper for the page fragment allocator kernel-module selftest, providing smoke and performance parameter presets plus manual module-parameter validation.

Important APIs and functions: CPU selection derives two test CPUs from `/proc/cpuinfo`; presets are `SMOKE_PARAM`, `NONALIGNED_PARAM`, and `ALIGNED_PARAM`; `check_test_requirements()` validates root, `insmod`, and `./page_frag/page_frag_test.ko`; `validate_passed_args()` checks keys against `modinfo`; `check_test_failed_prefix()` scans dmesg for the module failure prefix.

Control flow: accepts `smoke`, `nonaligned`, `aligned`, or manual parameters. It inserts the module with selected arguments, scans dmesg for `"page_frag_test failed:"`, then prints completion guidance.

State and persistence: loads a test module by path and relies on kernel logs for results. The script does not explicitly remove the module after insertion, so module persistence depends on the module/test behavior or later cleanup.

Dependencies and integration: depends on root, built page_frag test module, `modinfo`, `insmod`, readable dmesg, and the `page_frag` category in `run_vmtests.sh`.

Risks and test signals: pass/fail detection is dmesg-string based and can miss failures if log access is restricted or old failure lines remain. Workload size scales down on single-CPU systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/test_page_frag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/test_vmalloc.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/test_vmalloc.sh

Purpose: wrapper for the `test_vmalloc` kernel module, exposing smoke, performance, stress, and manual parameter modes for vmalloc allocator testing.

Important APIs and functions: preset parameter groups include `PERF_PARAM`, `SMOKE_PARAM`, `STRESS_PARAM`, and `PCPU_OBJ_PARAM`; `check_memory_requirement()` caps per-CPU object count to 90 percent of available memory per CPU; `validate_passed_args()` verifies manual keys and positive values against `modinfo`; run helpers call `modprobe test_vmalloc`.

Control flow: requires root, `modprobe`, and `CONFIG_TEST_VMALLOC=m`, then dispatches based on the first argument. `run_vmtests.sh` invokes `bash ./test_vmalloc.sh smoke`.

State and persistence: loads the `test_vmalloc` module with parameters and writes results to kernel logs. The script does not explicitly unload the module after running.

Dependencies and integration: depends on root, module tools, online CPU count, `getconf`, module parameters exposed by `test_vmalloc`, and dmesg for detailed summaries.

Risks and test signals: script exit status mainly reflects argument/module setup, not a parsed kernel pass/fail line. Memory-capping reduces OOM risk but stress/performance modes still consume substantial vmalloc/percpu resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/test_vmalloc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/thp_settings.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/thp_settings.c

Purpose: shared utility implementation for reading, writing, saving, restoring, and stacking transparent hugepage sysfs settings used by THP-related selftests.

Important APIs and functions: file helpers `read_file()`, `read_num()`, `write_num()`; THP sysfs wrappers `thp_read_string()`, `thp_write_string()`, `thp_read_num()`, `thp_write_num()`; state APIs `thp_read_settings()`, `thp_write_settings()`, `thp_save_settings()`, `thp_restore_settings()`, `thp_push_settings()`, `thp_pop_settings()`; supported-order detection for anon and shmem; availability/enabled checks.

Control flow: settings reads parse bracketed active values from `/sys/kernel/mm/transparent_hugepage/*`, including per-order `hugepages-*kB` directories and khugepaged tunables. Writes mirror the stored struct back to sysfs.

State and persistence: maintains static `saved_settings`, a small settings stack, and optional device read-ahead path. It mutates global kernel THP sysfs state and optional block read-ahead state, so restoration is critical.

Dependencies and integration: depends on `vm_util.h` `write_file()`, Linux THP sysfs layout, `getpagesize()`, and `thp_settings.h`. Used by many THP tests including `prctl_thp_disable.c`, `soft-dirty.c`, split tests, and stress tools.

Risks and test signals: parsing assumes bracketed current values and fixed enum string ordering. Unsupported per-order directories are represented as disabled. Abrupt exits after writes can leave host THP settings changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/thp_settings.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/thp_settings.h -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/thp_settings.h

Purpose: declares the shared transparent hugepage settings model and helper API used by mm selftests that need to inspect or temporarily modify THP policy.

Important APIs and types: enums model anon THP policy (`THP_NEVER`, `THP_ALWAYS`, `THP_INHERIT`, `THP_MADVISE`), defrag policy, and shmem policy. Structs include `hugepages_settings`, `khugepaged_settings`, `shmem_hugepages_settings`, and aggregate `thp_settings` with per-order arrays sized by `NR_ORDERS`.

Control flow: no executable flow; consumers include this header and link `thp_settings.c` to call read/write/save/restore/stack APIs and supported-order queries.

State and persistence: the header defines only data shapes and prototypes; persistent effects are implemented in `thp_settings.c`.

Dependencies and integration: depends on standard bool/size/integer headers. It is a central integration point for THP tests, making sysfs THP state changes structured instead of open-coded.

Risks and test signals: enum ordering must remain aligned with string arrays in `thp_settings.c` and sysfs accepted values. `NR_ORDERS` bounds how many page-size orders can be represented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/thp_settings.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/thuge-gen.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/thuge-gen.c

Purpose: tests explicit hugepage size selection for `mmap(MAP_HUGETLB | MAP_HUGE_*)` and `shmget(SHM_HUGETLB | SHM_HUGE_*)` across available hugepage sizes.

Important APIs and functions: `find_pagesizes()` globs `/sys/kernel/mm/hugepages/hugepages-*kB`, checks free page counts and `shmmax`; `test_mmap()` maps, writes, and validates hugepage consumption; `test_shmget()` creates, attaches, writes, marks for removal, and validates consumption; `ilog2()` builds shift arguments.

Control flow: `main()` discovers usable sizes, sets TAP plan, tests each explicit mmap size, default huge mmap, non-huge shm, each explicit shm size, and default huge shm.

State and persistence: consumes reserved hugetlb pages temporarily, creates SYSV shm segments marked `IPC_RMID`, and reads sysfs/proc knobs. It does not reserve hugepages itself.

Dependencies and integration: depends on pre-reserved hugepages, sufficient `/proc/sys/kernel/shmmax`, root for some shm behavior, `vm_util.h`, `kselftest.h`, and `run_vmtests.sh` hugetlb category.

Risks and test signals: pass criteria compare free hugepage counts before and after touching mappings. The suite skips on insufficient hugepages or, on x86-64, absence of 1GB pages; parallel hugepage users can make counts unstable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/thuge-gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/transhuge-stress.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mm/transhuge-stress.c

Purpose: long-running transparent hugepage stress tool that repeatedly allocates THPs, records physical distribution, and splits most of each THP with `MADV_DONTNEED` to exercise compaction, allocation, and migration paths.

Important APIs and functions: `main()` parses optional `-f` backing file, `-d` duration, and size MiB; uses `allocate_transhuge()` from `vm_util.h`, `/proc/self/pagemap`, `MADV_HUGEPAGE`, and a PFN-index bitmap to count distinct hugepage frames.

Control flow: after THP availability and mapping setup, an infinite loop touches each hugepage-sized chunk, records successes/failures, discards all but the last base page of each THP, prints throughput and counts, and exits successfully only when a positive duration has elapsed.

State and persistence: state is a large virtual mapping, optional shared file mapping, pagemap fd, dynamically resized bitmap, and elapsed time. Without `-d`, it intentionally runs forever.

Dependencies and integration: depends on THP policy, physical memory, pagemap access, `vm_util.h`, and `thp_settings.h`. `run_vmtests.sh` invokes it as `./transhuge-stress -d 20`.

Risks and test signals: useful signals are throughput, succeed/failed counts, and distinct page counts. It can create heavy memory pressure; file-backed mode depends on a prepared writable file large enough for the mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/transhuge-stress.c -->
