# sources/cloud-native/nydus/smoke/tests/api_test.go

Purpose: smoke tests for nydusd API v1 and FUSE service behavior: status, metrics, prefetch, repeated submounts, nested mountpoint remount stat behavior, API mount, and hot config reload.

Important APIs/types: `APIV1TestSuite`, tests `TestDaemonStatus`, `TestMetrics`, `TestPrefetch`, `TestSubMountCache`, `TestNestedMountpointStatAfterRemount`, `TestMount`, `TestHotReloadConfig`, helper `buildLayer`, helper `visit`, and top-level `TestAPI`.

Control flow: tests build RAFS layers from generated texture files via `nydus-image`, create `tool.NydusdConfig`, mount nydusd, call APIs through `tool.Nydusd`, read files to generate metrics/prefetch/cache activity, mount/unmount child filesystems by API, and verify file trees. Hot reload fetches config for `/`, updates registry auth twice, and verifies reads through the API.

State and persistence: uses per-test work dirs, blob/cache/bootstrap paths, mount dirs, API sockets, generated layers, and nydusd runtime metrics. Submount test mounts and unmounts 300 unique child paths to exercise VFS index/cache turnover.

Dependencies and integration: integrates smoke `tool` package, texture/layer builders, snapshotter converter, nydusd binary/API, localfs backend, RAFS modes/cache settings, and FUSE mount behavior.

Risks: root/FUSE permissions required, async prefetch needs polling, metric opcode indexes can drift, submount loop is expensive, and `TestGenerateBlobcache`-style file reads rely on generated texture content. Nested stat behavior specifically guards stale entry invalidation after remount.

Test signals: daemon reaches `RUNNING`; global metrics flags and counters update after reads; blob-cache prefetch amount becomes positive; 300 mount/unmount cycles verify file trees; nested mountpoint can be statted immediately after remount; API-mounted RAFS verifies file tree; registry auth changes are observable.
