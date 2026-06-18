<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/version/version.go -->
# sources/cloud-native/stargz-snapshotter/version/version.go

## Purpose
Defines build-time version metadata variables for stargz snapshotter binaries.

## Important APIs, Types, And Functions
- `Version` defaults to `0.0.0+unknown`.
- `Revision` defaults to empty string.
- `Package` defaults to `github.com/containerd/stargz-snapshotter`.

## Control Flow
No runtime flow; variables are read by binaries and can be overridden with linker flags.

## State And Persistence
Process-global version variables only. Values are typically embedded at build time.

## Dependencies And Integration Points
Used by CLI/server binaries for version output and release identification. Build scripts may set these via `-ldflags`.

## Risks And Edge Cases
Missing linker flags produce unknown version metadata. External consumers should not assume `Revision` is non-empty.

## Test Signals
Version commands or package consumers should report linker-provided values in release builds and defaults in local builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/version/version.go -->
