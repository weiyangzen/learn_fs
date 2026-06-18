<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_defaults_linux.go -->
# sources/cloud-native/containerd/plugins/transfer/plugin_defaults_linux.go

## Purpose
Defines Linux default transfer unpack platforms, including an optional EROFS-native image path.

## Important APIs, Types, And Functions
`erofsPlatformSpec` adds OS feature `erofs` to the default platform. `defaultUnpackConfig` returns default and EROFS configurations.

## Control Flow
The first entry uses the default platform, default snapshotter, and default differ. The second entry uses the full platform including `os.features=erofs`, snapshotter `erofs`, differ `erofs`, and `Optional: true`.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by transfer plugin initialization on Linux. It ties EROFS snapshotter/differ discovery to unpack platform configuration without making EROFS mandatory.

## Risks And Edge Cases
If EROFS differ or snapshotter is registered but skipped or unavailable, optional handling must skip cleanly; this is tested. Platform formatting uses `FormatAll` so OS features remain part of matching.

## Test Signals
`plugin_linux_test.go` verifies unavailable EROFS differ does not prevent default unpack platform configuration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_defaults_linux.go -->
