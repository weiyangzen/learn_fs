# sources/cloud-native/containerd/plugins/cri/images/plugin.go

## Purpose
Registers the CRI image service plugin (`io.containerd.cri.v1.images`) and migrates image-related settings from the legacy monolithic CRI gRPC plugin. It wires the CRI image server to metadata content/images, snapshotters, transfer, leases, sandbox store, warnings, and an in-memory containerd client.

## Important APIs, Types, And Functions
`init` registers the plugin with `criconfig.DefaultImageConfig`. `configMigration` and `migrateConfig` copy legacy `sandbox_image`, registry, image pull, image decryption, snapshotter, and runtime snapshot settings into the new image config. The init function builds `images.CRIImageServiceOptions`, resolves snapshotter roots, parses runtime platforms, and calls `images.NewService`.

## Control Flow
Startup loads metadata DB, fills the default Linux registry config path only when no registry mirrors/config path are configured, validates image config, emits warnings through the warning plugin, warns about local image pull conflicts, creates an in-memory client in the Kubernetes namespace, selects the default snapshotter, computes image filesystem paths, maps runtime names to snapshotter/platform pairs, then returns the CRI image service.

## State And Persistence
The plugin itself is not persistent. It uses metadata DB content/image services and snapshotter state. `ImageFSPaths` are derived from plugin exports or root-directory conventions. Migration mutates the daemon config map before plugin initialization.

## Dependencies And Integration Points
Depends on metadata, lease, sandbox store, service, snapshot, transfer, and warning plugins. Integrates with `internal/cri/server/images`, CRI config validation, `platforms`, containerd client in-memory services, and snapshotter plugin metadata exports.

## Risks
Migration uses unchecked type assertions on config maps, so malformed legacy config can panic during daemon config migration. Runtime platform parsing is startup-fatal. Missing default snapshotter prevents CRI image service startup. Registry defaults are Linux-specific and can conflict with explicitly configured mirrors if validation is bypassed.

## Test Signals
`plugin_test.go` verifies sandbox image and registry config migration. Broader behavior is covered indirectly by CRI image service and daemon integration tests.
