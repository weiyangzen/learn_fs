<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_pull.go -->
# sources/cloud-native/moby/daemon/containerd/image_pull.go

Purpose: implements registry pull through containerd while preserving Docker API progress, leases, platform selection, dangling old-image retention, snapshot unpacking, referrer discovery, and registry error translation.

Important APIs and flow: `PullImage` rejects multiple platforms, creates a cancellable lease, pulls one tag or enumerates all tags for a name-only reference. `pullTag` configures media type ref-key prefixes, resolver/auth, old image preservation lease, platform matcher, progress jobs, layer/status handlers, pull unpack options, snapshotter info labels, and referrer provider/wrapper before calling `client.Pull`. It removes obsolete dangling refs, logs events, and warms the identity cache on success. `joinHandlerWrappers` composes containerd handler wrappers. `referrersForPull` and `referrersList` track inline attestation/referrer descriptors and fetch Sigstore referrers when needed. `parseSubject`, `writeStatus`, and `isModelMediaType` support subject parsing, Docker-compatible status output, and AI model warning behavior.

State and persistence: writes pulled content, image metadata, unpacked snapshots, snapshotter labels, temporary leases, dangling references for replaced images, and identity-cache state. A canceled cancellable lease may remain until expiration/prune.

Dependencies and integration: containerd remote pull/unpack, Moby registry tag enumeration, resolver/auth helpers, progress subsystem, snapshotter append-info handler, BuildKit attestation annotations, policy-helper media types, metrics, and Docker event logging.

Risks: referrer handling includes TODO-filtered provenance logic and registry-specific workarounds. Pull can leave old content protected as dangling if a new digest replaces it. Missing/unsupported platforms are translated from containerd errors by string inspection. AI model media types warn but are still processed by pull. Progress ordering depends on deferred final updates after the progress goroutine stops.

Test signals: load/provenance/list tests validate local outcomes of partial/multi-platform/referrer-style content, but direct registry pull/referrer/auth progress tests are outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_pull.go -->
