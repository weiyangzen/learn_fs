# sources/cloud-native/containerd/internal/cri/server/sandbox_run_other.go

## Purpose

This non-Linux, non-Windows file supplies CRI service sandbox network helper stubs for other Unix-like platforms.

## Important APIs, Types, and Functions

`bringUpLoopback` returns nil. `setupNetnsWithinUserns` returns an unsupported error for setting up netns within userns.

## Control Flow

Both functions are direct returns.

## State and Persistence Behavior

No network namespace or link state is changed.

## Dependencies and Integration Points

It satisfies symbols used by `RunPodSandbox` under `!windows && !linux`.

## Risks and Test Signals

Pod user namespaces with sandbox networking are unsupported on these platforms. Compile and platform smoke tests are the main signals.
