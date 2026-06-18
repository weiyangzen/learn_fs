<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_commit.go -->
# sources/cloud-native/moby/daemon/images/image_commit.go

Purpose: creates image records from container writable-layer diffs and provides a builder-specific commit shim.

Important APIs and control flow: `CommitImage` exports the container RW layer as a tar stream, resolves or creates the parent image, registers a new layer over the parent chain, builds a child image config, creates the image, logs a create event, marks it built locally, and records its parent. `exportContainerRw` gets, mounts, streams, unmounts, and releases the RW layer with cleanup on errors. `CommitBuildStep` looks up a container and fills mount label, OS, and parent image before delegating to `CommitImage`.

State and persistence: writes new layer-store layer data, image-store config records, built-locally metadata, parent links, and image events. It reads container store and existing parent image state.

Dependencies and integration: integrates backend commit configs, layer tar streams, internal image config construction, ioutils read-closer wrappers, and daemon events.

Risks: mount/unmount/release sequencing is error-prone; `exportContainerRw` must keep releasing on both happy and error paths. `CommitBuildStep` intentionally bypasses normal container-state validation, which is acceptable only for the legacy builder shim.

Test signals: no direct tests here; commit and builder integration tests cover behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_commit.go -->
