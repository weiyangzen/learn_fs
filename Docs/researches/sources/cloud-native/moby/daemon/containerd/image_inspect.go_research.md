<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_inspect.go -->
# sources/cloud-native/moby/daemon/containerd/image_inspect.go

Purpose: implements Docker image inspect against the containerd image/content/snapshot model, including manifest summaries, repo tags/digests, config fields, rootfs diff IDs, size, and optional identity data.

Important APIs and flow: `ImageInspect` resolves a reference or ID, finds all image records with the same target digest, calculates last tag time, builds a requested/default platform matcher, calls `size` and `multiPlatformSummary`, optionally selects the platform-specific target, and fills `imagebackend.InspectData`. `collectRepoTagsAndDigests` deduplicates Docker-style familiar tags and digests while skipping synthetic dangling references. `size` dispatches through descriptor children with a small semaphore and platform limiting.

State and persistence: inspect is read-only but consumes mutable containerd metadata and content. It reads image labels for the classic builder parent, image config JSON for Docker fields, and content descriptor sizes. Missing config content is tolerated in some paths to keep partial images inspectable.

Dependencies and integration: integrates with image resolution, platform matching, `multiPlatformSummary`, image identity cache helpers, containerd children handlers, Docker reference normalization, and API storage driver metadata. The graph-driver legacy field is populated with the snapshotter name for older API compatibility.

Risks: image records can change between resolve and list, producing `errInconsistentData`. Size calculation ignores missing child content except non-not-found errors, which favors partial-image visibility over strict integrity. Platform-specific inspect changes the returned descriptor/ID to the chosen manifest, which must remain aligned with Docker API expectations. Malformed image names are logged but still returned in repo tags for list compatibility.

Test signals: `image_inspect_test.go` covers missing multi-platform blobs, missing layer blobs, optional manifest output, and explicit platform selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_inspect.go -->
