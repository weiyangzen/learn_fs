# sources/cloud-native/containerd/integration/failpoint/cmd/runc-fp/issue9103.go

## Purpose

This Linux failpoint profile reproduces issue 9103 by killing the runc init process immediately after a successful `runc create`. It forces shim cleanup paths to handle an init process that dies at a sensitive lifecycle point.

## Important APIs, Types, And Functions

- `issue9103KillInitAfterCreate` is an `invokerInterceptor` registered under profile name `issue9103`.
- It reads `init.pid`, parses the PID, sends `SIGKILL`, and sleeps for three seconds.

## Control Flow

The interceptor detects whether the current runc command line contains `create`, invokes real runc first, and returns immediately for non-create commands. For create, it reads the generated `init.pid`, validates it is positive, sends `SIGKILL` to that process, then sleeps to give the shim time to receive `SIGCHLD` and begin cleanup.

## State And Persistence Behavior

It reads the bundle-local `init.pid` file created by runc and mutates process state by killing the init process. No file state is intentionally written.

## Dependencies And Integration Points

It integrates with the `runc-fp` wrapper, runc bundle layout, Linux signals, and shim lifecycle cleanup behavior.

## Risks And Edge Cases

The profile assumes `init.pid` exists after `runc create` and contains a valid integer. The fixed three-second sleep is timing-sensitive but intentionally gives shim cleanup a deterministic window.

## Test Signals

Issue-specific tests using this profile can verify containerd handles init death after create without leaking shim/task state.
