# sources/cloud-native/containerd/plugins/services/sandbox/store_local.go

## Purpose
`store_local.go` registers the local sandbox metadata store plugin.

## Important APIs, Types, And Functions
The plugin type is `plugins.SandboxStorePlugin`, ID `local`, and it requires the metadata plugin. Initialization returns `metadata.NewSandboxStore(m.(*metadata.DB))`.

## Control Flow
Plugin initialization resolves the single metadata DB and constructs a store wrapper around it.

## State And Persistence
Sandbox records persist in the shared metadata database through `metadata.NewSandboxStore`.

## Dependencies And Integration Points
The file connects the plugin registry, metadata DB, and sandbox store plugin type. It is consumed by `store_service.go`.

## Risks
The implementation assumes the metadata plugin instance is `*metadata.DB`. All validation and concurrency behavior is delegated to the metadata store.

## Test Signals
No direct tests are present. Sandbox store service and metadata store tests elsewhere are the likely coverage.
