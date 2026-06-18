<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/plugin/plugin.go -->
# sources/cloud-native/containerd/plugins/snapshots/native/plugin/plugin.go

## Purpose
Registers the native snapshotter plugin and maps optional root-path configuration to `native.NewSnapshotter`.

## Important APIs, Types, And Functions
`Config` has `RootPath`. `init` registers snapshot plugin ID `native`.

## Control Flow
The initializer appends the default platform, validates `Config`, chooses configured root or `plugins.PropertyRootDir`, exports the root directory metadata, and constructs the native snapshotter.

## State And Persistence
The plugin itself stores no state. The snapshotter creates `metadata.db` and snapshot directories under the selected root.

## Dependencies And Integration Points
Integrates with containerd plugin registry, `plugins.SnapshotPlugin`, `plugins.SnapshotterRootDir`, `platforms.DefaultSpec`, and the native snapshotter package.

## Risks And Edge Cases
Mis-typed config returns an initialization error. Root path override can place snapshotter state outside the daemon plugin root, which is intentional but operationally significant.

## Test Signals
Indirectly covered through daemon plugin initialization and native snapshotter tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/plugin/plugin.go -->
