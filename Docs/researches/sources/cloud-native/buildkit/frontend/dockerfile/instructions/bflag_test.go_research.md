<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go

## Purpose
Unit tests for builder flag parsing, duplicate detection, unknown flag suggestions, values, boolean forms, and -- delimiter handling. The file has 215 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Test entry points: `TestBuilderFlags`.

## Control Flow
Callers register allowed flags, Parse iterates raw --flag or --flag=value arguments until --, validates type and duplicates, records used flags, applies defaults, and wraps unknown flag errors with suggestions.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: slices; strings; testing.
Integrated with Dockerfile frontend integration tests and BuildKit gateway solve paths.

## Risks and Edge Cases
Primary risk is incomplete coverage if new parser/frontend flags are added without expanding these assertions; integration tests also depend on sandbox capabilities and external context setup.

## Test Signals
Direct test coverage in this file: `TestBuilderFlags`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go -->
