<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_push.go -->
# sources/cloud-native/moby/daemon/containerd/image_push.go

Purpose: implements Docker image push through containerd, including all-tags push, platform-specific descriptor selection, cross-repository blob mount optimization, progress reporting, fallback from index to manifest when content is missing, distribution source labeling, and event/metric reporting.

Important APIs and flow: `PushImage` handles multi-platform rejection, all-tags repository push, and single-ref push. `pushRef` creates a lease, resolves the image tag, selects a target descriptor with `getPushDescriptor` when a platform is requested, builds resolver/status tracking, finds missing mountable blobs, wraps the content store to fake mountable blob metadata, pushes content with `remotes.PushContent`, retries an index push as a platform manifest on missing content, emits aux messages for fallback or missing content, appends distribution source labels, and logs events. `getPushDescriptor` walks reachable manifests, ignores attestations, filters by availability and platform, and decides between whole index, one manifest, not-found, or conflict. `findMissingMountable`, `getDigestSources`, `extractDistributionSources`, `distributionSource`, and `canBeMounted` implement cross-repo mount discovery.

State and persistence: read-mostly over image/content metadata, but it updates content labels after a successful push so future pushes can mount shared blobs from the target registry. It uses leases to protect pushed descriptors during traversal.

Dependencies and integration: depends on resolver/auth construction, progress jobs, fake content store wrapper, containerd remotes, Docker reference parsing, containerd distribution source labels, platform matchers, `ImageManifest`, and registry error translation.

Risks: descriptor selection is nuanced for partial multi-platform indexes and host platform preference. Fake content `Info` enables cross-repo mounts but `ReaderAt` still fails, so correctness depends on containerd remotes using labels for mounts rather than reading missing content. Distribution source labels strip target registry ports before comparison, which may conflate registries in unusual deployments. Multiple matching manifests without explicit platform can conflict.

Test signals: `image_push_test.go` exercises `getPushDescriptor` across all-present, partial, explicit platform, daemon-platform, ARM variant, not-found, and conflict cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_push.go -->
