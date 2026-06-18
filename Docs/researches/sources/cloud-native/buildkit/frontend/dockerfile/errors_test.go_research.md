<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/errors_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/errors_test.go

## Purpose
Integration test coverage for source-map-rich Dockerfile errors returned through the frontend/gateway path. The file has 116 lines and belongs to package `dockerfile`.

## Important APIs, Types, and Functions
Important symbols: `testErrorsSourceMap`.

## Control Flow
The tests construct table-driven Dockerfile snippets or integration build contexts, invoke the target parser/frontend path, and assert exact parsed structures, warnings, error messages, source maps, or build output files.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: test assertions; platform/test filesystem helpers.
Integrated with Dockerfile frontend integration tests and BuildKit gateway solve paths.

## Risks and Edge Cases
Primary risk is incomplete coverage if new parser/frontend flags are added without expanding these assertions; integration tests also depend on sandbox capabilities and external context setup.

## Test Signals
No direct test in this file; behavior is exercised through higher-level parser, instruction, dockerui, and integration tests in adjacent packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/errors_test.go -->
