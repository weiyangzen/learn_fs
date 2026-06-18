<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/errors_windows.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/errors_windows.go

## Purpose
Windows-specific JSON-form error helper that adds hints for unescaped Windows paths in JSON arrays. The file has 29 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Important symbols: `errNotJSON`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated between parser.Node AST output and dockerfile2llb conversion, with linter warnings and RUN extension state consumed by later Dockerfile frontend conversion.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/errors_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/errors_windows.go -->
