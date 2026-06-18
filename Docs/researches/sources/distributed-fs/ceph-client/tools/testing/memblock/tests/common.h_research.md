# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/common.h

## Purpose
`common.h` defines the shared memblock test harness contract: constants for fake memory sizing, assertion macros, basic data carriers, setup function declarations, and small inline utilities for pass reporting, top-down/bottom-up execution, and memory-content validation.

## Important APIs, Types, And Functions
Important constants are `MEM_SIZE`, `PHYS_MEM_SIZE`, `NUMA_NODES`, `INIT_MEMBLOCK_REGIONS`, and `INIT_MEMBLOCK_RESERVED_REGIONS`. `enum test_flags` controls raw allocation/content checks. `struct test_memory` wraps dummy allocated memory and `struct region` models base/size pairs. Assertion macros include equality, inequality, ordering, and byte-wise memory equality/inequality checks. Inline helpers include `region_end()`, `test_pass_pop()`, `run_top_down()`, `run_bottom_up()`, and `assert_mem_content()`.

## Control Flow
Macros call `test_fail()` before `assert()` when conditions are violated. `run_top_down()` and `run_bottom_up()` set the global memblock allocation direction, push a prefix, execute a caller-provided check function, and pop the prefix. `assert_mem_content()` chooses zeroed versus nonzero content expectations from `TEST_F_RAW`.

## State And Persistence
The header itself owns no storage, but its inline helpers mutate global memblock allocation direction through `memblock_set_bottom_up()` and mutate the prefix stack through `prefix_push()`/`prefix_pop()`.

## Dependencies And Integration Points
The header depends on Linux memblock, size, type, printk, and kselftest headers, plus libc `stdlib` and `assert`. It is the central integration point for all memblock test C files.

## Risks
Assertion macros evaluate arguments more than once only in a limited way, but callers should still avoid side effects in expected/seen expressions. `ASSERT_MEM_NE()` means every byte must differ from the expected byte; it is not a general "buffers differ" helper. Inline control-flow helpers assume the called test restores anything beyond allocation direction.

## Test Signals
The macros generate immediate abort-on-failure behavior, with optional verbose failure naming supplied by `common.c`. Build signals include whether kernel headers and kselftest headers remain compatible with this user-space harness.
