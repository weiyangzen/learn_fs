# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataFetcher.hh

## Purpose
This header declares `MetadataFetcher`, a static utility class for direct QuarkDB metadata reads without caching. It exposes future-returning APIs for file/container protobufs, parent maps, path resolution, fsview membership, and content counts.

## Important APIs, Types, and Functions
The API includes `getFileFromId`, `getContainerFromId`, existence checks, file/container map fetches, map-to-metadata fetch expansion, fetches by parent/name, path-to-id and container full-path resolution, fsview membership checks, and `countContents()`. Private helpers construct parent hash keys for files and subcontainers.

## Control Flow
All public methods are static and either return a `folly::Future`, a vector of futures, or a pair of futures. Callers compose or block on these futures depending on their own threading model.

## State and Persistence Behavior
The class stores no state and performs no writes. It reads durable QuarkDB namespace structures and returns protobuf/map snapshots from the time of query.

## Dependencies and Integration Points
It includes identifier types, metadata interfaces, namespace macros, file/container protobufs, `std::future`, and folly futures. It is the low-level read layer for both cache-backed services and the inspector.

## Risks and Test Signals
Because the class returns many independent futures, callers need to handle partial failures explicitly. Tests should verify API behavior for missing ids, missing names, bad maps, detached paths, root path, file-vs-container final component, and fsview membership.
