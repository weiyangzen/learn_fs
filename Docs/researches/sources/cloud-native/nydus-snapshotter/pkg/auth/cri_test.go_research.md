# sources/cloud-native/nydus-snapshotter/pkg/auth/cri_test.go

Purpose: validates that the CRI provider can capture credentials from proxied CRI `PullImage` requests and later return them by image reference.

Important APIs and functions: `MockImageService` implements `runtime.ImageServiceServer` enough to accept `PullImage`; `TestFromImagePull` sets up a downstream mock CRI Unix socket, a proxy CRI Unix socket through `AddImageProxy`, then uses a CRI client to perform image pulls with `runtime.AuthConfig`.

Control flow: the test first asserts `NewCRIProvider().GetCredentials` fails before any proxy is registered. It then starts a mock real ImageService, starts the proxy server registered by `AddImageProxy`, checks that no credentials exist before pulling, sends `PullImage` calls with username/password auth, and checks that later lookups return the captured credentials for matching refs and fail for a wrong tag. It repeats for another registry and a digest-pinned image.

State and persistence: the test exercises the package-global `credentials` slice and the stargz CRI keychain's in-memory capture store. Temporary Unix sockets are under `t.TempDir`; gRPC servers are stopped with defers.

Dependencies and integration points: uses real gRPC servers over Unix sockets, containerd's dialer, Kubernetes CRI API types, and the production `AddImageProxy` path. This is closer to an integration test than a pure unit test.

Risks and gaps: the package global `credentials` is not reset by the test, so test order or repeated runs in the same process can retain state. The test does not run concurrent calls and does not check malformed refs, proxy downstream failure propagation, or resolver error behavior.

Test signals: verifies tag refs, digest refs, multiple registries, empty-before-pull behavior, and wrong-tag miss behavior.
