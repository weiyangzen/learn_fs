<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/support_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/support_test.go

## Purpose
Unit tests for handleJSONArgs behavior on JSON and non-JSON command attributes. The file has 65 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Test entry points: `TestHandleJSONArgs`.

## Control Flow
The tests construct table-driven Dockerfile snippets or integration build contexts, invoke the target parser/frontend path, and assert exact parsed structures, warnings, error messages, source maps, or build output files.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated with Dockerfile frontend integration tests and BuildKit gateway solve paths.

## Risks and Edge Cases
Primary risk is incomplete coverage if new parser/frontend flags are added without expanding these assertions; integration tests also depend on sandbox capabilities and external context setup.

## Test Signals
Direct test coverage in this file: `TestHandleJSONArgs`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/support_test.go -->
