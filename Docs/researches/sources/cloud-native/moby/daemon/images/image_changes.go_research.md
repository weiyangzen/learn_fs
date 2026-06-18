<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_changes.go -->
# sources/cloud-native/moby/daemon/images/image_changes.go

Purpose: returns filesystem changes for a container's writable layer.

Important APIs and control flow: `ImageService.Changes` locks the container, validates that `RWLayer` is present and implements `layer.RWLayer`, then returns `rwLayer.Changes()`.

State and persistence: reads the container's RW layer state through the layer store; no state is written.

Dependencies and integration: used by daemon change/diff APIs and depends on container locking plus the archive change model.

Risks: the function holds the container lock while calling `Changes`, so slow graphdriver operations can extend lock hold time. Unexpected RW layer types produce explicit errors.

Test signals: direct tests are not in this subset; daemon changes tests exercise this path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_changes.go -->
