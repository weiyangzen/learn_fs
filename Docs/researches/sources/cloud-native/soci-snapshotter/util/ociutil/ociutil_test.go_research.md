# sources/cloud-native/soci-snapshotter/util/ociutil/ociutil_test.go

## Purpose
This test file validates the behavior of `DedupePlatforms`.

## Important APIs, Types, and Functions
`assertPlatformEqual` compares every field of `ocispec.Platform`, including OS features via `slices.Equal`. `TestDedupePlatforms` covers no duplicates, exact duplicate removal, and normalized duplicate removal where `x86_64` matches `amd64`.

## Control Flow, State, and Persistence
The test is table-driven. For each case, it runs `DedupePlatforms`, asserts result length, and compares platforms positionally. It has no filesystem, network, or persistent state.

## Dependencies and Integration Points
The test uses Go `testing`, `slices`, and OCI platform structs. It indirectly validates integration with `containerd/platforms.Normalize` and `OnlyStrict`.

## Risks and Test Signals
The test does not cover `ValidateMediaType`. It also does not cover variants, OS version, or OS features in the de-duplication path. The strongest signal is that first-match order is expected and normalized architecture aliases collapse.
