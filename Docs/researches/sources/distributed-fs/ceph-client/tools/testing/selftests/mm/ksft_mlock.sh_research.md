# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mlock.sh

## Purpose
Wrapper entry point for the MM selftest `mlock` category.

## Important APIs, types, and functions
Runs `./run_vmtests.sh -t mlock` using shell exit-on-error.

## Control flow
Delegates locked-memory test execution to the runner.

## State and persistence behavior
No wrapper-owned state.

## Dependencies and integration points
Requires runner and mlock-related test binaries; underlying tests may depend on `RLIMIT_MEMLOCK`.

## Risks and edge cases
Memory-lock limits and privileges affect delegated results.

## Test signals
The wrapper succeeds if the `mlock` target succeeds.
