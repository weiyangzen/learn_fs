<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/attr.go -->
# sources/cloud-native/buildkit/frontend/dockerui/attr.go

## Purpose
dockerui option parsers for platforms, resolve mode, extra hosts, shm size, ulimits, Linux resources, network mode, local session IDs, and prefixed option filtering. The file has 207 lines and belongs to package `dockerui`.

## Important APIs, Types, and Functions
Important symbols: `parsePlatforms`, `parseResolveMode`, `parseExtraHosts`, `parseShmSize`, `parseUlimits`, `parseLinuxResources`, `parseNetMode`, `parseLocalSessionIDs`, `filter`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: BuildKit LLB state/options; wrapped error reporting; CSV-style flag value parsing; platform/test filesystem helpers.
Integrated with gateway/client BuildOpts, LLB source construction, exporter metadata, frontend inputs, named contexts, .dockerignore, and source-date-epoch behavior.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerui/build_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/attr.go -->
