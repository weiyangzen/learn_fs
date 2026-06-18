# sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3.c

## Purpose

`clone3.c` is the general clone3 syscall ABI selftest. It validates basic clone creation, argument size compatibility, excess argument rejection, exit signal validation, PID/time namespace flags, and rejection of legacy signal bits in `flags`. The complete 342-line file was read.

## Important APIs, Types, and Functions

Important types are `enum test_mode`, `filter_function`, `size_function`, and `struct test`. Helpers include `call_clone3()`, `test_clone3()`, `not_root()`, `no_timenamespace()`, and `page_size_plus_8()`.

## Control Flow

`main()` prints the kselftest header, declares a plan, verifies clone3 support, then iterates `tests[]`. Each row may skip through a filter, compute a dynamic size, call `sys_clone3()`, wait for the child when one is created, and compare the result to an expected errno or success.

## State and Persistence Behavior

It creates short-lived child processes and optional PID/time namespaces. There is no file persistence.

## Dependencies and Integration Points

It depends on clone3 syscall support, local `clone3_selftests.h`, kselftest helpers, root for PID/time namespace cases, and `/proc/self/ns/time` for time namespace availability.

## Risks and Edge Cases

Results depend on the running kernel's clone3 feature set and namespace permission policy. Tests with larger-than-struct arguments depend on zeroed vs nonzero excess bytes. Running inside nested PID namespaces can alter some expectations.

## Test Signals

Pass signals are exact expected return codes for each table row and successful wait/reap for child-creating clone3 calls.
