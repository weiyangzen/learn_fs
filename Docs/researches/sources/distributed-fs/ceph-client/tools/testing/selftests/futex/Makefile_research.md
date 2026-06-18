<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/Makefile

## Purpose
This top-level futex selftest Makefile delegates build, install, and clean operations to the `functional` subdirectory.

## Important APIs, Types, And Functions
It defines `SUBDIRS := functional`, `TEST_PROGS := run.sh`, custom `all`, `INSTALL_RULE`, and `CLEAN` blocks, and includes `../lib.mk`.

## Control Flow
The `all` target creates per-subdir output directories, invokes `make -C functional`, and copies subdir `run.sh` into the output tree. Install and clean recurse similarly.

## State And Persistence
It creates output directories and installed test files.

## Dependencies And Integration Points
It integrates `functional/Makefile` with kselftest's top-level futex entry point.

## Risks
Recursive output path handling must stay aligned with `lib.mk`; missing `rsync` would break copying the subdir runner.

## Test Signals
Successful recursive build of all functional programs and executable top-level `run.sh` are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/Makefile -->
