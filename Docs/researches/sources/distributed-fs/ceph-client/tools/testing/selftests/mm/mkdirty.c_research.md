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
