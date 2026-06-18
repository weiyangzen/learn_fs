<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_tag.go -->
# sources/cloud-native/moby/daemon/containerd/image_tag.go

Purpose: implements Docker image tagging for the containerd-backed image store, including replacement and dangling preservation semantics.

Important APIs and flow: `TagImage` resolves an image ID/reference to a target descriptor and calls `createOrReplaceImage` with a new image name and copied labels. `createOrReplaceImage` first attempts create, handles already-exists by resolving the existing reference set, no-ops if the target digest is unchanged, soft-deletes the replaced image otherwise, then creates the new record without cancellation. After successful non-dangling creation it logs a tag event, deletes any synthetic dangling name for the same digest, and warms the identity cache.

State and persistence: creates/deletes containerd image records, may create a synthetic dangling record for a replaced last reference via `softImageDelete`, deletes stale dangling records, and updates identity cache state.

Dependencies and integration: uses image resolution helpers, soft-delete helpers, Docker references, containerd image store, event logging, and identity cache warming.

Risks: replacement is multi-step and relies on non-cancelable cleanup to avoid losing the old digest. Concurrent tag operations can race between create/delete/create. Label copying carries source labels onto the new tag, except dangling creation strips name labels in `soft_delete.go`.

Test signals: lookup tests cover reference resolution, but direct tag replacement/dangling behavior is not covered in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_tag.go -->
