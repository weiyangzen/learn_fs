# sources/cloud-native/containerd/core/images/image.go

## Purpose

This file defines the image metadata model and core image inspection helpers for resolving manifests, configs, platforms, rootfs diff IDs, sizes, child descriptors, and local content completeness. It is a central descriptor/content utility layer for containerd images.

## Important APIs, Types, and Functions

`Image` holds name, labels, target descriptor, and timestamps. `Store` defines image CRUD with field-mask updates and delete options. `DeleteOptions`, `DeleteOpt`, `SynchronousDelete`, and `DeleteTarget` model delete behavior. Image methods `Config`, `RootFS`, and `Size` delegate to package functions. Package functions include `Manifest`, `Config`, `Platforms`, `Check`, `Children`, `RootFS`, `ConfigPlatform`, and internal `validateMediaType`.

## Control Flow

`Image.Size` walks target content using a handler chain that sums non-negative descriptor sizes and descends through platform-limited children. `Manifest` walks from an image descriptor, reading and validating manifests or indexes. For manifest descriptors it unmarshals an OCI manifest, checks descriptor or config platform when needed, and records the first match. For index descriptors it reads an index, filters and sorts manifest descriptors by platform, limits to one candidate, and continues walking. `Children` reads known manifest or index blobs, validates media type against document shape, and returns immediate config/layer or manifest children. `Check` resolves the target manifest, then verifies config and layer blobs by opening readers.

## State and Persistence Behavior

The file mostly reads from a content provider and does not mutate storage. It models persistent image records through `Image` and `Store` interfaces but does not implement a store here. `Check` opens and closes content readers to test availability. JSON blobs are parsed from the content store, and media-type validation rejects Docker schema 1 and mismatches between descriptor media type and document contents.

## Dependencies and Integration Points

It depends on `core/content`, `platforms`, `errdefs`, OCI image-spec descriptors/manifests/indexes/images, OpenContainers digests, and local handler/media-type helpers. Metadata stores implement `Store`; pull, fetch, unpack, export, and usage calculation use the descriptor readers and traversal helpers.

## Risks and Edge Cases

Several helpers assume OCI manifest shape even for Docker schema 2. `Manifest` returns the first sorted match and does not detect multiple equally valid platform matches beyond stable ordering. If an index has no match, it returns NotFound only after walking yields no manifest. `Check` ignores possible children under referenced components and only verifies config/layers. `validateMediaType` uses structural JSON heuristics, so unusual but valid future documents could be rejected.

## Test Signals

`image_test.go` directly covers `validateMediaType` for manifest/index pairs, declared media-type mismatches, and schema 1 rejection. Additional high-value tests should cover platform-less manifest resolution via config platform, platform sorting, `Check` missing vs present blobs, `Children` unknown media-type logging, negative descriptor sizes in `Size`, and config/rootfs parsing failures.
