# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_madv_guard.sh

## Purpose
Wrapper entry point for the MM selftest `madv_guard` category.

## Important APIs, types, and functions
The wrapper executes `./run_vmtests.sh -t madv_guard`.

## Control flow
The runner's `madv_guard` target invokes the guard-region tests, including `guard-regions`.

## State and persistence behavior
No local state. Underlying tests create mappings, temporary files, memfds, and inspect procfs.

## Dependencies and integration points
Requires kernel support for guard-region madvise operations and the built `guard-regions` binary.

## Risks and edge cases
Feature availability, permissions for userfaultfd/process_madvise, and THP configuration affect delegated results.

## Test signals
Wrapper success mirrors the `madv_guard` runner target.
