<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/verification/verificationtest-ktap -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/verification/verificationtest-ktap

## Purpose
Shell wrapper that runs ftracetest in KTAP mode for runtime verification tests.

## Important APIs, Types, and Functions
../ftrace/ftracetest -K -v --rv ../verification.

## Control Flow
Executes ftracetest with KTAP output and the verification directory as the runtime-verification suite.

## State and Persistence
No persistent state except ftracetest logs/output.

## Dependencies and Integration Points
Depends on /bin/sh, ftracetest, and runtime verification test files.

## Risks and Edge Cases
Relative paths make it sensitive to invocation location under kselftest.

## Test Signals
Pass/fail is delegated to ftracetest KTAP output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/verification/verificationtest-ktap -->
