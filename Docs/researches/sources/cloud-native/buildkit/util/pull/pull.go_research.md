<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/pull/pull.go -->
# sources/cloud-native/buildkit/util/pull/pull.go

Purpose: resolves and pulls image manifests and non-layer metadata while deliberately skipping layer blob downloads so lazy layer providers can fetch layer content later.

Important APIs and types: `SessionResolver`, `Puller`, `PulledManifests`, `Puller.PullManifests`, provider `ReaderAt`, `filterLayerBlobs`, and `getLayers`.

Control flow: `Puller.resolve` flightcontrols remote/local resolution and caches the descriptor or error. `tryLocalResolve` resolves digest-pinned content from the content store when it has matching distribution source labels. `PullManifests` resolves the reference, constructs platform-filtered image handlers, fetches only metadata/config/nonlayer descriptors through `images.Dispatch`, rejects Docker schema1 manifests, derives layer descriptors and diffID annotations through `getLayers`, and returns a session-aware content provider for later fetches.

State and persistence: `Puller` caches resolution state, descriptors, layer and nonlayer lists, and errors in memory. Content persistence happens through the provided containerd content store, distribution source labels, and fetch handlers.

Dependencies and integration: integrates with containerd content/images/remotes/docker, BuildKit sessions, flightcontrol, image media detection, resolver concurrency limiting, retry handler, and progress logging. The returned provider calls session-specific resolvers to fetch blobs.

Risks: `resolveErr` is cached except for context cancellation; transient non-cancel errors can poison a `Puller` instance. Metadata map is protected because containerd dispatch handlers may run in parallel. Lazy layer semantics depend on `filterLayerBlobs` recognizing all layer media types.

Test signals: no direct tests in this subset; behavior is typically covered by image pull/integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/pull/pull.go -->
