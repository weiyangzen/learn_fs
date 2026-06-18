<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/config.go -->
# sources/cloud-native/stargz-snapshotter/service/config.go

## Purpose
Defines the top-level service configuration shape for stargz snapshotter, embedding filesystem settings and adding keychain, resolver, and snapshotter-specific options.

## Important APIs, Types, And Functions
- `Config` embeds `fs/config.Config`, `KubeconfigKeychainConfig`, `CRIKeychainConfig`, `ResolverConfig`, and `SnapshotterConfig`.
- `KubeconfigKeychainConfig` controls Kubernetes secret-backed credentials and kubeconfig path.
- `CRIKeychainConfig` controls CRI PullImage auth capture and CRI image service/listen sockets.
- `ResolverConfig` aliases `service/resolver.Config`.
- `SnapshotterConfig.AllowInvalidMountsOnRestart` lets startup continue when remote snapshot remounting fails.

## Control Flow
This file has no executable flow; it provides TOML/JSON-tagged structs consumed by plugin and service constructors.

## State And Persistence
Configuration fields determine persistent roots, registry behavior, credential sources, and snapshotter recovery policy. The file itself stores no state.

## Dependencies And Integration Points
Couples the service package to `fs/config` and resolver configuration. `plugincore.RegisterPlugin` and `service.NewStargzSnapshotterService` consume these fields during containerd plugin initialization.

## Risks And Edge Cases
Embedded structs flatten configuration fields, so TOML layout and backward compatibility need care. `AllowInvalidMountsOnRestart` can leave unusable remote snapshots in containerd metadata that users must remove manually.

## Test Signals
Signals are mostly integration-level: config TOML should unmarshal into these structs, keychain/resolver toggles should alter plugin setup, and restart behavior should match `AllowInvalidMountsOnRestart`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/config.go -->
