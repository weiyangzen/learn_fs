## sources/cloud-native/buildkit/snapshot/snapshotter.go

Purpose: defines BuildKit's snapshotter abstraction and adapters to and from containerd snapshotters.

Important APIs/types/functions: `Mountable` aliases executor mountable refs. `Snapshotter` interface adds name, BuildKit `Mountable` returns, close, and identity mapping to containerd snapshot operations. `FromContainerdSnapshotter` wraps a containerd snapshotter. `fromContainerd.Mounts/View` return `staticMountable`; `Commit` preserves inherited labels from active snapshots. `NewContainerdSnapshotter` adapts back to containerd API and tracks mount release callbacks. `getRedirectDirOption` and `setRedirectDir` disable overlay `redirect_dir` when needed.

Control flow: adapter methods delegate containerd operations and translate mount lists to mountables or vice versa. `containerdSnapshotter.returnMounts` records releases and applies redirect_dir options. `release` calls all stored release functions.

State and persistence: adapter state includes snapshotter name, idmap, release callbacks, and cached redirect_dir detection. Persistent snapshot state remains in underlying snapshotter.

Dependencies and integration points: central bridge between BuildKit executor/cache and containerd snapshotters. Redirect_dir handling protects diff correctness on Linux overlay.

Risks and test signals: `containerdSnapshotter` accumulates release callbacks until global release, so callers must call the returned release function. Redirect_dir detection is Linux-specific but guarded by stat/userns checks. Tests in snapshotter merge use this adapter.
