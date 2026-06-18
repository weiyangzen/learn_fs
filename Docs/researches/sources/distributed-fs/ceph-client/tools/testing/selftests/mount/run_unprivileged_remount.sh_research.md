<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/run_unprivileged_remount.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount/run_unprivileged_remount.sh

## Purpose
Kselftest wrapper that runs `unprivileged-remount-test` when user namespace mapping support is visible.

## Important APIs, Types, and Functions
- Defines `ksft_skip=4`.
- Checks for `/proc/self/uid_map`.
- Executes `./unprivileged-remount-test` or prints a warning and exits skip.

## Control Flow
The script gates the C helper on uid-map availability, then delegates execution and exit status to the helper.

## State and Persistence Behavior
No direct state changes beyond running the helper.

## Dependencies and Integration Points
Requires `/proc/self/uid_map` and the compiled helper. Registered by the mount `Makefile`.

## Risks and Edge Cases
The presence of `/proc/self/uid_map` does not guarantee `unshare(CLONE_NEWUSER)` is permitted by runtime policy, so the helper can still fail.

## Test Signals
Missing uid map exits 4. Otherwise the helper's exit code is returned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/run_unprivileged_remount.sh -->
