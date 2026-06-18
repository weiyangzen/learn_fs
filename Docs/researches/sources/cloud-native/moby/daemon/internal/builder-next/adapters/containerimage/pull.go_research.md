<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/containerimage/pull.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/adapters/containerimage/pull.go

Purpose: implements a BuildKit image source backed by Moby's legacy image/layer stores and containerd content store.

Important APIs and control flow: `Source` exposes the Docker image scheme, parses image identifiers and attributes, resolves local refs from Moby ref/image stores, resolves remote configs with BuildKit/containerd resolver flightcontrol, and creates `puller` source instances. `puller.CacheKey` prefers local config or manifest digest keys and falls back to remote resolution. `Snapshot` reuses local image layers via BuildKit cache refs when possible; otherwise it creates a temporary lease, fetches manifests/configs/layers with containerd handlers, streams download/extract progress, downloads layers through Moby's layer download manager, gets cache refs by diff IDs, leases non-layer content to the ref, and sets optional usage record types. `layerDescriptor` adapts remote descriptors to Moby layer download descriptors. Helpers handle progress status, cache keys from config chain IDs, platform matching, and source policy mutation.

State and persistence: reads Moby image/reference/layer stores, writes containerd content blobs, metadata V2 layer digest mappings, BuildKit cache refs, temporary leases, and possibly triggers garbage collection. It keeps in-memory singleflight/flightcontrol state for resolution.

Dependencies and integration: bridges BuildKit source, solver, cache, sessions, source policies, containerd remotes/content/images/leases, Moby distribution download manager, V2 metadata, and legacy image/layer stores.

Risks: this is lifecycle-heavy code: progress goroutines, temporary leases, cache refs, release callbacks, and background GC must stay ordered. Schema1 manifests are rejected. Local platform matching uses Docker's variant fallback, while remote resolution uses OCI platform filtering. The legacy store cannot represent multi-arch tags well, so cache keys and local reuse must be conservative.

Test signals: no direct tests in this subset. The attempted local `go test` could not run because `go` is not installed in the workspace environment. BuildKit build/pull integration tests are the expected coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/containerimage/pull.go -->
