# sources/cloud-native/moby/integration/daemon/default_storage_test.go

Purpose: integration tests for storage backend defaults, graphdriver persistence, and inspect API compatibility between graphdriver and containerd snapshotter modes.

Important APIs and helpers: `TestDefaultStorageDriver`, `TestGraphDriverPersistence`, and `TestInspectGraphDriverAPIBC` use the daemon harness, `Info`, `ImageInspect`, `ContainerInspect`, `client.WithAPIVersion`, and storage response types.

Control flow: default storage clears storage-driver environment overrides, starts a daemon, and checks driver status identifies containerd snapshotter mode. Persistence starts with explicit `overlay2`, loads busybox, creates a container, stops, restarts without explicit storage-driver flags, and verifies the daemon remains on the same graphdriver with image/container data intact. API compatibility table-drives current vs older API behavior and graphdriver vs snapshotter storage, then inspects image/container GraphDriver and Storage fields.

State and persistence: validates daemon root storage selection across restart, image and container metadata persistence, and API response shape stability for clients that expect `GraphDriver` or the newer `Storage.RootFS.Snapshot` field.

Dependencies and integration: depends on Linux sub-daemons, storage driver availability, busybox frozen image loading, client API version negotiation, and Moby storage response structs.

Risks: storage driver availability can vary by host. The tests intentionally clear env vars to avoid external overrides, but host filesystem/kernel support still affects `overlay2` and `vfs` behavior.

Test signals: verifies no unexpected auto-migration from graphdriver to snapshotter, default containerd snapshotter selection, and backward-compatible inspect fields across API versions.
