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
