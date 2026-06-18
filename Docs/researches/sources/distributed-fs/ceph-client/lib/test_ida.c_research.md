
# sources/distributed-fs/ceph-client/lib/test_ida.c

## Purpose

This module exercises the IDA allocator API across allocation, free, destroy, maximum id, internal representation conversion, bad frees, and first-used-id queries.

## Important APIs, Types, And Functions

It uses a global `DEFINE_IDA(ida)` plus `tests_run` and `tests_passed`. `IDA_BUG_ON()` records assertions and dumps state/stack on failure. Test functions cover `ida_alloc()`, `ida_alloc_min()`, `ida_free()`, `ida_destroy()`, `ida_is_empty()`, `ida_exists()`, `ida_find_first()`, and `ida_find_first_range()`.

## Control Flow And State

`ida_checks()` runs all test groups during module init and prints the pass count. Each group leaves the IDA empty before the next group. The return convention is unusual: it returns `0` if any test failed and `-EINVAL` when all tests passed, causing a successful selftest to fail module insertion by design.

## Dependencies And Integration Points

It depends on `linux/idr.h`, module infrastructure, stack dumping, and kernel logging. It is a self-contained kernel API regression test.

## Risks And Test Signals

The intentional bad-free section emits expected "not allocated" warnings bracketed by log markers. Key signals are the final `IDA: X of X tests passed` line, any stack dump from `IDA_BUG_ON`, and the init return behavior that must be interpreted as a test harness convention.
