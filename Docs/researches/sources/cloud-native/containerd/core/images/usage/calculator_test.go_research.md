# sources/cloud-native/containerd/core/images/usage/calculator_test.go

## Purpose

This test file verifies image usage calculation against synthetic image graphs. It confirms the distinction between manifest-reported size and actual stored content size, including missing layers and platform-limited indexes.

## Important APIs, Types, and Functions

`TestUsageCalculation` is a table test using `imagetest.ContentCreator` inputs, `imagetest.ContentSizeCalculator` expected functions, and calculator options. It exercises `CalculateImageUsage`, `WithManifestUsage`, and `WithManifestLimit`.

## Control Flow

For each case the test creates a log-aware context, builds a temporary content store, generates a target content graph, constructs an `images.Image` targeting that descriptor, runs `CalculateImageUsage`, computes the expected size from the in-memory graph, and fails if the totals differ.

## State and Persistence Behavior

Tests write temporary content blobs and delete layer blobs in stripped-layer cases through `imagetest.StripLayers`. All state is isolated in the testing temp directory and in-memory label store.

## Dependencies and Integration Points

It connects the usage package to `core/images`, `imagetest`, `platforms.Only`, OCI platform descriptors, and `logtest`. It is a regression suite for descriptor traversal, content-store presence checks, and manifest-limit behavior.

## Risks and Edge Cases

There is a TODO for snapshot usage, so unpacked snapshot accounting is not verified. The synthetic layer blobs are not valid tar/gzip content, which is fine for usage but not unpack paths. The table does not check error cases for missing required platform manifests or provider errors.

## Test Signals

Passing tests indicate correct totals for manifest-only counting, content-backed counting, missing layers counted as zero when appropriate, and platform limit selection of a single manifest from an index.
