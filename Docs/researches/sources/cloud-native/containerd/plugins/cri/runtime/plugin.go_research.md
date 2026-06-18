# sources/cloud-native/containerd/plugins/cri/runtime/plugin.go

## Purpose
Registers the base CRI runtime plugin and owns runtime-side CRI config validation, state/root directory compatibility, base OCI spec preloading, klog level setup, and migration from legacy CRI config.

## Important APIs, Types, And Functions
`init` registers the `runtime` CRI service plugin. `initCRIRuntime` validates config and returns a `runtime` object. `runtime.Config` and `runtime.LoadOCISpec` expose cached runtime state. `loadBaseOCISpecs`, `loadOCISpec`, `setGLogLevel`, `configMigration`, and `migrateConfig` are the main helpers.

## Control Flow
Initialization sets plugin platform/export metadata, validates runtime config and emits warnings, computes backward-compatible CRI root/state directories, creates/chmods state dir, logs the marshaled config, initializes klog flags from containerd log level, loads unique `BaseRuntimeSpec` files, and returns the runtime service object.

## State And Persistence
Persistent state is the CRI state directory under the containerd state parent and any referenced base OCI spec files. The plugin caches loaded specs in memory. Migration mutates config maps before startup and preserves unknown runtime keys unless they moved to other split plugins.

## Dependencies And Integration Points
Integrates with the warning plugin, CRI config validation, Kubernetes klog, `platforms`, `errdefs`, `pkg/oci`, and versioned config migration. Other CRI services depend on this base plugin for config and OCI spec lookup.

## Risks
Config migration relies on concrete `map[string]any` shapes and type assertions. `setGLogLevel` mutates global klog flags. Base OCI spec loading is startup-fatal when a referenced file is missing or invalid. Directory permissions are forced to `0700`, which matters for upgrades.

## Test Signals
`load_test.go` covers spec loading. `plugin_test.go` covers migration of selected runtime, CNI, and moved keys. Full startup validation is covered by broader CRI integration tests.
