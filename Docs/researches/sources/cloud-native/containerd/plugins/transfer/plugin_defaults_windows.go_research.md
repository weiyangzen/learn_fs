<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_defaults_windows.go -->
# sources/cloud-native/containerd/plugins/transfer/plugin_defaults_windows.go

## Purpose
Defines Windows default transfer unpack configuration.

## Important APIs, Types, And Functions
`defaultUnpackConfig` returns one entry using the default platform, snapshotter, and differ.

## Control Flow
The transfer plugin uses this entry when no TOML unpack config is provided on Windows.

## State And Persistence
No state.

## Dependencies And Integration Points
Integrates with defaults/platforms and the Windows build of the transfer plugin.

## Risks And Edge Cases
No optional CimFS/block-CIM defaults are added here, so advanced Windows snapshotters require explicit config or separate registration behavior.

## Test Signals
No file-local tests; covered by platform builds and transfer plugin initialization tests where run on Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_defaults_windows.go -->
