# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_madv_populate.sh

## Purpose
Wrapper entry point for the MM selftest `madv_populate` category.

## Important APIs, types, and functions
The script uses `#!/bin/sh -e` and invokes `./run_vmtests.sh -t madv_populate`.

## Control flow
Delegates to runner-managed tests for `MADV_POPULATE_READ` and `MADV_POPULATE_WRITE` behavior.

## State and persistence behavior
The wrapper has no state; underlying tests control their mappings.

## Dependencies and integration points
Requires `run_vmtests.sh` and built populate selftest binaries.

## Risks and edge cases
Kernel support and memory pressure affect delegated results.

## Test signals
Exit status follows the `madv_populate` target.
