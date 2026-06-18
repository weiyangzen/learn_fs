## sources/cloud-native/stargz-snapshotter/fs/fs_test.go

Purpose: unit-tests `filesystem.Check` behavior with a controllable fake layer.

Important APIs and helpers: `TestCheck` creates a `filesystem` with one mountpoint mapped to `breakableLayer`, a small background task manager, and default-label source resolver. `breakableLayer` implements the full `layer.Layer` interface with success/failure switches for `Check` and `Refresh`; other methods are stubs returning failures or nil as needed.

Control flow: first the fake layer succeeds, and `fs.Check` must return nil. Then the fake layer fails, and `fs.Check` must return an error. Because `Info` reports `Size: 1` and default `FetchedSize: 0`, `Check` exercises connectivity/refresh logic before prefetch waiting.

State and persistence: in-memory fake layer state only (`success bool`). No mounts, FUSE server, disk cache, or remote registry are used.

Dependencies and integration points: depends on `fs/layer.Layer`, `fs/source`, `task.BackgroundTaskManager`, and containerd reference/registry host types to satisfy the check path. The fake ensures interface compatibility with the production layer contract.

Risks: coverage is narrow. It does not test a missing mountpoint, successful refresh after initial failure, prefetch wait warning semantics, noprefetch behavior, or actual label-driven source refresh. Stubs can hide interactions with real layer state and metrics.

Test signals: basic regression signal that `Check` consults layer connectivity and propagates hard refresh failures.
