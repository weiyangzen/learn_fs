<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_linux_test.go -->
# sources/cloud-native/containerd/plugins/transfer/plugin_linux_test.go

## Purpose
Tests Linux-specific transfer defaults, especially the optional EROFS unpack entry.

## Important APIs, Types, And Functions
`TestConfigureUnpackPlatformsDefaultConfigSkipsUnavailableErofsDiffer` uses `defaultConfig`, `newTestInitContext`, and `newTestDiffPlugin`.

## Control Flow
The test registers default and EROFS snapshotters, a usable default differ, and an EROFS differ that returns `plugin.ErrSkipPlugin`. It calls `configureUnpackPlatforms` with default config and asserts only the default unpack platform remains.

## State And Persistence
Uses temporary content and metadata stores created by shared test helpers.

## Dependencies And Integration Points
Depends on Linux build tags, transfer local config, snapshotter stubs, platform specs with `OSFeatures`, and plugin skip semantics.

## Risks And Edge Cases
Only covers unavailable EROFS differ, not unavailable EROFS snapshotter or successful EROFS configuration.

## Test Signals
Protects startup resilience when optional EROFS support is compiled into defaults but runtime dependencies are not available.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_linux_test.go -->
