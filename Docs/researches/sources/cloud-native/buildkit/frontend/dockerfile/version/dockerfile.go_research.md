<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/version/dockerfile.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/version/dockerfile.go

## Purpose
Dockerfile frontend version parser that normalizes tags into semantic version values with labs/latest/channel handling. The file has 48 lines and belongs to package `version`.

## Important APIs, Types, and Functions
Important symbols: `Version`, `normalizeDockerfileVersion`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated by Dockerfile frontend version negotiation and syntax image tag interpretation.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/version/dockerfile_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/version/dockerfile.go -->
