<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/push/push.go -->
# sources/cloud-native/buildkit/util/push/push.go

Purpose: pushes image content and manifests to a registry with BuildKit resolver/auth integration, deduplication, retries, concurrency limiting, and distribution source label updates.

Important APIs and types: `Pusher`, `Push`, `skipNonDistributableBlobs`, `annotateDistributionSourceHandler`, `childrenHandler`, `updateDistributionSourceHandler`, and `dedupeHandler`.

Control flow: `Push` normalizes target references, handles by-digest mode, builds an insecure registry host callback when requested, gets a pooled resolver, creates a masked pusher wrapper, traverses image children, pushes layers/configs with retry and concurrency limiting, records manifest descriptors separately, and finally pushes manifests in reverse stack order. Child traversal adds distribution-source annotations from explicit annotations and content labels.

State and persistence: persistent side effects are registry uploads and content-store distribution source label updates after successful layer pushes. In-memory state includes a manifest stack, dedupe cache, and flightcontrol group.

Dependencies and integration: uses containerd content/images/remotes/docker, BuildKit sessions, progress, logs, resolver pool/config, limited concurrency, retry handler, image media detection, and in-toto payload type handling.

Risks: comments note a race in distribution source label updates when concurrent pull/push jobs consume the same layer. `childrenHandler` assumes OCI manifest/index shape even for Docker mediatypes. By-digest mode rejects tagged refs to avoid ambiguous push targets.

Test signals: no direct tests in this subset; image push behavior is integration-heavy.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/push/push.go -->
