# sources/cloud-native/containerd/integration/failpoint/cmd/runc-fp/delayexec.go

## Purpose

This Linux failpoint profile delays runc `exec` invocations until test-controlled FIFOs signal continuation. It allows integration tests to reproduce races around exec and container lifecycle operations.

## Important APIs, Types, And Functions

- `delayExec` wraps an `invoker` and only delays commands whose argv contains `exec`.
- `delay` triggers a ready FIFO and waits on a delay FIFO.
- `fifoFromProcessEnv` reads FIFO names from the exec process spec environment.
- `processEnvironment` locates `--process <file>`, reads the OCI process JSON, and returns environment variables.
- Environment keys come from `integration/failpoint/const.go`.

## Control Flow

For non-exec runc commands, `delayExec` directly invokes the underlying runc. For exec commands, it parses the process spec to find `_RUNC_FP_DELAY_EXEC_READY` and `_RUNC_FP_DELAY_EXEC_DELAY`, creates a trigger and waiter, signals readiness to the test, blocks until the test releases the delay FIFO, and then calls real runc.

## State And Persistence Behavior

State is externalized through named FIFOs supplied in the process environment. No durable repository or containerd state is written by this file.

## Dependencies And Integration Points

It integrates with the `runc-fp` main wrapper, OCI process JSON, containerd `fifosync`, logrus, and the failpoint environment constants.

## Risks And Edge Cases

The code assumes runc command-line arguments include `--process` for exec. Missing env vars or FIFO creation failures abort the runc command. Environment parsing keeps the last value for duplicate keys.

## Test Signals

Tests using the `delayExec` profile can assert ordering by waiting for the ready FIFO before triggering the delayed runc exec.
