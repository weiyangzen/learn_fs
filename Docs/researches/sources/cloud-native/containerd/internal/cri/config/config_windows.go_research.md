# sources/cloud-native/containerd/internal/cri/config/config_windows.go

## Purpose

`config_windows.go` defines Windows default CRI image and runtime configuration.

## Important APIs, Types, and Functions

- `defaultNetworkPluginBinDirs` returns `%ProgramFiles%\containerd\cni\bin`.
- `DefaultImageConfig` sets default snapshotter, stats period, max downloads, key model, pause image, and image pull progress timeout.
- `DefaultRuntimeConfig` configures Windows CNI paths and two runhcs runtimes: `runhcs-wcow-process` and `runhcs-wcow-hypervisor`.

## Control Flow

Default runtime config builds process-isolated and hypervisor-isolated runtime entries. The hypervisor runtime includes runhcs options for sandbox isolation and CPU limit scaling.

## State and Persistence Behavior

Only in-memory default config structs are returned. Paths are derived from `ProgramFiles`.

## Dependencies and Integration Points

It depends on containerd defaults, Windows environment variables/path handling, runhcs runtime type strings, and Windows-specific annotation pass-through patterns.

## Risks and Edge Cases

Defaults depend on `ProgramFiles` being set. Runtime annotation allowlists and hypervisor options must stay aligned with hcsshim/runhcs expectations.

## Test Signals

Windows integration tests and config tests indirectly validate these defaults.
