# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mdwe.sh

## Purpose
Wrapper entry point for the MM selftest `mdwe` category.

## Important APIs, types, and functions
It calls `./run_vmtests.sh -t mdwe` under `sh -e`.

## Control flow
Delegates to Memory-Deny-Write-Execute tests selected by the runner.

## State and persistence behavior
No wrapper-owned state.

## Dependencies and integration points
Requires runner and MDWE-capable kernel/test binaries.

## Risks and edge cases
Architecture or kernel support may determine skips in the delegated target.

## Test signals
Successful wrapper exit means the `mdwe` target succeeded.
