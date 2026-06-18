# sources/cloud-native/containerd/core/images/imagetest/size.go

## Purpose

This file defines size accounting helpers for image test content graphs. It separates descriptor-reported manifest size, actually stored content size, snapshot usage, and uncompressed byte estimates.

## Important APIs, Types, and Functions

`Size` carries `Manifest`, `Content`, `Unpacked`, and `Uncompressed` counters. `ContentSizeCalculator` is a function type used by table tests. `SizeOfManifest` recursively sums `Content.Size.Manifest`, and `SizeOfContent` recursively sums `Content.Size.Content`.

## Control Flow

Both calculators use straightforward depth-first recursion over `Content.Children`. They add the current node's selected size counter and then add each child's recursive value.

## State and Persistence Behavior

There is no persistence. The functions read the in-memory `Content` graph and intentionally do not deduplicate repeated descriptors or consult the content store.

## Dependencies and Integration Points

The helpers live in the `imagetest` package and are used by usage calculator tests to compare manifest-based size against actual content-store-based size, especially when layers are removed.

## Risks and Edge Cases

Duplicate blobs are counted multiple times because the graph structure is accumulated, not unique digests. Deep graphs could recurse deeply, though image graphs are normally shallow. `Unpacked` and `Uncompressed` are modeled in `Size` but not used by these two functions.

## Test Signals

Signals are simple: usage tests should produce expected totals for simple manifests, indexes, stripped-layer graphs, and platform-limited indexes using these calculators.
