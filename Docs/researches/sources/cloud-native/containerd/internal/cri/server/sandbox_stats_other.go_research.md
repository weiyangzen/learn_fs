# sources/cloud-native/containerd/internal/cri/server/sandbox_stats_other.go

## Purpose

This non-Linux, non-Windows file marks pod sandbox stats unsupported.

## Important APIs, Types, and Functions

`podSandboxStats` returns `pod sandbox stats not implemented` wrapping `errdefs.ErrNotImplemented`.

## Control Flow

The function is a direct error return.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It satisfies the platform-specific stats symbol under `!windows && !linux`.

## Risks and Test Signals

Clients on these platforms receive a not-implemented stats error. Build-tag compile tests are the main signal.
