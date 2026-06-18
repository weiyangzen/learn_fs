# sources/cloud-native/nydus-snapshotter/export/snapshotter/snapshotter.go

Purpose: register Nydus as an in-process containerd snapshot plugin.

Flow: `init` registers plugin type `SnapshotPlugin` with ID `nydus`, default platform metadata, config type `SnapshotterConfig`, default filling, and `snapshot.NewSnapshotter` initialization.

State/dependencies: modifies containerd plugin registry at package import time. Depends on containerd plugin APIs, platforms, config, and snapshot package.

Integration points: enables embedding Nydus snapshotter directly in containerd rather than only via remote proxy plugin.

Risks/tests: root property handling appears inverted: `if root == "" { cfg.Root = root }` sets empty root only when property is absent, likely not intended. No direct tests in this subset.
