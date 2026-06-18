<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/dumper/main.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/dumper/main.go

## Purpose
Small AST dumper command-line utility that parses a Dockerfile and prints parser.Node.Dump output. The file has 29 lines and belongs to package `main`.

## Important APIs, Types, and Functions
Important symbols: `main`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: Dockerfile parser AST and source ranges.
Integrated as the first Dockerfile frontend stage: dockerui reads source bytes, parser.Parse builds AST, instructions.Parse converts nodes, and errors carry parser.Range locations.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
No direct test in this file; behavior is exercised through higher-level parser, instruction, dockerui, and integration tests in adjacent packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/dumper/main.go -->
