# sources/cloud-native/containerd/plugins/cri/runtime/plugin_test.go

## Purpose
Tests migration from the old CRI plugin config into the split CRI runtime plugin config.

## Important APIs, Types, And Functions
`TestCRIRuntimePluginConfigMigration` exercises `configMigration` and checks migrated general runtime keys, moved image/server keys, CNI `bin_dir` to `bin_dirs`, and runtime `sandbox_mode` to `sandboxer`.

## Control Flow
The test constructs a legacy CRI config map with runtime, CNI, image, and server fields, runs migration for config version `2`, then inspects the destination runtime plugin map.

## State And Persistence
All state is in-memory. It verifies config shape migration rather than TOML persistence.

## Dependencies And Integration Points
Uses the `plugins` package for plugin keys and `testify` for assertions. It covers the migration helper in `runtime/plugin.go`.

## Risks
It does not check preservation of existing destination values, invalid CNI type shapes, or multiple runtimes, but it covers the most important split-config behavior.

## Test Signals
Provides regression coverage for avoiding image/server config leakage into the runtime plugin and for compatibility renames.
