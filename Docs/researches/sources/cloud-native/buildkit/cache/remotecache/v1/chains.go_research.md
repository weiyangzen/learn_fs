# sources/cloud-native/buildkit/cache/remotecache/v1/chains.go

## Purpose

This file defines the core in-memory cache graph used by remote cache export and import. It implements `solver.CacheExporterTarget`, deduplicates cache records, links records through dependencies, tracks remote results, and marshals the graph into the v1 cache config schema.

## Important APIs, Types, and Functions

- `NewCacheChains` constructs a graph with root records indexed by digest.
- `CacheChains.Add` accepts solver cache records, dependencies, and export results, merging compatible graph nodes and recording parent/child links.
- `computeIDs` and `item.computeID` assign deterministic IDs for solver key storage.
- `leaves` returns graph nodes without children, which become marshal/storage roots.
- `IntersectAll` intersects dependency candidate sets.
- `Marshal` serializes the graph into `cacheimporttypes.CacheConfig` and a descriptor/provider map.
- `DescriptorProviderPair` wraps OCI descriptors and content/info providers, while forwarding optional unlazy-session and snapshot-label capabilities.
- `item` tracks digest, children, parents, results, and owning graph.
- `addChild`, `addResult`, `bestResult`, `walkChildren`, and `walkAllResults` maintain and traverse graph relationships.

## Control Flow and State

`Add` ignores digests with the `random:` prefix, since those cache keys should not become portable cache records. Root records with no dependencies are deduplicated by digest. Records with dependencies validate that every source is an `*item` from the same `CacheChains`, build candidate sets from existing child links that match selector/input/digest, and merge multiple candidate items into one main item when necessary. It then adds results, protects against cycles by removing dependency sources that are already children of the target item, and records child/parent links.

Marshalling starts from leaves and recursively marshals parents before children. Each item emits at most its best result, chosen by newest `CreatedAt`. Remote descriptor chains are serialized through `marshalRemote` in `utils.go`; the final config is sorted deterministically.

Graph state is in memory during a solve or import parse. Persisted state is the marshaled cache config plus remote blobs managed by the backend.

## Dependencies and Integration Points

This graph is shared by all remote cache exporters in the subset: GHA, S3, inline, local, and registry via the generic exporter. It integrates with solver cache export records, containerd content providers, OCI descriptors, BuildKit sessions, and snapshot label extension interfaces.

## Risks and Edge Cases

The merge path for multiple dependency candidates rewrites child parent links and carries results forward; regressions here can create incorrect cache graph aliases. `computeID` iterates over maps, so deterministic ID stability depends on the surrounding graph structure and may be vulnerable to map iteration nondeterminism despite deterministic hashing intent. Only the best result per item is marshaled, so older results are dropped from exported configs. Cycle avoidance mutates dependency sources to nil when needed, which can remove links silently.

## Test Signals

`chains_test.go` verifies a simple graph with two roots and one dependent result, deterministic layer parent encoding, record inputs/selectors, idempotent repeated adds, marshal/parse roundtrip, and adding an extra root. It does not cover merging multiple candidates, cycles, random digests, multi-result best selection, or optional provider capabilities.
