# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_mkdirty.sh

## Purpose
Wrapper entry point for the MM selftest target named `mkdirty`.

## Important APIs, types, and functions
The script calls `./run_vmtests.sh -t mkdirty`; the filename uses `mkdirty`, while the runner target string is `mkdirty`.

## Control flow
Delegates directly to the runner's dirty-page marking test.

## State and persistence behavior
No local state.

## Dependencies and integration points
Requires the runner target spelling `mkdirty` and its built test binary.

## Risks and edge cases
The target-name mismatch between filename and runner argument is intentional in this file and should not be silently renamed without checking `run_vmtests.sh`.

## Test signals
Successful exit from `run_vmtests.sh -t mkdirty`.
