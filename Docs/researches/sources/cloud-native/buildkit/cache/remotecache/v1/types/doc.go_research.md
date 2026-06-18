# sources/cloud-native/buildkit/cache/remotecache/v1/types/doc.go

## Purpose

This package documentation describes the v1 BuildKit distributable cache format: an OCI image index or manifest containing cache layer descriptors and one BuildKit cache config object.

## Important APIs, Types, and Functions

This file does not declare runtime APIs. It documents the JSON layout later expressed by `spec.go`: `layers` reference blobs and parent layer indexes; `records` reference cache key digests, result layer pointers, chained layer pointers, and dependency inputs.

## Control Flow and State

There is no control flow. The documented state model is persisted in remote cache backends. Cache layer descriptors require uncompressed digest annotations and may include `buildkit/createdat` to preserve timestamps. Cache records describe solver cache-key graph edges and associated remote layer chains.

## Dependencies and Integration Points

The documentation references OCI image index layout and the BuildKit cache config media type used by registry/local importers and exporters.

## Risks and Edge Cases

The comment still describes older field names such as `chains` and conceptual `layers` pointers; it should stay aligned with `spec.go` JSON tags and parser behavior. Drift here can confuse backend implementers.

## Test Signals

No tests target package documentation directly. Consistency is indirectly validated by compile-time struct tags and v1 marshal/parse tests.
