# sources/cloud-native/containerd/integration/windows_device_test.go

## Purpose

`windows_device_test.go` verifies Windows device-class injection by exposing host GPU/display driver store content inside a container.

## Important APIs, Types, and Functions

- `TestWindowsDevice` creates a sandbox with a log directory, requests device class `GUID_DEVINTERFACE_DISPLAY_ADAPTER`, runs a command that lists `HostDriverStore`, and checks the CRI log.

## Control Flow

The test creates a sandbox, pulls a test image, creates a container with command, log path, and `WithDevice("", "class/<GUID>", "")`, starts it, waits for exit, reads the container log, and asserts expected stdout content.

## State and Persistence Behavior

It inspects the container log file written under the pod log directory. The relevant runtime state is Windows device mount injection into the container filesystem.

## Dependencies and Integration Points

It depends on Windows CRI integration helpers, device option generation, log formatting helpers, and Windows host driver store behavior.

## Risks and Edge Cases

The test assumes the display adapter class is supported and mounts `HostDriverStore/FileRepository`. Host GPU/display configuration or image shell compatibility can affect the signal.

## Test Signals

Failure indicates Windows device class handling, HCS mount injection, container execution, or CRI log capture regressions.
