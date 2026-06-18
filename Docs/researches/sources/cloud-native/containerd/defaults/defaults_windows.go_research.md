# sources/cloud-native/containerd/defaults/defaults_windows.go

## Purpose
This Windows-specific file defines containerd defaults for paths, named pipes, runtime, snapshotter, differ, and FIFO behavior.

## Important APIs, Types, and Functions
Variables derive `DefaultRootDir`, `DefaultStateDir`, `DefaultConfigDir`, and `DefaultConfigIncludePattern` from `ProgramData` and `programfiles`. Constants include named-pipe addresses, differ `windows`, empty FIFO dir, runtime `io.containerd.runhcs.v1`, and snapshotter `windows`.

## Control Flow
No procedural flow beyond package variable initialization from environment variables.

## State and Persistence
Persistent root/state/config locations are environment-dependent Windows paths. Named pipes define API endpoints.

## Dependencies and Integration Points
Used by Windows clients, daemon defaults, and integration tests.

## Risks
Environment-variable casing matters (`ProgramData` and `programfiles`). Path defaults are evaluated at process start.

## Test Signals
Windows integration client files use Windows-specific defaults and image selection.
