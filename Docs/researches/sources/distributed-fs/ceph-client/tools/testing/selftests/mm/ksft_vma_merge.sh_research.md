# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_vma_merge.sh

## Purpose
Wrapper entry point for the MM selftest `vma_merge` category.

## Important APIs, types, and functions
The script calls `./run_vmtests.sh -t vma_merge`.

## Control flow
Delegates VMA merge regression tests to the runner.

## State and persistence behavior
No local state.

## Dependencies and integration points
Requires runner and merge test binary.

## Risks and edge cases
VMA layout and filesystem-specific mmap behavior can affect delegated tests.

## Test signals
Pass/fail follows the `vma_merge` target.
