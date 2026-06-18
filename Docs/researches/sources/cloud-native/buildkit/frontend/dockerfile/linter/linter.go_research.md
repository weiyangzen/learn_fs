<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/linter/linter.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/linter/linter.go

## Purpose
Dockerfile linter runtime: rule config, warning emission, comment-based check directives, error aggregation, and lint option parsing. The file has 240 lines and belongs to package `linter`.

## Important APIs, Types, and Functions
Important symbols: `Config`, `Linter`, `New`, `Run`, `WithMergedConfig`, `WithMergedConfigFromComments`, `Error`, `LinterRuleI`, `LinterRule`, `RuleName`, `Run`, `IsDeprecated`, `IsExperimental`, `LintFormatShort`, `LintWarnFunc`, `ParseLintOptions`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
Linter instances hold config and accumulated warnings in memory; WithMergedConfig creates merged config copies and Error aggregates warnings into a returned error.

## Dependencies and Integration Points
Dependencies: Dockerfile parser AST and source ranges; wrapped error reporting.
Integrated with instruction parsing and frontend check options; warnings travel through parser ranges and gateway Warn/Error reporting.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
No direct test in this file; behavior is exercised through higher-level parser, instruction, dockerui, and integration tests in adjacent packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/linter/linter.go -->
