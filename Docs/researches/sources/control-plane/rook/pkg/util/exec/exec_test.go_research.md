# sources/control-plane/rook/pkg/util/exec/exec_test.go

## Purpose
This file tests local exec helper behavior and exit-code extraction.

## Important APIs, Types, and Functions
`Test_assertErrorType()` checks stderr extraction for known exec error types. `TestMockExecHelperProcess()` exposes the helper process from `exec/test`. `TestExtractExitCode()` covers multiple error implementations and fallback string parsing. `TestFakeTimeoutError()` checks timeout detection. `TestExecuteCommandWithTimeout()` runs real simple commands.

## Control Flow, State, and Persistence
Tests execute local commands such as `cat`, `echo`, `false`, and `sleep`. The mock helper process relaunches the test binary with environment variables to simulate stdout/stderr/exit code.

## Dependencies and Integration Points
It depends on `exec/test` mock helpers, Kubernetes status/errors, Kubernetes utils exec errors, and testify. It protects command execution paths used by sys and Ceph utilities.

## Risks
Tests assume Unix-like commands are available. Timeout tests can be timing-sensitive on loaded systems. Remote pod exec is not covered.

## Test Signals
Signals include stdin capture, nil stdin output, nonzero exit errors, timeout errors, and exit code extraction from Go, Kubernetes, status, and string-form errors.
