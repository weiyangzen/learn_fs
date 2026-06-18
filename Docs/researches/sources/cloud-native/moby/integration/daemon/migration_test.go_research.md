# sources/cloud-native/moby/integration/daemon/migration_test.go

Purpose: Linux integration tests for migrating from graphdriver storage to containerd snapshotters and preserving image usability through save/load after migration.

Important APIs and helpers: `TestMigrateOverlaySnapshotter`, `TestMigrateNativeSnapshotter`, `testMigrateSnapshotter`, and `TestMigrateSaveLoad`. They use daemon feature flag `containerd-migration`, env `DOCKER_MIGRATE_SNAPSHOTTER_THRESHOLD`, frozen image loading, container helpers, `ImageSave`, `ImageLoad`, and `ImageRemove`.

Control flow: migration tests start a daemon with `overlay2` or `vfs`, capture daemon ID and image count, load busybox, create a running container, then restart with migration enabled. With a container present, migration should be blocked and storage driver unchanged. After removing the container, restart with migration enabled should switch to the expected snapshotter while preserving image count and daemon ID. Save/load test migrates, saves busybox, removes all images, reloads the archive, and runs a container from the loaded image.

State and persistence: validates daemon root metadata across storage-backend migration: daemon ID, image count, image content, and container blockers. It also validates exported archive compatibility after migration.

Dependencies and integration: depends on Linux, storage drivers, containerd snapshotter support, frozen image fixtures, daemon restart semantics, and image save/load APIs.

Risks: migration behavior is gated by environment variables and active containers. Tests are slow and host-storage sensitive. They assume the selected graphdriver/snapshotter pair is available.

Test signals: strong regression signal for safe migration gating, persistence of daemon identity and images, and post-migration image execution plus archive round-trip behavior.
