# sources/cloud-native/containerd/internal/cri/server/sandbox_portforward_other.go

## Purpose

This non-Linux, non-Windows file marks port forwarding unsupported.

## Important APIs, Types, and Functions

`portForward` returns `port forward: ErrNotImplemented`.

## Control Flow

The function is a direct error return.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It satisfies the platform-specific port-forward symbol under `!windows && !linux`.

## Risks and Test Signals

Callers must surface the not-implemented error cleanly. Build-tag compile tests are the primary signal.
