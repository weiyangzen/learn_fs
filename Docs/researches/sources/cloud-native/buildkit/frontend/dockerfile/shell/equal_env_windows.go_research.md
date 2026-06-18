<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/shell/equal_env_windows.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/shell/equal_env_windows.go

## Purpose
Windows environment key equality implementation with case-insensitive comparison and uppercase normalization. The file has 17 lines and belongs to package `shell`.

## Important APIs, Types, and Functions
Important symbols: `EqualEnvKeys`, `NormalizeEnvKey`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated by parser heredoc detection, line parsers, and Dockerfile variable expansion paths that need shell-compatible quote/env semantics.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/shell/lex_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/shell/equal_env_windows.go -->
