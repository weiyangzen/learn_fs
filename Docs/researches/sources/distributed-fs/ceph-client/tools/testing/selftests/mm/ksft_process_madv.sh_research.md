# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_process_madv.sh

## Purpose
Despite its filename, this wrapper invokes the runner's `mmap` category.

## Important APIs, types, and functions
The script is `#!/bin/sh -e` plus `./run_vmtests.sh -t mmap`.

## Control flow
It delegates to `run_vmtests.sh` exactly like `ksft_mmap.sh`; there is no local call to a `process_madv` target.

## State and persistence behavior
No wrapper-owned state.

## Dependencies and integration points
Requires the `mmap` runner target. If process-madvise tests are expected, this wrapper-to-target mapping should be checked against the broader selftest design.

## Risks and edge cases
The filename/target mismatch is the main maintenance risk. Automated systems may assume it runs process_madvise-specific coverage when it actually requests `mmap`.

## Test signals
Success follows `run_vmtests.sh -t mmap`.
