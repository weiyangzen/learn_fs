<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/linter/generate.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/linter/generate.go

## Purpose
Go generate helper that introspects linter rules and writes documentation/index material from rule metadata. The file has 219 lines and belongs to package `main`.

## Important APIs, Types, and Functions
Important symbols: `Rule`, `tmplStr`, `destDir`, `main`, `run`, `genRuleDoc`, `genIndex`, `listRules`, `camelToKebab`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated with instruction parsing and frontend check options; warnings travel through parser ranges and gateway Warn/Error reporting.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
No direct test in this file; behavior is exercised through higher-level parser, instruction, dockerui, and integration tests in adjacent packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/linter/generate.go -->
