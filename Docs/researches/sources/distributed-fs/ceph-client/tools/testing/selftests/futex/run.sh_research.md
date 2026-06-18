<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/run.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/run.sh

## Purpose
This top-level futex runner detects color support and delegates to the functional test runner.

## Important APIs, Types, And Functions
It uses `tput setf/setaf/sgr0`, exports `USE_COLOR`, and runs `(cd functional; ./run.sh)`.

## Control Flow
The script probes terminal color capability, sets `USE_COLOR=1` if color setup succeeds, then executes the functional runner in a subshell.

## State And Persistence
It only exports an environment variable and changes directory in a subshell.

## Dependencies And Integration Points
It integrates the top-level kselftest entry with `functional/run.sh`.

## Risks
Because `functional/run.sh` is empty in this snapshot, this top-level runner also performs no actual binary execution beyond delegation.

## Test Signals
Direct success only proves shell and directory availability; meaningful futex test signals require functional runner content or direct binary invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/run.sh -->
