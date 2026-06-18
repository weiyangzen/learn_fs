<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/plugin/plugin.go -->
# sources/cloud-native/containerd/plugins/snapshots/overlay/plugin/plugin.go

## Purpose
Registers the Linux `overlayfs` snapshotter plugin and maps daemon config into overlay snapshotter options and advertised capabilities.

## Important APIs, Types, And Functions
`Config` exposes `root_path`, `upperdir_label`, `sync_remove`, `slow_chown`, and `mount_options`. Capability constants are `remap-ids`, `only-remap-ids`, and `rebase`.

## Control Flow
The initializer sets the default platform, validates config, chooses root, enables upperdir labels if requested, enables async removal unless `sync_remove` is true, passes configured mount options, probes ID-mapped mount support, and handles slow-chown capability signaling. It advertises `rebase` only outside user namespaces because whiteout conversion needs `mknod`.

## State And Persistence
Exports the snapshotter root and delegates persistent metadata/directory creation to `overlay.NewSnapshotter`.

## Dependencies And Integration Points
Integrates with the plugin registry, containerd plugin constants, `platforms.DefaultSpec`, moby userns detection, overlayutils capability probing, and the overlay snapshotter package.

## Risks And Edge Cases
Capability metadata affects higher-level unpack/rebase behavior. If ID-mapped mount probing fails and `slow_chown` is false, the plugin signals `only-remap-ids` without `remap-ids`, restricting user namespace workflows.

## Test Signals
Indirectly covered by overlay tests and daemon plugin initialization; capability combinations are not exhaustively unit tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/plugin/plugin.go -->
