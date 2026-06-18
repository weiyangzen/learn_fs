<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/build.go -->
# sources/cloud-native/buildkit/frontend/dockerui/build.go

## Purpose
dockerui build coordinator that runs per-platform build functions, attaches refs/config metadata, handles multi-platform exporter metadata, and normalizes platform IDs. The file has 155 lines and belongs to package `dockerui`.

## Important APIs, Types, and Functions
Important symbols: `BuildResult`, `BuildFunc`, `Build`, `ResultBuilder`, `Finalize`, `EachPlatform`, `extendWindowsPlatform`, `makeExportPlatform`.

## Control Flow
Build expands target platforms, launches one errgroup task per platform, calls the provided BuildFunc, serializes image/base configs, stores refs and metadata with single- or multi-platform keys, and Finalize adds exporter platform metadata.

## State and Persistence
ResultBuilder accumulates refs and exporter metadata in client.Result memory. Per-platform writes share one result object, so correctness depends on BuildKit result APIs tolerating the errgroup write pattern.

## Dependencies and Integration Points
Dependencies: BuildKit gateway client/result APIs; wrapped error reporting; platform/test filesystem helpers.
Integrated with gateway/client BuildOpts, LLB source construction, exporter metadata, frontend inputs, named contexts, .dockerignore, and source-date-epoch behavior.

## Risks and Edge Cases
Risks include closure capture in concurrent platform loops, shared Result mutation under errgroup, platform ID/config metadata mismatches, and Windows OSVersion/OSFeatures normalization regressions.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerui/build_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/build.go -->
