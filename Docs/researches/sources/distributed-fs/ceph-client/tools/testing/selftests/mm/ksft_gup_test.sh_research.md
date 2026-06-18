# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_gup_test.sh

## Purpose
Wrapper entry point for the MM selftest `gup_test` category.

## Important APIs, types, and functions
The script uses `#!/bin/sh -e` and calls `./run_vmtests.sh -t gup_test`.

## Control flow
The runner target executes GUP fast/PIN fast benchmarks, page dump coverage, and `gup_longterm`.

## State and persistence behavior
The wrapper has none. Underlying tests may open `/sys/kernel/debug/gup_test`, map memory, and allocate hugetlb resources.

## Dependencies and integration points
Requires `run_vmtests.sh`, built GUP test binaries, debugfs, and `CONFIG_GUP_TEST` for full coverage.

## Risks and edge cases
Without debugfs or permissions the underlying category may skip. The wrapper does not pass through custom arguments.

## Test signals
Exit status follows `run_vmtests.sh -t gup_test`.
