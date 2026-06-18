# sources/cloud-native/containerd/core/metadata/boltutil/helpers.go

## Purpose

This file provides reusable bbolt serialization helpers for common metadata fields: labels, annotations, timestamps, extension maps, and protobuf Any values.

## Important APIs, Types, and Functions

`ReadLabels`, `WriteLabels`, `ReadAnnotations`, and `WriteAnnotations` operate on child buckets. `ReadTimestamps` and `WriteTimestamps` store binary `time.Time` values for created/updated keys. `WriteExtensions` and `ReadExtensions` marshal maps of `typeurl.Any` into an `extensions` bucket. `WriteAny` and `ReadAny` marshal individual protobuf Any values.

## Control Flow

Map writers delete any existing child bucket, skip creation for empty maps, create a fresh bucket, write non-empty values, and delete zero-value keys from the caller's map. Readers return nil when a map bucket does not exist. Extension and Any helpers use containerd's protobuf shim and typeurl marshaling before storing bytes.

## State and Persistence Behavior

The helpers mutate bbolt buckets passed by callers. Labels/annotations are stored as nested key/value buckets, timestamps as binary blobs, extensions as protobuf Any bytes by extension name, and individual Any values as protobuf bytes under a named key.

## Dependencies and Integration Points

Container, image, content, sandbox, lease, and namespace metadata code use these helpers for consistent serialization. Dependencies include containerd protobuf packages, typeurl, bbolt, and `time`.

## Risks and Edge Cases

`writeMap` mutates the caller-provided labels map by deleting empty values. `WriteExtensions` does not remove an existing extensions bucket when the map is empty, so callers replacing extensions with nil need to ensure stale data is handled elsewhere. `ReadExtensions` returns protobuf Any wrappers, not fully unmarshaled typed values. Timestamp unmarshalling errors surface from potentially corrupt DB values.

## Test Signals

Tests should cover nil and empty maps, empty label deletion side effects, replacing existing label buckets, timestamp round trips, Any nil handling, extension map round trips, corrupt protobuf bytes, and stale extension removal behavior in callers.
