# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_ksm_numa.sh

## Purpose
Wrapper entry point for the MM selftest `ksm_numa` category.

## Important APIs, types, and functions
The script calls `./run_vmtests.sh -t ksm_numa`.

## Control flow
Delegates to the runner's NUMA-aware KSM tests, including `ksm_tests -N` modes in the runner.

## State and persistence behavior
No wrapper-owned state; delegated tests can affect KSM sysfs state.

## Dependencies and integration points
Requires NUMA/KSM support for full coverage and the runner in the current directory.

## Risks and edge cases
On non-NUMA or restricted systems the underlying target may skip or fail.

## Test signals
The script passes when the `ksm_numa` target passes.
