# sources/cloud-native/containerd/integration/windows_rootfs_size_test.go

## Purpose

`windows_rootfs_size_test.go` verifies that a requested Windows container root filesystem size is reflected in the container's C: drive free-space output.

## Important APIs, Types, and Functions

- `TestWindowsRootfsSize` creates a container with `WindowsContainerResources.RootfsSizeInBytes` set to 200 GiB and parses `dir /-C C:\` output from the container log.

## Control Flow

The test creates a sandbox with log directory, pulls pause image, creates a container that runs `cmd /c dir /-C C:\` with a log path and rootfs size resource, waits for exit, reads the log, scans for the `bytes free` line, parses the available bytes, and checks it is within 300 MiB below the requested size.

## State and Persistence Behavior

It validates runtime-created virtual disk/rootfs sizing and CRI log output. No long-lived state is intended.

## Dependencies and Integration Points

It depends on Windows CRI runtime service, Windows resources in CRI API, container logs, and command output formatting.

## Risks and Edge Cases

The parser is tied to English `dir` output and exact token positions. Some space is expected to be occupied, so the assertion uses tolerance rather than exact equality.

## Test Signals

Failure points to Windows rootfs sizing, resource propagation, container execution, or log parsing regressions.
