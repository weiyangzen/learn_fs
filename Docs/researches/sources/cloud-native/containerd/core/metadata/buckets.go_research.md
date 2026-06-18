# sources/cloud-native/containerd/core/metadata/buckets.go

## Purpose

This file documents and codifies the bbolt bucket schema for containerd metadata. It defines bucket key constants and helper functions for locating or creating namespace-scoped object buckets.

## Important APIs, Types, and Functions

Constants include schema/version keys, object buckets for labels/images/containers/snapshots/content/blobs/ingests/leases/sandboxes, field keys such as digest/media type/size/runtime/spec/snapshot fields, and a deprecated ingest bucket key. Helpers include `getBucket`, `createBucketIfNotExists`, path helpers for namespace labels and images, and getters/creators for image, container, snapshotter, blob, ingest, and sandbox buckets.

## Control Flow

`getBucket` walks a sequence of bucket keys and returns nil on the first missing bucket. `createBucketIfNotExists` creates the first bucket on the transaction and then creates each nested bucket. Object-specific helpers compose these primitives with namespace and object-type keys.

## State and Persistence Behavior

The file is the persistence map for metadata DB version `v1`. It lays out namespace labels, images, containers, snapshots, content blobs/ingests, sandboxes, and leases, including timestamps, labels, target descriptors, runtime/spec data, parent/children links, and lease resource buckets.

## Dependencies and Integration Points

All metadata stores and GC code depend on these key constants and helpers. The embedded schema comments are the reference for migrations and backward-compatible additions. It depends only on bbolt and OpenContainers digests.

## Risks and Edge Cases

Bucket key changes are schema changes and must be paired with migrations. Some helper names differ from schema comments historically, so code should rely on constants rather than prose alone. `createBlobBucket` uses `CreateBucket`, not `CreateBucketIfNotExists`, to detect duplicate content. Namespace name `version` is reserved by schema design.

## Test Signals

Migration tests, CRUD tests for each object type, and GC graph scans validate the bucket layout. Any schema change needs tests that old layouts migrate into the documented bucket tree and that helper getters find the expected buckets.
