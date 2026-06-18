<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/transport/pool.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/transport/pool.go

Purpose: caches authenticated registry transports and resolves blob URLs, including redirect targets, for efficient remote blob access.

Important APIs/types: `Pool`, `NewPool`, `Resolve` interface, `Pool.Resolve`, and `redirect`. `Pool` holds an LRU of up to 3000 transports keyed by reference name plus a base `http.DefaultTransport`.

Control flow and state: `Resolve` builds a `/v2/<repo>/blobs/<digest>` URL, checks the transport cache, and validates cached transports by issuing a range GET through `redirect`. If cached redirect fails, it removes the cache entry, authenticates a new transport via `registry.AuthnTransport`, resolves redirect again, and caches the transport. `redirect` sends `Range: bytes=0-0`, accepts 2xx as the original endpoint and 3xx with `Location` as the redirected URL, drains the response body, and errors otherwise.

Dependencies/integration: uses go-containerregistry references/keychains, registry auth helper, groupcache LRU, HTTP, and containerd logging. It supports remote content fetch optimization.

Risks and test signals: `Resolve` holds the mutex across network calls, serializing all resolutions and making slow registries block unrelated refs. It keys cache by full ref name, not registry/repository scope alone. `pool_test.go` covers cache reuse and invalidation on redirect failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/transport/pool.go -->
