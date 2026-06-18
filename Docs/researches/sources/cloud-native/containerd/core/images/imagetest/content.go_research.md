# sources/cloud-native/containerd/core/images/imagetest/content.go

## Purpose

This file provides test helpers for constructing image content graphs in a temporary content store. It lets tests build manifests, indexes, blobs, platforms, missing-layer scenarios, and expected size models without manually writing OCI JSON and content blobs.

## Important APIs, Types, and Functions

`Content` wraps an OCI descriptor, labels, size accounting, and child `Content` values. `ContentStore` embeds `content.Store` and carries test context. `NewContentStore` creates a local labeled content store with an in-memory label store. Methods `Index`, `Manifest`, `Blob`, `RandomBlob`, `JSONObject`, and `Walk` create or mutate graph content. Content creators include `SimpleManifest`, `SimpleIndex`, and `StripLayers`; modifiers include `AddPlatform` and `LimitChildren`. `memoryLabelStore` implements the local content label store.

## Control Flow

Blob creation computes the SHA256 digest, writes the blob with `content.WriteBlob`, and returns a descriptor/size wrapper. JSON helpers marshal typed objects and store them as blobs. Manifest and index helpers assemble descriptors from child `Content`, write the OCI JSON object, and attach child lists for recursive test expectations. `Walk` applies a mutation callback to a content node, recursively processes children, and replaces child values with mutated copies. `StripLayers` uses `Walk` to delete layer blobs from the store and set their content size to zero.

## State and Persistence Behavior

The helper writes real blobs to a temporary local content store. `memoryLabelStore` persists labels only in a mutex-protected in-memory map for the lifetime of the test. The `Content` graph mirrors store state when helpers are used; direct external mutations can make size and child metadata stale, which the file comments warn about.

## Dependencies and Integration Points

It integrates with `core/content`, `core/images`, the local content plugin, OCI descriptors, OpenContainers digests, and Go testing. It is used by image usage tests and can support traversal, size, filtering, and missing-content tests.

## Risks and Edge Cases

`RandomBlob` uses deterministic pseudo-random bytes seeded by size, so blobs with the same size share content/digest. Blob refs are just digest strings, which could collide with concurrent duplicate writes but are suitable for isolated tests. `SimpleManifest` layers are random bytes, not valid compressed tar streams, so unpack/diffid tests must not use them as real layers. `memoryLabelStore.Get` returns the map directly, allowing callers to mutate stored labels without `Set` or `Update`.

## Test Signals

Tests using these helpers should compare calculated usage to `SizeOfManifest` and `SizeOfContent`, verify missing layers after `StripLayers`, platform-limited graph traversal, label persistence in the local labeled store, and consistency of recursively mutated `Content` graphs.
