# sources/distributed-fs/seaweedfs/weed/filer/elastic/v7/doc.go

## Purpose
This package documentation file explains that the Elasticsearch filer store is build-tagged and compiled only in full installs because the `olivere/elastic/v7` dependency is large.

## Important APIs, Types, and Functions
No APIs are defined. It declares package `elastic` and documents the build/install context.

## Control Flow and State
No runtime control flow.

## State and Persistence Behavior
No persistence.

## Dependencies and Integration Points
It documents the package implemented by `elastic_store.go` and `elastic_store_kv.go`, both of which use the `elastic` build tag.

## Risks and Edge Cases
The comment notes build-size concerns; users may not have this backend unless building with the correct tag/full install path.

## Test Signals
Package availability should be covered by build-tag CI or full-install builds.
