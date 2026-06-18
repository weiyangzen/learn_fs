<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/version/dockerfile_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/version/dockerfile_test.go

## Purpose
Version normalization tests for canonical, labs, latest, invalid, and prerelease Dockerfile frontend version strings. The file has 37 lines and belongs to package `version`.

## Important APIs, Types, and Functions
Test entry points: `TestNormalizeDockerfileVersion`.

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
Direct test coverage in this file: `TestNormalizeDockerfileVersion`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/version/dockerfile_test.go -->
