# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_pfnmap.sh

## Purpose
Wrapper entry point for the MM selftest `pfnmap` category.

## Important APIs, types, and functions
The script delegates with `./run_vmtests.sh -t pfnmap`.

## Control flow
No local control flow beyond runner invocation.

## State and persistence behavior
No local state.

## Dependencies and integration points
Requires runner and PFNMAP test support.

## Risks and edge cases
PFN mapping tests may be architecture/configuration sensitive.

## Test signals
Exit status mirrors the `pfnmap` target.
