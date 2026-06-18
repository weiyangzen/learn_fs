# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_kern_overflow.c

## Purpose
Ensures a lightweight skeleton with overflowing or invalid kernel CO-RE relocation fails to open/load.

## Important APIs, types, and functions
Uses `core_kern_overflow.lskel.h` and `ASSERT_NULL()` around `core_kern_overflow_lskel__open_and_load()`.

## Control flow and state
There is no long-lived state. If an unexpected skeleton is returned, it is destroyed after the assertion.

## Dependencies and integration points
Depends on generated lskel and verifier/libbpf relocation rejection. Integrated through `test_core_kern_overflow_lskel()`.

## Risks and test signals
The main signal is negative: open/load must return NULL. A successful load would indicate lost overflow validation.
