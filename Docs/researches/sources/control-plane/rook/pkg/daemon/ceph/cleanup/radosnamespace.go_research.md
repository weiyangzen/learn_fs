<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/radosnamespace.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/radosnamespace.go

Purpose: removes RBD images, snapshots, trash entries, and active clients for either a `CephBlockPoolRadosNamespace` or an entire `CephBlockPool`.

Important APIs/types/functions: `RadosNamespaceCleanup`, `cleanupImages`, `BlockPoolCleanup`, `blocklistClients`, `getClients`, and constant `ClientBlocklistDuration` set to `1200` seconds.

Control flow: cleanup lists images in the pool/namespace, blocklists all watchers found from image status, then for each image lists and deletes snapshots, moves the image to trash, and schedules trash deletion by image ID. Errors per image/snapshot are logged and accumulated in `retErr`, while blocklist/list failures abort earlier.

State and persistence behavior: no local state persists, but Ceph cluster state is changed through RBD snapshot deletion, image trash operations, trash-removal tasks, and blocklist entries. The client set is a Kubernetes `sets.Set[string]` used for deduplication.

Dependencies and integration points: depends on `clusterd.Context`, Ceph client helpers for RBD/rados namespace operations, and Rook cleanup logging. It is likely called during CR deletion finalization for block pools and Rados namespaces.

Risks: blocklisting every watcher can disrupt active clients; only the last per-image error is returned; trash move/delete ordering assumes image ID remains valid. Empty namespace and pool cleanup share the same path, so namespace argument formatting must stay correct.

Test signals: no-image cleanup, snapshot deletion, namespace vs pool command paths, watcher deduplication and blocklist failures, partial failure accumulation, and trash task command construction.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/radosnamespace.go -->
