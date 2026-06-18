<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/migration/migration.go -->
# sources/cloud-native/moby/daemon/containerd/migration/migration.go

Purpose: migrates legacy graphdriver images/layers into containerd content, image metadata, and snapshots.

Important APIs and flow: `LayerMigrator` holds legacy layer/reference/image stores plus containerd leases/content/images. `NewLayerMigrator` wires dependencies. `MigrateTocontainerd` supports overlay2 and vfs, creates a 24-hour lease, iterates Docker image heads, converts each legacy layer tar stream to compressed zstd content in parallel, copies each graphdriver upper/source directory into a prepared snapshot, commits snapshots by chain ID, writes the image config blob with snapshot GC labels, writes the manifest blob with content GC labels, maps children labels, and creates tagged or dangling containerd image records from legacy references. `extractSource` finds the writable source path from bind or overlay mounts.

State and persistence: writes new containerd content blobs, snapshot records/filesystem trees, image records, and temporary leases. It reads legacy graphdriver layer directories and legacy image/ref stores.

Dependencies and integration: bridges Moby legacy `layer.Store`, `refstore.Store`, and `image.Store` to containerd content/images/snapshots. Depends on containerd compression, content writers, snapshot labels, OCI manifests, and continuity `fs.CopyDir`.

Risks: migration is large and partially parallel; if a layer conversion goroutine fails after snapshots/content are written, cleanup is not comprehensive. Only overlay2/vfs and single-source bind/overlay snapshot mounts are supported. Zstd compression is hard-coded. Snapshot parent tracking must match diff ID chain order. Existing tags are skipped if already present, which can leave mixed old/new state.

Test signals: no direct tests in this subset; migration needs integration tests against real legacy stores and snapshotters.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/migration/migration.go -->
