<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/support.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/support.go

## Purpose
Shared helper for choosing JSON exec form versus shell form argument representation for shell-dependent instructions. The file has 19 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Important symbols: `handleJSONArgs`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated between parser.Node AST output and dockerfile2llb conversion, with linter warnings and RUN extension state consumed by later Dockerfile frontend conversion.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/support_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/support.go -->
