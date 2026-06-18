<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands.go

## Purpose
Typed Dockerfile instruction model: command structs, expansion hooks, stage management, source/destination representation, and per-command metadata. The file has 579 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Important symbols: `KeyValuePair`, `String`, `KeyValuePairOptional`, `String`, `ValueString`, `Command`, `KeyValuePairs`, `withNameAndCode`, `String`, `Name`, `Location`, `Comments`, `newWithNameAndCode`, `SingleWordExpander`, `SupportsSingleWordExpansion`, `SupportsSingleWordExpansionRaw`, `PlatformSpecific`, `expandKvp`, `expandKvpsInPlace`, `expandSliceInPlace`, `EnvCommand`, `Expand`, `MaintainerCommand`, `NewLabelCommand`, plus helper symbols used internally.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
Instruction structs carry parsed command state; RUN extensions store mount/device/network/security details via withExternalData maps on RunCommand. No disk persistence occurs.

## Dependencies and Integration Points
Dependencies: Dockerfile parser AST and source ranges; wrapped error reporting.
Integrated between parser.Node AST output and dockerfile2llb conversion, with linter warnings and RUN extension state consumed by later Dockerfile frontend conversion.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/support_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands.go -->
