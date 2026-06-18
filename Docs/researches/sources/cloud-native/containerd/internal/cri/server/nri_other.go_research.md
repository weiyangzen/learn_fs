# sources/cloud-native/containerd/internal/cri/server/nri_other.go

## Purpose

This non-Linux build-tag file provides placeholder CRI implementation methods for NRI-adjacent container operations that are implemented differently on Linux. It keeps the server package compiling on non-Linux platforms without wiring Linux-specific resource update or stop logic.

## Important APIs, Types, and Functions

`(*criImplementation).UpdateContainerResources` accepts a container store object, CRI update request, and current status, but returns an empty status with no error. `(*criImplementation).StopContainer` accepts a container and timeout and returns nil without performing work.

## Control Flow

Both methods are straight-line stubs. There is no validation, containerd call, NRI notification, status mutation, or timeout handling.

## State and Persistence Behavior

No state is read or persisted. The empty status returned by `UpdateContainerResources` is risky if accidentally used as real state on a non-Linux path.

## Dependencies and Integration Points

The file depends only on CRI container store types and CRI runtime API request types. It integrates through build tags with platform-specific CRI implementation method sets.

## Risks and Test Signals

The main risk is silent no-op behavior on unsupported platforms. Compile coverage for non-Linux targets is the primary signal; behavioral tests should assert that callers either avoid these paths or treat them as unsupported where appropriate.
