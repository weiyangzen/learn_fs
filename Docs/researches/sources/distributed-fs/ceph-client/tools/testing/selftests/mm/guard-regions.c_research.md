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
