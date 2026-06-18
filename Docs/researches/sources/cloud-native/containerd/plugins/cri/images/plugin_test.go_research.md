# sources/cloud-native/containerd/plugins/cri/images/plugin_test.go

## Purpose
Tests legacy CRI image configuration migration into the split CRI image plugin.

## Important APIs, Types, And Functions
`TestSandboxImageConfigMigration` calls `configMigration` with a legacy `sandbox_image` and asserts it appears under `pinned_images.sandbox`. `TestRegistryConfigMigration` verifies `registry.config_path` is preserved under the image service plugin key.

## Control Flow
Each test builds a synthetic `pluginConfigs` map containing `io.containerd.grpc.v1.cri`, invokes migration with config version `2`, and inspects the generated `io.containerd.cri.v1.images` map.

## State And Persistence
All state is in-memory test data. The tests validate mutation of the config map, not on-disk TOML serialization.

## Dependencies And Integration Points
Uses `plugins` names and `testify` assertions. It directly covers migration helpers in `plugin.go`.

## Risks
Coverage is narrow: it does not test runtime platform migration, pinned image merge behavior, existing destination config preservation, or invalid map types.

## Test Signals
Positive migration tests provide regression signals for the two most visible legacy image settings.
