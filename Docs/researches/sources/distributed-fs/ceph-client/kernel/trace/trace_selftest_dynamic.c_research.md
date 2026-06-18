# sources/distributed-fs/ceph-client/kernel/trace/trace_selftest_dynamic.c

## Purpose

`trace_selftest_dynamic.c` defines two stable noinline functions used as dynamic ftrace test targets. The complete 15-line file was read.

## Important APIs, Types, and Functions

The only functions are `DYN_FTRACE_TEST_NAME()` and `DYN_FTRACE_TEST_NAME2()`, both marked `noinline __noclone` and returning zero.

## Control Flow

There is no meaningful local control flow. Selftests call these functions after applying ftrace filters and registering callbacks.

## State and Persistence Behavior

The file owns no state. Its value is stable symbol emission for ftrace filtering.

## Dependencies and Integration Points

It includes `trace.h` for macro names and integrates with `trace_selftest.c` dynamic ftrace, recursion, regs, and graph tests.

## Risks and Edge Cases

If the compiler inlines, clones, removes, or renames these functions, dynamic ftrace selftests can fail. Architecture-specific symbol prefixes are handled by wildcard filters.

## Test Signals

Successful dynamic ftrace selftests prove both functions were emitted and filterable; symbol inspection can also confirm presence.
