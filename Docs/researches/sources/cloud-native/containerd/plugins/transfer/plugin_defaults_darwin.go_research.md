<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_defaults_darwin.go -->
# sources/cloud-native/containerd/plugins/transfer/plugin_defaults_darwin.go

## Purpose
Defines Darwin's default unpack configuration for the transfer plugin.

## Important APIs, Types, And Functions
`defaultUnpackConfig` returns one `unpackConfiguration`.

## Control Flow
It starts from `platforms.DefaultSpec`, rewrites the OS to `linux`, and selects the default snapshotter and default differ.

## State And Persistence
No state.

## Dependencies And Integration Points
Uses `containerd/defaults` and `platforms`. Consumed by `plugin.go` when no explicit unpack configuration is provided.

## Risks And Edge Cases
Darwin images are not defined for default unpack, so Linux is assumed. This is convenient for Linux image workflows on Darwin clients but not a general Darwin runtime statement.

## Test Signals
Indirectly covered by transfer configuration tests where platform-specific defaults are compiled.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_defaults_darwin.go -->
