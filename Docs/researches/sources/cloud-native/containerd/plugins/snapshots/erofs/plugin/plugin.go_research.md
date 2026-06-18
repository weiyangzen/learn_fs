<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin.go -->
# sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin.go

## Purpose
Registers the `erofs` snapshotter plugin and translates daemon TOML configuration into EROFS snapshotter options and plugin metadata.

## Important APIs, Types, And Functions
`Config` exposes `root_path`, `ovl_mount_options`, `enable_fsverity`, `set_immutable`, `default_size`, and `dmverity_mode`. `init` registers a `plugins.SnapshotPlugin` with ID `erofs`. Capability constants are `remap-ids` and `only-remap-ids`.

## Control Flow
At initialization, the plugin sets the default platform, validates `Config`, chooses `RootPath` or the plugin root property, appends EROFS options for overlay mount options, fsverity, immutable files, parsed default writable size, and dm-verity mode, then probes ID-mapped mount support. It always advertises `only-remap-ids` and `rebase`, and advertises `remap-ids` only when supported.

## State And Persistence
The plugin exports the snapshotter root via `plugins.SnapshotterRootDir`; persistent metadata and layer state are created by `erofs.NewSnapshotter`, not in this file.

## Dependencies And Integration Points
Integrates with `github.com/containerd/plugin/registry`, containerd plugin type constants, `platforms.DefaultSpec`, EROFS snapshotter options, and `docker/go-units` for size parsing. Platform probing is delegated to `supportsIDMappedMounts`.

## Risks And Edge Cases
Invalid `default_size` aborts plugin initialization. `dmverity_mode` parsing is deferred to the snapshotter. The plugin intentionally does not support overlay's slow recursive chown fallback, so callers relying on remapping need ID-mapped mount support.

## Test Signals
Indirectly covered through EROFS snapshotter tests and transfer default tests that expect optional EROFS differ/snapshotter configuration to skip when unavailable.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin.go -->
