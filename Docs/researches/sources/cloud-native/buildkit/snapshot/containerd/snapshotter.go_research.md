## sources/cloud-native/buildkit/snapshot/containerd/snapshotter.go

Purpose: adapts containerd snapshotters into BuildKit snapshotters while forcing all operations into a configured namespace and forbidding direct remove through the namespace wrapper.

Important APIs/types/functions: `NewSnapshotter` returns BuildKit `snapshot.Snapshotter` by wrapping `nsSnapshotter` with `snapshot.FromContainerdSnapshotter`. `NSSnapshotter` exposes the namespace wrapper as a containerd `snapshots.Snapshotter`. `nsSnapshotter` embeds `snapshots.Snapshotter` and overrides methods to inject namespace into context. `Remove` returns an error.

Control flow: each method creates a namespaced context then delegates to the embedded snapshotter. `Prepare` and `View` return containerd mounts directly. `Remove` is blocked to prevent unsafe deletion through this adapter.

State and persistence: wrapper only stores namespace and underlying snapshotter. Snapshot metadata/layers persist in containerd.

Dependencies and integration points: integrates containerd snapshotters with BuildKit's snapshot abstraction and optional identity mapping.

Risks and test signals: callers needing removal must use the intended GC/lifecycle path, not this wrapper. Namespace injection is easy to miss if methods are added to the interface later. Tests are indirect through snapshotter/merge behavior.
