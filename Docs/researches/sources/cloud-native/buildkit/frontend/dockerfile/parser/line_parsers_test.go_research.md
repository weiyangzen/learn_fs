<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers_test.go

## Purpose
Focused tests for name/value parsing in old and new ENV/ARG-like forms, including empty value rejection. The file has 59 lines and belongs to package `parser`.

## Important APIs, Types, and Functions
Test entry points: `TestParseNameValOldFormat`, `TestParseNameValNewFormat`, `TestParseNameValWithoutVal`.

## Control Flow
The tests construct table-driven Dockerfile snippets or integration build contexts, invoke the target parser/frontend path, and assert exact parsed structures, warnings, error messages, source maps, or build output files.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: test assertions.
Integrated with Dockerfile frontend integration tests and BuildKit gateway solve paths.

## Risks and Edge Cases
Primary risk is incomplete coverage if new parser/frontend flags are added without expanding these assertions; integration tests also depend on sandbox capabilities and external context setup.

## Test Signals
Direct test coverage in this file: `TestParseNameValOldFormat`, `TestParseNameValNewFormat`, `TestParseNameValWithoutVal`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers_test.go -->
