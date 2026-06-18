<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/build_test.go -->
# sources/cloud-native/buildkit/frontend/dockerui/build_test.go

## Purpose
Unit test for platform ID normalization and Windows platform extension from image metadata. The file has 100 lines and belongs to package `dockerui`.

## Important APIs, Types, and Functions
Test entry points: `TestNormalizePlatform`.

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
Direct test coverage in this file: `TestNormalizePlatform`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/build_test.go -->
