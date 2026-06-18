<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/split_command.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/split_command.go

## Purpose
Command splitter that separates instruction name, builder flags, and remaining args while respecting escape tokens and flag terminators. The file has 122 lines and belongs to package `parser`.

## Important APIs, Types, and Functions
Important symbols: `splitCommand`, `extractBuilderFlags`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: strings; unicode.
Integrated as the first Dockerfile frontend stage: dockerui reads source bytes, parser.Parse builds AST, instructions.Parse converts nodes, and errors carry parser.Range locations.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/parser/directives_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/json_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/split_command.go -->
