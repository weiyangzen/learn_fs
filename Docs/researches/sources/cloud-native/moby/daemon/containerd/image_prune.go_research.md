<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_prune.go -->
# sources/cloud-native/moby/daemon/containerd/image_prune.go

Purpose: implements Docker image prune for the containerd-backed image store, including filter handling, lease cleanup, container-use protection, image metadata deletion, and reclaimed-space reporting.

Important APIs and flow: `ImagePrune` enforces a single active prune with `pruneRunning`, validates filters, interprets `dangling` defaulting to true, removes dangling filter values before calling `setupFilters`, deletes expiring pull leases labeled for prune, and delegates to `pruneUnused`. `pruneUnused` lists images, counts references per target digest, selects dangling or all unused candidates, removes candidates used by containers, preserves the last reference to a digest used by ID/digest-created containers, and calls `pruneAll`. `filterImagesUsedByContainers` protects dangling names, exact tags, ID-created containers, and tag+digest cases. `pruneAll` walks present children for size accounting, deletes image records synchronously, logs untag/delete events, and checks which blobs disappeared.

State and persistence: deletes containerd image records and may trigger content garbage collection via synchronous delete. It also deletes pull leases marked with `moby/prune.images`, using synchronous deletion for the final lease. The report is derived after deletion by probing content availability.

Dependencies and integration: reuses list filters and label filters, daemon container store, containerd leases/images/content, tracing spans, Docker event logging, and dangling image naming.

Risks: prune behavior depends on containerd GC timing and content availability after image delete. It walks blobs before deletion, so concurrent changes can skew `SpaceReclaimed`. Container reference protection is subtle for ID, truncated ID, tag, and tag+digest forms. Context cancellation returns accumulated errors early only for cancellation/deadline cases.

Test signals: no direct test file in this subset; behavior is indirectly related to image delete/list helpers. High-value missing tests include concurrent prune rejection, container reference preservation, label/until filters, and content reclaimed accounting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_prune.go -->
