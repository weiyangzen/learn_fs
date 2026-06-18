# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_thp.sh

## Purpose
Wrapper entry point for the MM selftest `thp` category.

## Important APIs, types, and functions
The wrapper calls `./run_vmtests.sh -t thp`.

## Control flow
Delegates transparent hugepage tests, including khugepaged-related binaries, to the runner.

## State and persistence behavior
No wrapper state; underlying tests may mutate THP sysfs settings and restore them.

## Dependencies and integration points
Requires THP-capable kernel and built THP selftests.

## Risks and edge cases
THP sysfs permissions, swap availability, and filesystem support affect the delegated target.

## Test signals
Wrapper status mirrors the `thp` target.
