<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerignore/dockerignore_deprecated.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerignore/dockerignore_deprecated.go

## Purpose
Compatibility shim exposing the deprecated dockerignore.ReadAll alias while delegating semantics to patternmatcher/ignorefile. The file has 14 lines and belongs to package `dockerignore`.

## Important APIs, Types, and Functions
Important symbols: `ReadAll`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: Docker ignore pattern parsing.
Integrated with Dockerfile frontend integration tests and BuildKit gateway solve paths.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
No direct test in this file; behavior is exercised through higher-level parser, instruction, dockerui, and integration tests in adjacent packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerignore/dockerignore_deprecated.go -->
