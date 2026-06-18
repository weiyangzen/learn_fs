
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/nri_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/nri_linux.go

## Purpose

This Linux-specific file adds NRI adapter methods that let NRI invoke CRI container resource updates and container stop behavior through existing `criService` implementations.

## Important APIs, Types, and Functions

It defines `(*criImplementation).UpdateContainerResources` and `(*criImplementation).StopContainer`.

## Control Flow

`UpdateContainerResources` delegates to `i.c.updateContainerResources`, passing the container, request, and current status supplied by NRI integration. `StopContainer` delegates to `i.c.stopContainerRetryOnConnectionClosed` with a timeout.

## State and Persistence Behavior

State changes are performed by the delegated CRI service methods. Resource updates can mutate containerd spec metadata, running task resources, and CRI container status. Stop can signal and wait for runtime task shutdown. This adapter file itself stores no state.

## Dependencies and Integration Points

Dependencies include context, time, CRI container store, and CRI runtime API. It integrates NRI plugin actions with the CRI server's native resource-update and stop-container code paths on Linux.

## Risks and Edge Cases

Because this delegates into shared CRI logic, NRI-triggered changes inherit the same race and rollback behavior as normal CRI calls. Stop behavior depends on retry handling for connection-closed errors in code outside this file. The file is Linux-only, so equivalent NRI hooks are unavailable on non-Linux builds.

## Test Signals

Useful tests would use fake `criService` state to verify that NRI adapter calls reach the underlying update and stop methods, propagate errors, and preserve status updates consistently with direct CRI RPC paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/nri_linux.go -->
