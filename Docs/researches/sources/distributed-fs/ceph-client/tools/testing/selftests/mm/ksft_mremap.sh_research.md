# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mremap.sh

## Purpose
Wrapper entry point for the MM selftest `mremap` category.

## Important APIs, types, and functions
Runs `./run_vmtests.sh -t mremap`.

## Control flow
Delegates mremap regression tests to the runner.

## State and persistence behavior
No wrapper-owned state.

## Dependencies and integration points
Requires runner and mremap test binaries.

## Risks and edge cases
Address-space layout and feature availability can affect delegated tests.

## Test signals
Successful runner completion for `mremap`.
