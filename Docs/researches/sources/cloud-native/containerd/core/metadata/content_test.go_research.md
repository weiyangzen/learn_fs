# sources/cloud-native/containerd/core/metadata/content_test.go

## Purpose

This test file validates the metadata content store wrapper against containerd's content-store contract and verifies lease linkage for committed blobs and active ingests.

## Important APIs, Types, and Functions

`createContentStore` builds a local content store plus metadata DB and namespace wrapper used by testsuite helpers. `createContentStoreWithPolicy` adapts DB options into a testsuite init function. `TestContent` runs content, cross-namespace shared, cross-namespace isolated, and shared-namespace isolated suites. `TestContentLeased` and `TestIngestLeased` check lease buckets. Helpers include `createLease`, `checkContentLeased`, and `checkIngestLeased`.

## Control Flow

The testsuite wrapper creates unique namespaces per test and optionally marks namespaces as shared by writing the shared namespace label through the namespace store. Lease tests create a metadata DB, create a lease, write or begin content through a lease-bearing context, then inspect Bolt buckets to assert content or ingest resource references exist or are removed after commit/abort.

## State and Persistence Behavior

Tests use temporary local content and metadata databases. They directly inspect `v1/<namespace>/leases/<lease>/content` and `.../ingests` buckets to verify lease persistence. The content suites exercise backend blob storage, namespace metadata, and policy-dependent sharing behavior.

## Dependencies and Integration Points

The file integrates `core/content/testsuite`, metadata DB, local content store, leases, namespace labels, bbolt, errdefs, digest and OCI descriptors. It is the strongest behavioral signal for `content.go`.

## Risks and Edge Cases

Event publishing and backend garbage collection are not directly checked here. Lease checks inspect internal bucket paths, which is appropriate for metadata but couples tests to schema. The shared namespace wrapper writes labels in a raw DB update and assumes namespace store behavior.

## Test Signals

Passing tests indicate the metadata content store satisfies the content store contract in default/shared and isolated policies, correctly attaches existing and newly committed content to leases, leases active ingests, and removes ingest lease records after abort/commit.
