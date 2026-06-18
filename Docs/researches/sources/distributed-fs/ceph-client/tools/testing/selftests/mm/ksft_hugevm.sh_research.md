# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_hugevm.sh

## Purpose
Wrapper entry point for the MM selftest `hugevm` category.

## Important APIs, types, and functions
The wrapper calls `./run_vmtests.sh -t hugevm`.

## Control flow
No local branching exists; execution is delegated to the VM test runner.

## State and persistence behavior
No wrapper-owned state.

## Dependencies and integration points
Requires the runner and huge virtual memory tests it selects.

## Risks and edge cases
Large virtual-memory tests may be environment-sensitive; the wrapper provides no guard beyond the runner.

## Test signals
Successful completion of `run_vmtests.sh -t hugevm`.
