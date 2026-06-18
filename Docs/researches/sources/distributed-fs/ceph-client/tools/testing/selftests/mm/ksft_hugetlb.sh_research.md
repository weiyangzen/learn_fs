# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_hugetlb.sh

## Purpose
Wrapper entry point for the MM selftest `hugetlb` category.

## Important APIs, types, and functions
The script runs `./run_vmtests.sh -t hugetlb` under `#!/bin/sh -e`.

## Control flow
All hugetlb setup, hugepage allocation checks, and test selection are delegated to `run_vmtests.sh`.

## State and persistence behavior
The wrapper has no local state. The hugetlb target can mount filesystems, consume hugepages, and run accounting tests.

## Dependencies and integration points
Requires built hugetlb selftest binaries and a host configured with hugetlb support.

## Risks and edge cases
Many hugetlb tests need root or preallocated pages. Wrapper-level failure handling is only `set -e`.

## Test signals
Exit status is exactly the hugetlb target's exit status.
