<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice.go

## Purpose
RUN --device extension parser and hook integration that stores CDI device requests on RunCommand external state. The file has 118 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Important symbols: `devicesKey`, `init`, `runDevicePreHook`, `runDevicePostHook`, `setDeviceState`, `getDeviceState`, `GetDevices`, `deviceState`, `Device`, `ParseDevice`.

## Control Flow
RUN parsing registers pre/post hooks; the pre hook declares repeated --device values, parsing validates CSV fields into Device objects, and GetDevices retrieves the external state attached to RunCommand.

## State and Persistence
Instruction structs carry parsed command state; RUN extensions store mount/device/network/security details via withExternalData maps on RunCommand. No disk persistence occurs.

## Dependencies and Integration Points
Dependencies: wrapped error reporting; CSV-style flag value parsing.
Integrated between parser.Node AST output and dockerfile2llb conversion, with linter warnings and RUN extension state consumed by later Dockerfile frontend conversion.

## Risks and Edge Cases
Risks include ambiguous bare fields versus key=value fields, duplicate name detection, required boolean parsing, and future CDI option compatibility.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/support_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice.go -->
