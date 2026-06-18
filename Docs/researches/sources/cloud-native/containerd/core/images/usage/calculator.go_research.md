# sources/cloud-native/containerd/core/images/usage/calculator.go

## Purpose

This file calculates image storage usage by walking an image descriptor graph and summing either manifest-reported sizes, actual content-store sizes, and optionally referenced snapshot usage.

## Important APIs, Types, and Functions

`usageOptions` stores platform, manifest limit, manifest-only mode, and snapshotter lookup. Options are `WithManifestLimit`, `WithSnapshotters`, and `WithManifestUsage`. `CalculateImageUsage(ctx, image, provider, opts...)` is the exported calculator and requires a `content.InfoReaderProvider`.

## Control Flow

The calculator builds an `images.ChildrenHandler`, wraps it with `LimitManifests` when a platform matcher is supplied, and dispatches from the image target with a concurrency limit of 3. For each descriptor, the handler attempts to discover children, treats missing content as zero usage unless the platform-limited path requires it, reads `content.Info` when actual usage or snapshots are needed, replaces descriptor size with larger actual store size, scans snapshot GC labels, asks configured snapshotters for usage, ignores benign missing/invalid snapshot usage errors, and atomically accumulates descriptor and snapshot sizes.

## State and Persistence Behavior

The function does not mutate metadata. It reads descriptor children, content info, labels, and snapshot usage. The atomic counter allows concurrent handler execution from `images.Dispatch`.

## Dependencies and Integration Points

It integrates `core/images` traversal, content info providers, snapshotters, errdefs, platform matchers, OCI descriptors, and semaphores. It is useful for image listing, CLI size reporting, and cleanup/accounting paths.

## Risks and Edge Cases

Manifest-only mode can count descriptor sizes for content that is not present. Without manifest-only, missing non-required descriptors are counted as zero. Actual content info size can override descriptor size only when larger, avoiding negative or understated sizes. Snapshot usage is discovered through `containerd.io/gc.ref.snapshot.<snapshotter>` labels, so missing labels produce no unpacked usage. Duplicate descriptors are counted each time traversal visits them.

## Test Signals

`calculator_test.go` covers simple manifest, index, missing-layer manifest-only, missing-layer actual usage, and platform manifest limiting. Further tests should include snapshotter usage labels, snapshot not-found/invalid-argument suppression, hard errors from snapshotters, missing platform-limited manifests, duplicate descriptor counting, and negative descriptor sizes.
