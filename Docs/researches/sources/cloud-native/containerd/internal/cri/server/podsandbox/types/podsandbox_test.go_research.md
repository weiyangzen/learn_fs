# sources/cloud-native/containerd/internal/cri/server/podsandbox/types/podsandbox_test.go

## Purpose

This unit test validates `PodSandbox` lifecycle status and wait/exit synchronization.

## Important APIs, Types, and Functions

`Test_PodSandbox` creates a sandbox, updates it to ready with PID and creation time, starts one waiter expected to time out and one waiter expected to receive exit status, then calls `Exit`.

## Control Flow

The test uses a wait group with two goroutines. One context times out before exit; the other waits until `Exit` closes the stop channel and returns code 128 with the expected exit time.

## State and Persistence Behavior

Only in-memory status and stop channel state are exercised.

## Dependencies and Integration Points

It depends on sandbox store status types and containerd exit status conversion.

## Risks and Test Signals

The test catches regressions in wait cancellation and exit signaling. It does not cover repeated `Exit` calls or concurrent status updates beyond this simple case.
