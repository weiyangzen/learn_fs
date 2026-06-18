<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_runnetwork.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_runnetwork.go

## Purpose
RUN --network parser hook implementing sandbox/none/host mode validation and storage on RunCommand state. The file has 63 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Important symbols: `NetworkMode`, `allowedNetwork`, `isValidNetwork`, `networkKey`, `init`, `runNetworkPreHook`, `runNetworkPostHook`, `GetNetwork`, `networkState`.

## Control Flow
RUN parsing registers hooks that add a string flag with a default, validate the requested mode after flag parsing, and store a lightweight external state on RunCommand for later conversion.

## State and Persistence
Instruction structs carry parsed command state; RUN extensions store mount/device/network/security details via withExternalData maps on RunCommand. No disk persistence occurs.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated between parser.Node AST output and dockerfile2llb conversion, with linter warnings and RUN extension state consumed by later Dockerfile frontend conversion.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/support_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_runnetwork.go -->
