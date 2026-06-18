<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/run.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/run.sh

## Purpose
Runs a VFIO test binary with all BDFs recorded by setup.sh.

## Important APIs, Types, and Functions
main, DEVICES_DIR, command invocation "$@" ${device_bdfs}.

## Control Flow
Lists prepared device BDFs, skips with exit code 4 if none exist, otherwise appends BDFs to the supplied test command.

## State and Persistence
Reads state from TMPDIR/vfio-selftests-devices only.

## Dependencies and Integration Points
Depends on bash, lib.sh, and setup.sh-created directory.

## Risks and Edge Cases
Whitespace in BDF list is not expected; command status is the test status.

## Test Signals
Used to run compiled tests against prepared devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/scripts/run.sh -->
