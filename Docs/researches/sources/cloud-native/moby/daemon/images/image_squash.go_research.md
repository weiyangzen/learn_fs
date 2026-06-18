<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_squash.go -->
# sources/cloud-native/moby/daemon/images/image_squash.go

Purpose: creates a new squashed image by replacing the diff between an image and optional parent with a single layer.

Important APIs and control flow: `SquashImage` loads target and optional parent images, obtains the target root layer, streams the diff from the parent chain with `TarStreamFrom`, registers a new layer over the parent chain, copies and rewrites the image rootfs/history, marks intervening history entries as empty layers, appends a squash history entry, marshals the new config, and creates a new image.

State and persistence: reads existing images and layers, writes a new layer and image record. It does not delete or retag the original images.

Dependencies and integration: uses internal image/layer stores and is exposed through the daemon image-service interface for legacy squash support.

Risks: mutating history/rootfs correctness depends on parent ancestry matching the target. The new image is untagged unless a later caller tags it. Layer references must be released after streaming/registering.

Test signals: no direct tests in this subset; squash integration tests are the likely coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_squash.go -->
