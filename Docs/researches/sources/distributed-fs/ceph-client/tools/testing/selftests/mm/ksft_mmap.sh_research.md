# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mmap.sh

## Purpose
Wrapper entry point for the MM selftest `mmap` category.

## Important APIs, types, and functions
The script invokes `./run_vmtests.sh -t mmap`.

## Control flow
Delegates mmap-related selftests to the runner.

## State and persistence behavior
No wrapper-owned state.

## Dependencies and integration points
Requires runner and mmap test binaries.

## Risks and edge cases
Underlying tests may depend on architecture, permissions, or vm sysctls.

## Test signals
Exit status mirrors the runner's `mmap` target.
