<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount/Makefile

## Purpose
Build and register classic mount namespace selftests for unprivileged remount behavior and `MS_NOSYMFOLLOW`.

## Important APIs, Types, and Functions
- Sets `CFLAGS = -Wall -O2`.
- `TEST_PROGS := run_unprivileged_remount.sh run_nosymfollow.sh`.
- `TEST_GEN_FILES := unprivileged-remount-test nosymfollow-test`.
- Includes `../lib.mk`.

## Control Flow
The makefile compiles two C helpers and registers two shell wrappers as test programs. Kselftest invokes the wrappers, not the helpers directly.

## State and Persistence Behavior
Generated binaries are build artifacts managed by kselftest. No runtime state is defined here.

## Dependencies and Integration Points
Depends on kselftest `lib.mk` and the directory `config` requesting user namespaces.

## Risks and Edge Cases
The wrappers assume binaries are in the current test execution directory. Compiler flags are minimal and do not include special kernel headers.

## Test Signals
Build success produces `unprivileged-remount-test` and `nosymfollow-test`; runtime signals come from the wrappers/helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/Makefile -->
