# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_rmap.sh

## Purpose
Wrapper entry point for the MM selftest `rmap` category.

## Important APIs, types, and functions
Runs `./run_vmtests.sh -t rmap`.

## Control flow
Delegates reverse-map tests to the runner.

## State and persistence behavior
No wrapper state.

## Dependencies and integration points
Requires runner and rmap test binaries/configuration.

## Risks and edge cases
Underlying tests may be kernel-config dependent.

## Test signals
The wrapper passes when the `rmap` target passes.
