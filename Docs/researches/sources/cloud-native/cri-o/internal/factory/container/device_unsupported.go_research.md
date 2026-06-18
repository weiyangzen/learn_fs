# sources/cloud-native/cri-o/internal/factory/container/device_unsupported.go

## Purpose
Provides device API implementations for platforms that are neither Linux nor FreeBSD. It rejects general device setup and conditionally rejects CDI injection when devices are requested.

## Important APIs, Types, And Functions
- `SpecAddDevices` always returns an unsupported-platform error containing `runtime.GOOS`.
- `SpecInjectCDIDevices` succeeds for empty CDI input and errors for non-empty `c.Config().CDIDevices`.

## Control Flow
The file is gated by `//go:build !linux && !freebsd`. Common factory callers can compile on unsupported platforms but cannot successfully add CRI-O/CRI devices. CDI is only tolerated when there is nothing to inject.

## State And Persistence
No state is changed. It does not mutate the OCI spec or persist anything.

## Dependencies And Integration Points
Maintains API parity for cross-platform builds while avoiding Linux and FreeBSD-specific imports. It imports only the CRI-O device config type plus `fmt` and `runtime`.

## Risks And Edge Cases
Configured devices fail fast on unsupported platforms, unlike FreeBSD where they are a no-op. Only structured CDI device requests are checked; legacy annotation CDI behavior is not parsed here.

## Test Signals
No direct tests in this subset. Build tags and compile coverage are the main signal.
