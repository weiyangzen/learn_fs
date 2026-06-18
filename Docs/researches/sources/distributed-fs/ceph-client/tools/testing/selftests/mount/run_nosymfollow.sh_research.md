<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/run_nosymfollow.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount/run_nosymfollow.sh

## Purpose
Minimal kselftest wrapper that runs the compiled `nosymfollow-test` binary.

## Important APIs, Types, and Functions
- Executes `./nosymfollow-test`.

## Control Flow
No branching; the script delegates all logic and exit status to the C helper.

## State and Persistence Behavior
No state beyond the helper's namespace-local filesystem work.

## Dependencies and Integration Points
Requires the helper binary to be built in the current directory.

## Risks and Edge Cases
If the binary is missing or not executable, the wrapper fails directly.

## Test Signals
Exit code and output are from `nosymfollow-test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/run_nosymfollow.sh -->
