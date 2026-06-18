<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go

## Purpose
Instruction parser unit tests for arity, healthcheck flags, comments, invalid forms, nil linter behavior, RUN flag accounting, and stage name parsing. The file has 283 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Test entry points: `TestCommandsExactlyOneArgument`, `TestCommandsAtLeastOneArgument`, `TestCommandsNoDestinationArgument`, `TestCommandsTooManyArguments`, `TestCommandsBlankNames`, `TestHealthCheckCmd`, `TestParseOptInterval`, `TestNilLinter`, `TestCommentsDetection`, `TestErrorCases`, `TestRunCmdFlagsUsed`.

## Control Flow
The tests construct table-driven Dockerfile snippets or integration build contexts, invoke the target parser/frontend path, and assert exact parsed structures, warnings, error messages, source maps, or build output files.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: Dockerfile parser AST and source ranges; test assertions.
Integrated with Dockerfile frontend integration tests and BuildKit gateway solve paths.

## Risks and Edge Cases
Primary risk is incomplete coverage if new parser/frontend flags are added without expanding these assertions; integration tests also depend on sandbox capabilities and external context setup.

## Test Signals
Direct test coverage in this file: `TestCommandsExactlyOneArgument`, `TestCommandsAtLeastOneArgument`, `TestCommandsNoDestinationArgument`, `TestCommandsTooManyArguments`, `TestCommandsBlankNames`, `TestHealthCheckCmd`, `TestParseOptInterval`, `TestNilLinter`, `TestCommentsDetection`, `TestErrorCases`, `TestRunCmdFlagsUsed`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go -->
