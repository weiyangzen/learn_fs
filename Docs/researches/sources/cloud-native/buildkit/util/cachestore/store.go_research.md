# sources/cloud-native/buildkit/util/cachestore/store.go

## Purpose
Cache-key graph exporter. It walks a solver.CacheKeyStorage with link-walking support and builds serializable Records containing parent/child relationships and stable IDs.

## Important APIs, Types, And Functions
Package: `cachestore`. Build tags: `none`. Key declarations observed in the file: `Record, Link, storeWithLinks, Records, setLinkIDs, setIndex, loadRecord`.

## Control Flow, State, And Persistence
Records finds root cache keys with random:/sha256: prefixes, recursively loadRecord walks outbound links, detects cycles with nil sentinels, then setIndex assigns deterministic child order by digest and setLinkIDs materializes integer references.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/solver, github.com/opencontainers/go-digest, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are store implementations without WalkLinksAll, cycles, and graph size. No local tests in this subset.
