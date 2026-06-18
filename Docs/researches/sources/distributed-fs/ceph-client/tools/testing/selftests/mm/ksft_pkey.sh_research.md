# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_pkey.sh

## Purpose
Wrapper entry point for the MM selftest `pkey` category.

## Important APIs, types, and functions
The script runs `./run_vmtests.sh -t pkey`.

## Control flow
Delegates protection-key tests to the runner.

## State and persistence behavior
No wrapper-owned state.

## Dependencies and integration points
Requires architecture/kernel support for memory protection keys and the runner-managed binaries.

## Risks and edge cases
Unsupported architectures or disabled pkeys should be handled by the delegated target.

## Test signals
Successful `pkey` target completion.
