# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_soft_dirty.sh

## Purpose
Wrapper entry point for the MM selftest `soft_dirty` category.

## Important APIs, types, and functions
The script invokes `./run_vmtests.sh -t soft_dirty`.

## Control flow
Delegates soft-dirty tracking tests to the runner.

## State and persistence behavior
No local state; delegated tests may write procfs clear_refs controls and inspect pagemap soft-dirty bits.

## Dependencies and integration points
Requires pagemap/soft-dirty kernel support and runner-managed binaries.

## Risks and edge cases
Procfs permissions and PFN/bit visibility affect delegated behavior.

## Test signals
Success follows the runner's `soft_dirty` target.
