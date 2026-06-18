# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_process_mrelease.sh

## Purpose
Wrapper entry point for the MM selftest `process_mrelease` category.

## Important APIs, types, and functions
It calls `./run_vmtests.sh -t process_mrelease`.

## Control flow
Delegates to the runner's `process_mrelease(2)` test.

## State and persistence behavior
No local state.

## Dependencies and integration points
Requires kernel support for `process_mrelease` and runner-managed test binary.

## Risks and edge cases
Process lifecycle and permission behavior are handled by the delegated target.

## Test signals
Success is the `process_mrelease` target returning success.
