# Research: sources/cloud-native/containerd/client/snapshotter_opts_windows.go

## Purpose
Provides the Windows build of snapshot option resolution, where Unix user namespace remapping logic is not applicable.

## Important APIs, Control Flow, And State
`resolveSnapshotOptions` accepts the same signature as the Unix implementation but simply returns the parent snapshot key unchanged. It performs no option inspection, no capability probing, and no persistent mutation.

## Dependencies And Integration
Depends only on `context` and `core/snapshots` for signature compatibility. It is selected by Go build tags on Windows and lets shared client code compile without Unix remap behavior.

## Risks And Test Signals
The primary risk is callers expecting remap labels to have an effect on Windows. Build tests should ensure the Windows implementation remains signature-compatible; behavioral tests should assert it is a no-op.
