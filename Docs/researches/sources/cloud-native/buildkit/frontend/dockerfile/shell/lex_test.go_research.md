<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/shell/lex_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/shell/lex_test.go

## Purpose
Shell lexer tests for pattern conversion, variable expansion modifiers, mandatory env errors, word splitting, platform-specific environment matching, and match capture. The file has 658 lines and belongs to package `shell`.

## Important APIs, Types, and Functions
Test entry points: `TestConvertShellPatternToRegex`, `TestReverseString`, `TestReversePattern`, `TestShellParserMandatoryEnvVars`, `TestShellParser4EnvVars`, `TestShellParser4Words`, `TestGetEnv`, `TestProcessWithMatches`, `TestProcessWithMatchesPlatform`.

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
Direct test coverage in this file: `TestConvertShellPatternToRegex`, `TestReverseString`, `TestReversePattern`, `TestShellParserMandatoryEnvVars`, `TestShellParser4EnvVars`, `TestShellParser4Words`, `TestGetEnv`, `TestProcessWithMatches`, `TestProcessWithMatchesPlatform`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/shell/lex_test.go -->
