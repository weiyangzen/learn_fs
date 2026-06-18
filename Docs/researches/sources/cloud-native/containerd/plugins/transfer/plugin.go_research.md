<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin.go -->
# sources/cloud-native/containerd/plugins/transfer/plugin.go

## Purpose
Registers the local transfer service plugin and builds its configuration from leases, metadata, image verifiers, snapshotters, differs, registry config, and unpack platform rules.

## Important APIs, Types, And Functions
Plugin ID is `local` under `plugins.TransferPlugin`. Key functions are `configureUnpackPlatforms`, `getApplier`, and `defaultConfig`. Config types are `transferConfig` and `unpackConfiguration`.

## Control Flow
Initialization obtains metadata and lease plugins, collects optional image verifier plugins, applies concurrency settings, configures unpack platforms, sets registry config path and duplication suppressor, then constructs `local.NewTransferService`. `configureUnpackPlatforms` defaults unpack config when nil, parses platforms, resolves snapshotters, obtains snapshotter exports/capabilities, chooses an applier, and appends `unpack.Platform` entries. `getApplier` uses explicit differ selection when configured or scans diff plugins by supported platform, preferring the default differ when multiple match.

## State And Persistence
The plugin itself persists no state. It passes the metadata DB content/image stores and snapshotter references into the local transfer service. The duplication suppressor is an in-memory keyed mutex.

## Dependencies And Integration Points
Requires lease, metadata, diff, image verifier, and snapshot plugins. Imports transfer archive/image/registry packages for type registration. Integrates with platform matching, errdefs, defaults, unpack, and local transfer APIs.

## Risks And Edge Cases
Optional unpack entries are skipped when snapshotters or differs are missing; required entries fail initialization. Auto differ selection can be ambiguous, with warnings and default preference. `CheckPlatformSupported=false` broadens matching to OS-only, which can unpack for architectures not explicitly supported by a snapshotter.

## Test Signals
`plugin_test.go` covers optional/required differ skip and missing behavior plus auto differ skip. `plugin_linux_test.go` confirms default Linux config skips unavailable EROFS differ rather than failing all transfer initialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin.go -->
