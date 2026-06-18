# sources/cloud-native/containerd/integration/build_local_containerd_helper_test.go

## Purpose
This helper builds an in-process containerd client with core plugins initialized for integration tests.

## Important APIs, Types, and Functions
`buildLocalContainerdClient` loads plugins once, initializes them with per-plugin root/state paths, applies optional plugin tweak functions, and creates a client with in-memory services. `tweakContentInitFnWithDelayer` wraps the content plugin to delay commits. `contentStoreDelayer` and `contentWriterDelayer` implement the delay wrappers.

## Control Flow
Plugins are loaded through the server loader once. Each plugin gets a `plugin.InitContext` with root/state properties and decoded config. The helper adds each initialized plugin to a set, forces instance creation, and passes the last init context to `containerd.WithInMemoryServices`.

## State and Persistence
Test roots and states live under the caller's temp dir. The global `sync.Once` caches loaded plugin registrations. Delayer state wraps content writes and sleeps during commit.

## Dependencies and Integration Points
Imports many plugin packages for registration, server config/loading, content store, CRI constants, platform defaults, and containerd client construction.

## Risks
Plugin initialization order and the use of the last init context are subtle. Tweaking a plugin mutates a registration copy but must preserve original initialization. Commit delay can make tests timing-sensitive.

## Test Signals
Used by local in-memory integration tests to exercise real plugin wiring without a daemon process.
