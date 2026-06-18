<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/layer.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/layer.go

Purpose: converts graphdriver snapshots into registered Moby layers for BuildKit cache use.

Important APIs and control flow: `GetDiffIDs` returns existing layer diff chains when a key already maps to a layer. `EnsureLayer` serializes conversion per key, returns existing diff IDs when present, rejects active snapshots, recursively ensures the parent layer, computes diffID and size for the graphdriver ID into a temporary tar-split path, registers the graph ID as a layer with parent chain ID, records the chain ID in Bolt, caches the layer ref, and returns the full diff chain. `getDiffChain` walks parents recursively. `getGraphID` extracts graphdriver cache IDs from layers that expose `CacheID`.

State and persistence: reads/writes snapshot Bolt metadata, temporary tar-split files, layer-store registrations, and in-memory layer refs.

Dependencies and integration: used by the graphdriver BuildKit snapshotter and exporter/differ paths. Depends on layer store graph ID registration and checksum calculation extensions.

Risks: parent chain ID is assigned from a goroutine while another goroutine computes checksum; errors are coordinated by errgroup, but shared variables rely on completion before use. Active snapshots cannot be converted. Correct tar-split cleanup depends on temp directory removal.

Test signals: no direct tests in this subset; BuildKit graphdriver cache/export tests cover conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/layer.go -->
