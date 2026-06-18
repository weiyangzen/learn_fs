<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go

## Purpose
Unit tests for RUN --device CSV parsing, required flag forms, name handling, and invalid option diagnostics. The file has 69 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Test entry points: `TestParseDevice`.

## Control Flow
RUN parsing registers pre/post hooks; the pre hook declares repeated --device values, parsing validates CSV fields into Device objects, and GetDevices retrieves the external state attached to RunCommand.

## State and Persistence
Instruction structs carry parsed command state; RUN extensions store mount/device/network/security details via withExternalData maps on RunCommand. No disk persistence occurs.

## Dependencies and Integration Points
Dependencies: wrapped error reporting; test assertions.
Integrated with Dockerfile frontend integration tests and BuildKit gateway solve paths.

## Risks and Edge Cases
Risks include ambiguous bare fields versus key=value fields, duplicate name detection, required boolean parsing, and future CDI option compatibility.

## Test Signals
Direct test coverage in this file: `TestParseDevice`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go -->
