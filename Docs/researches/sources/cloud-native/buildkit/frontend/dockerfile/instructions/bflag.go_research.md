<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag.go

## Purpose
Builder flag parser for Dockerfile instruction flags such as --mount, --network, --security, --chown, --exclude, and typed bool/string/repeated values. The file has 222 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Important symbols: `FlagType`, `BFlags`, `Flag`, `NewBFlags`, `NewBFlagsWithArgs`, `AddBool`, `AddString`, `AddStrings`, `addFlag`, `IsUsed`, `Used`, `IsTrue`, `Parse`, `allFlags`.

## Control Flow
Callers register allowed flags, Parse iterates raw --flag or --flag=value arguments until --, validates type and duplicates, records used flags, applies defaults, and wraps unknown flag errors with suggestions.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated between parser.Node AST output and dockerfile2llb conversion, with linter warnings and RUN extension state consumed by later Dockerfile frontend conversion.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/support_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag.go -->
