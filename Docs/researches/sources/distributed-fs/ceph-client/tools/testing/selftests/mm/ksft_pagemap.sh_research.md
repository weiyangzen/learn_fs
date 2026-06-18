# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_pagemap.sh

## Purpose
Wrapper entry point for the MM selftest `pagemap` category.

## Important APIs, types, and functions
Invokes `./run_vmtests.sh -t pagemap`.

## Control flow
Delegates pagemap and procfs page-state tests to the runner.

## State and persistence behavior
No wrapper state.

## Dependencies and integration points
Requires pagemap-readable environment for full coverage and the runner's test binaries.

## Risks and edge cases
Unprivileged PFN masking or procfs restrictions can cause delegated skips/failures.

## Test signals
Success is the pagemap target returning success.
