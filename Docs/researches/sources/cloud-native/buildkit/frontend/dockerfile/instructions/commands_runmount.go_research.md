<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_runmount.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_runmount.go

## Purpose
RUN --mount parser and hook integration for bind/cache/tmpfs/secret/ssh mounts, options, delayed expansion, sharing, modes, ownership, and validation. The file has 310 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Important symbols: `MountType`, `allowedMountTypes`, `ShareMode`, `allowedSharingModes`, `mountsKeyT`, `mountsKey`, `init`, `allShareModes`, `allMountTypes`, `runMountPreHook`, `runMountPostHook`, `setMountState`, `getMountState`, `GetMounts`, `mountState`, `Mount`, `parseMount`.

## Control Flow
RUN parsing registers pre/post hooks; the pre hook declares a repeated --mount flag, req.flags.Parse collects raw CSV values, and the post hook parses each value into Mount structs with validation and delayed expansion where required.

## State and Persistence
Instruction structs carry parsed command state; RUN extensions store mount/device/network/security details via withExternalData maps on RunCommand. No disk persistence occurs.

## Dependencies and Integration Points
Dependencies: wrapped error reporting; CSV-style flag value parsing.
Integrated between parser.Node AST output and dockerfile2llb conversion, with linter warnings and RUN extension state consumed by later Dockerfile frontend conversion.

## Risks and Edge Cases
Risks include CSV quoting edge cases, deferred variable expansion semantics, mount-type-specific option validation, secret/ssh required handling, and unexpected read-only defaults.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/support_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_runmount.go -->
