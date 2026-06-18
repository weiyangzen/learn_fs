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
