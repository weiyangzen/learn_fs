# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_memory_failure.sh

## Purpose
Wrapper entry point for the MM selftest `memory-failure` category.

## Important APIs, types, and functions
The script calls `./run_vmtests.sh -t memory-failure`.

## Control flow
Delegates to memory-failure tests, which may inject or simulate hardware memory failure paths.

## State and persistence behavior
No local state. Delegated tests can affect poisoned-page state and require a controlled environment.

## Dependencies and integration points
Requires `run_vmtests.sh`, built memory-failure binary, and kernel support/permissions for memory-failure operations.

## Risks and edge cases
Hardware-poison or memory-failure tests are inherently invasive and permission-sensitive.

## Test signals
The wrapper status mirrors the `memory-failure` category.
