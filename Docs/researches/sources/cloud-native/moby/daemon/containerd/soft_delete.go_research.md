<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/soft_delete.go -->
# sources/cloud-native/moby/daemon/containerd/soft_delete.go

Purpose: preserves image content reachability when tags are replaced or deleted by creating synthetic dangling image records.

Important APIs and flow: `softImageDelete` creates a dangling image if the deleted image is the last reference to its target, then deletes the original name using a non-cancelable context. `ensureDanglingImage` copies the image metadata, strips name-related labels, renames it to `moby-dangling@<digest>`, and creates it if absent. `danglingImageName` and `isDanglingImage` define the synthetic naming convention.

State and persistence: creates and deletes containerd image records. Does not delete content directly; it protects target descriptors from becoming unreachable until prune/delete logic removes the dangling record.

Dependencies and integration: used by tag replacement, pull replacement, list hiding/filtering, prune, and inspect tag/digest collection.

Risks: the dangling convention is name-based and a TODO notes no expiration check. A failure to create the dangling image aborts replacement to avoid content loss. Concurrent references can make `len(imgs) == 1` stale.

Test signals: indirect behavior appears in list/prune/tag paths; no direct unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/soft_delete.go -->
