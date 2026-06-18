# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_page_frag.sh

## Purpose
Wrapper entry point for the MM selftest `page_frag` category.

## Important APIs, types, and functions
The script calls `./run_vmtests.sh -t page_frag`.

## Control flow
Delegates page-fragment tests to the runner.

## State and persistence behavior
No local state.

## Dependencies and integration points
Requires runner and page-fragment selftest binary.

## Risks and edge cases
Kernel configuration may determine whether the delegated test exists or skips.

## Test signals
Pass/fail mirrors the `page_frag` target.
