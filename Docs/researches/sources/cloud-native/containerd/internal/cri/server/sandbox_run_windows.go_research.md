# sources/cloud-native/containerd/internal/cri/server/sandbox_run_windows.go

## Purpose

This Windows CRI service file supplies platform-specific sandbox network helper behavior.

## Important APIs, Types, and Functions

`bringUpLoopback` returns nil because loopback setup is not performed here. `setupNetnsWithinUserns` returns an unsupported error for Windows.

## Control Flow

Both functions are direct returns.

## State and Persistence Behavior

No network namespace or interface state is changed.

## Dependencies and Integration Points

It satisfies `RunPodSandbox` helper symbols for Windows builds.

## Risks and Test Signals

Pod user namespace network namespace setup is unsupported on Windows. Windows sandbox run and portforward tests should cover supported network behavior.
