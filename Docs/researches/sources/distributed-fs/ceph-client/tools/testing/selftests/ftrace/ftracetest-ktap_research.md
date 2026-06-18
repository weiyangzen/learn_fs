<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/ftracetest-ktap -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/ftracetest-ktap

## Purpose
This wrapper adapts `ftracetest` to kselftest's expected KTAP output.

## Important APIs, Types, And Functions
It runs `./ftracetest -K -v` under `sh -e`.

## Control Flow
kselftest invokes this script as `TEST_PROGS`; the script immediately delegates to the main harness with KTAP and verbose mode enabled.

## State And Persistence
All state changes are from `ftracetest`; the wrapper has none of its own.

## Dependencies And Integration Points
It depends on `ftracetest` being present and executable in the same directory.

## Risks
Any nonzero `ftracetest` exit is propagated because `-e` is active.

## Test Signals
Expected output starts with KTAP/TAP formatting and exits with the aggregate ftrace test status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/ftracetest-ktap -->
