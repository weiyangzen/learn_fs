# sources/cloud-native/containerd/integration/issue7496_linux_test.go

## Purpose

This Linux regression test reproduces issue 7496/8931, where slow `umount2` during sandbox deletion could leak shims or block cleanup. It injects syscall delay with `strace` and verifies pod removal eventually succeeds and the shim exits.

## Important APIs, Types, And Functions

- `TestIssue7496` orchestrates the reproduction.
- `injectDelayToUmount2` attaches `strace` to a shim PID and injects delay into `umount2`.
- `connectToShim` resolves the shim socket and creates a ttrpc task client.
- `shimPid` calls shim `Connect` to get the shim process ID.

## Control Flow

The test creates a sandbox, connects to its shim, attaches `strace` with a 12-second `umount2` delay, creates and starts a container, then loops `StopPodSandbox` and `RemovePodSandbox` until they succeed or a three-minute context expires. After deletion, it waits for `strace` to exit. If `strace` is still running after 15 seconds, it expects shim connection failure, logs an error, kills the shim, and drains the strace goroutine.

## State And Persistence Behavior

The test mutates live shim process behavior through `strace` and observes sandbox/container runtime state. It does not write durable state except normal containerd metadata during the test.

## Dependencies And Integration Points

It depends on Linux `strace` with syscall injection support, shim ttrpc APIs, Unix sockets, CRI sandbox/container deletion, and Pause image availability.

## Risks And Edge Cases

The test is host-tool and timing sensitive. `strace` must be installed and new enough. Attaching to shims may require privileges. The cleanup path kills leaked shims only after a failure condition.

## Test Signals

Passing means sandbox removal tolerates slow unmounts and does not leave the shim stuck under the injected delay.
