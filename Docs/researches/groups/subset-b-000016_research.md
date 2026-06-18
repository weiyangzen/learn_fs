# subset-b-000016 Research

Grouped source research for BuildKit Dockerfile frontend parser, instruction, shell, linter, version, and dockerui files. Each section is bounded for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerignore/dockerignore_deprecated.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerignore/dockerignore_deprecated.go

## Purpose
Compatibility shim exposing the deprecated dockerignore.ReadAll alias while delegating semantics to patternmatcher/ignorefile. The file has 14 lines and belongs to package `dockerignore`.

## Important APIs, Types, and Functions
Important symbols: `ReadAll`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: Docker ignore pattern parsing.
Integrated with Dockerfile frontend integration tests and BuildKit gateway solve paths.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
No direct test in this file; behavior is exercised through higher-level parser, instruction, dockerui, and integration tests in adjacent packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerignore/dockerignore_deprecated.go -->

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/exclude_patterns_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/exclude_patterns_test.go

## Purpose
Integration tests for ADD/COPY --exclude pattern handling across local, Git, HTTP, wildcard, and Dockerfile-specific contexts. The file has 278 lines and belongs to package `dockerfile`.

## Important APIs, Types, and Functions
Important symbols: `excludedFilesTests`, `init`, `testExcludedFilesOnCopy`.

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
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/exclude_patterns_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag.go

## Purpose
Builder flag parser for Dockerfile instruction flags such as --mount, --network, --security, --chown, --exclude, and typed bool/string/repeated values. The file has 222 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Important symbols: `FlagType`, `BFlags`, `Flag`, `NewBFlags`, `NewBFlagsWithArgs`, `AddBool`, `AddString`, `AddStrings`, `addFlag`, `IsUsed`, `Used`, `IsTrue`, `Parse`, `allFlags`.

## Control Flow
Callers register allowed flags, Parse iterates raw --flag or --flag=value arguments until --, validates type and duplicates, records used flags, applies defaults, and wraps unknown flag errors with suggestions.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated between parser.Node AST output and dockerfile2llb conversion, with linter warnings and RUN extension state consumed by later Dockerfile frontend conversion.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/support_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag.go -->

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands.go

## Purpose
Typed Dockerfile instruction model: command structs, expansion hooks, stage management, source/destination representation, and per-command metadata. The file has 579 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Important symbols: `KeyValuePair`, `String`, `KeyValuePairOptional`, `String`, `ValueString`, `Command`, `KeyValuePairs`, `withNameAndCode`, `String`, `Name`, `Location`, `Comments`, `newWithNameAndCode`, `SingleWordExpander`, `SupportsSingleWordExpansion`, `SupportsSingleWordExpansionRaw`, `PlatformSpecific`, `expandKvp`, `expandKvpsInPlace`, `expandSliceInPlace`, `EnvCommand`, `Expand`, `MaintainerCommand`, `NewLabelCommand`, plus helper symbols used internally.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
Instruction structs carry parsed command state; RUN extensions store mount/device/network/security details via withExternalData maps on RunCommand. No disk persistence occurs.

## Dependencies and Integration Points
Dependencies: Dockerfile parser AST and source ranges; wrapped error reporting.
Integrated between parser.Node AST output and dockerfile2llb conversion, with linter warnings and RUN extension state consumed by later Dockerfile frontend conversion.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/support_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands.go -->

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_runsecurity.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_runsecurity.go

## Purpose
RUN --security parser hook implementing sandbox/insecure validation and storage on RunCommand state. The file has 59 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Important symbols: `allowedSecurity`, `isValidSecurity`, `securityKey`, `init`, `runSecurityPreHook`, `runSecurityPostHook`, `GetSecurity`, `securityState`.

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
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_runsecurity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/errors_unix.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/errors_unix.go

## Purpose
Unix build-tag implementation of JSON-form error text for Dockerfile instructions. The file has 9 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Important symbols: `errNotJSON`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated between parser.Node AST output and dockerfile2llb conversion, with linter warnings and RUN extension state consumed by later Dockerfile frontend conversion.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/errors_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/errors_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/errors_windows.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/errors_windows.go

## Purpose
Windows-specific JSON-form error helper that adds hints for unescaped Windows paths in JSON arrays. The file has 29 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Important symbols: `errNotJSON`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated between parser.Node AST output and dockerfile2llb conversion, with linter warnings and RUN extension state consumed by later Dockerfile frontend conversion.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/errors_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/errors_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse.go

## Purpose
Main typed-instruction parser that converts parser.Node AST entries into Stage and Command objects, validates syntax, runs linter checks, and wires RUN extension hooks. The file has 894 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Important symbols: `parseRequest`, `nodeArgs`, `newParseRequestFromNode`, `ParseInstruction`, `ParseInstructionWithLinter`, `ParseCommand`, `UnknownInstructionError`, `Error`, `parseError`, `Error`, `Unwrap`, `Parse`, `parseKvps`, `parseEnv`, `parseMaintainer`, `parseLabel`, `parseSourcesAndDest`, `parseAdd`, `parseCopy`, `parseFrom`, `validStageName`, `parseBuildStageName`, `parseOnBuild`, `parseWorkdir`, plus helper symbols used internally.

## Control Flow
ParseInstructionWithLinter builds a parseRequest from parser.Node, dispatches by lowercase command name, parses flags before command-specific validation, attaches locations on errors, and Parse walks AST children into meta ARGs and Stage command lists.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: Dockerfile parser AST and source ranges; Dockerfile linter rules/config; wrapped error reporting.
Integrated between parser.Node AST output and dockerfile2llb conversion, with linter warnings and RUN extension state consumed by later Dockerfile frontend conversion.

## Risks and Edge Cases
Risks include command arity mismatches, linter nil handling, stage-name validation, heredoc source/destination confusion, and RUN hook ordering because extension flags are registered before Parse.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/support_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go

## Purpose
Instruction-level heredoc tests for COPY and RUN heredoc parsing, expansion flags, chomp behavior, and invalid heredoc locations. The file has 257 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Test entry points: `TestErrorCasesHeredoc`, `TestCopyHeredoc`, `TestRunHeredoc`.

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
Direct test coverage in this file: `TestErrorCasesHeredoc`, `TestCopyHeredoc`, `TestRunHeredoc`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go -->

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/support.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/instructions/support.go

## Purpose
Shared helper for choosing JSON exec form versus shell form argument representation for shell-dependent instructions. The file has 19 lines and belongs to package `instructions`.

## Important APIs, Types, and Functions
Important symbols: `handleJSONArgs`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated between parser.Node AST output and dockerfile2llb conversion, with linter warnings and RUN extension state consumed by later Dockerfile frontend conversion.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/instructions/bflag_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/commands_rundevice_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/parse_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/instructions/support_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/instructions/support.go -->

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/linter/generate.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/linter/generate.go

## Purpose
Go generate helper that introspects linter rules and writes documentation/index material from rule metadata. The file has 219 lines and belongs to package `main`.

## Important APIs, Types, and Functions
Important symbols: `Rule`, `tmplStr`, `destDir`, `main`, `run`, `genRuleDoc`, `genIndex`, `listRules`, `camelToKebab`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated with instruction parsing and frontend check options; warnings travel through parser ranges and gateway Warn/Error reporting.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
No direct test in this file; behavior is exercised through higher-level parser, instruction, dockerui, and integration tests in adjacent packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/linter/generate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/linter/linter.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/linter/linter.go

## Purpose
Dockerfile linter runtime: rule config, warning emission, comment-based check directives, error aggregation, and lint option parsing. The file has 240 lines and belongs to package `linter`.

## Important APIs, Types, and Functions
Important symbols: `Config`, `Linter`, `New`, `Run`, `WithMergedConfig`, `WithMergedConfigFromComments`, `Error`, `LinterRuleI`, `LinterRule`, `RuleName`, `Run`, `IsDeprecated`, `IsExperimental`, `LintFormatShort`, `LintWarnFunc`, `ParseLintOptions`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
Linter instances hold config and accumulated warnings in memory; WithMergedConfig creates merged config copies and Error aggregates warnings into a returned error.

## Dependencies and Integration Points
Dependencies: Dockerfile parser AST and source ranges; wrapped error reporting.
Integrated with instruction parsing and frontend check options; warnings travel through parser ranges and gateway Warn/Error reporting.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
No direct test in this file; behavior is exercised through higher-level parser, instruction, dockerui, and integration tests in adjacent packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/linter/linter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/linter/ruleset.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/linter/ruleset.go

## Purpose
Static Dockerfile lint rule catalog with names, descriptions, URLs, severity, formatting functions, and deprecation/experimental flags. The file has 194 lines and belongs to package `linter`.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: fmt.
Integrated with instruction parsing and frontend check options; warnings travel through parser ranges and gateway Warn/Error reporting.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
No direct test in this file; behavior is exercised through higher-level parser, instruction, dockerui, and integration tests in adjacent packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/linter/ruleset.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/directives.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/directives.go

## Purpose
Parser-directive scanner for syntax, escape, and check directives, including BOM/shebang handling and JSON check directive parsing. The file has 200 lines and belongs to package `parser`.

## Important APIs, Types, and Functions
Important symbols: `validDirectives`, `Directive`, `DirectiveParser`, `directiveRegexp`, `SetComment`, `ParseLine`, `ParseAll`, `DetectSyntax`, `ParseDirective`, `parseDirective`, `detectDirectiveFromParser`, `discardShebang`, `discardBOM`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated as the first Dockerfile frontend stage: dockerui reads source bytes, parser.Parse builds AST, instructions.Parse converts nodes, and errors carry parser.Range locations.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/parser/directives_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/json_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/directives.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/directives_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/directives_test.go

## Purpose
Directive parser tests covering supported directives, ordering quirks, syntax detection, BOM handling, and check directive parsing. The file has 163 lines and belongs to package `parser`.

## Important APIs, Types, and Functions
Test entry points: `TestDirectives`, `TestDetectSyntax`, `TestDetectSyntaxBOM`, `TestParseDirective`.

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
Direct test coverage in this file: `TestDirectives`, `TestDetectSyntax`, `TestDetectSyntaxBOM`, `TestParseDirective`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/directives_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/dumper/main.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/dumper/main.go

## Purpose
Small AST dumper command-line utility that parses a Dockerfile and prints parser.Node.Dump output. The file has 29 lines and belongs to package `main`.

## Important APIs, Types, and Functions
Important symbols: `main`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: Dockerfile parser AST and source ranges.
Integrated as the first Dockerfile frontend stage: dockerui reads source bytes, parser.Parse builds AST, instructions.Parse converts nodes, and errors carry parser.Range locations.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
No direct test in this file; behavior is exercised through higher-level parser, instruction, dockerui, and integration tests in adjacent packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/dumper/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/errors.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/errors.go

## Purpose
Parser location error wrappers and Range/Position helpers used to attach source line spans to parse and instruction errors. The file has 71 lines and belongs to package `parser`.

## Important APIs, Types, and Functions
Important symbols: `LocationError`, `Unwrap`, `Range`, `Position`, `withLocation`, `WithLocation`, `SetLocation`, `setLocation`, `toRanges`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated as the first Dockerfile frontend stage: dockerui reads source bytes, parser.Parse builds AST, instructions.Parse converts nodes, and errors carry parser.Range locations.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/errors_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/directives_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/json_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_heredoc_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/json_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/json_test.go

## Purpose
Parser tests for JSON array-of-strings recognition and invalid JSON array rejection. The file has 57 lines and belongs to package `parser`.

## Important APIs, Types, and Functions
Test entry points: `TestJSONArraysOfStrings`.

## Control Flow
The tests construct table-driven Dockerfile snippets or integration build contexts, invoke the target parser/frontend path, and assert exact parsed structures, warnings, error messages, source maps, or build output files.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated with Dockerfile frontend integration tests and BuildKit gateway solve paths.

## Risks and Edge Cases
Primary risk is incomplete coverage if new parser/frontend flags are added without expanding these assertions; integration tests also depend on sandbox capabilities and external context setup.

## Test Signals
Direct test coverage in this file: `TestJSONArraysOfStrings`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/json_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers.go

## Purpose
Low-level Dockerfile line parsers that turn command arguments into parser.Node linked lists and JSON/shell attributes. The file has 373 lines and belongs to package `parser`.

## Important APIs, Types, and Functions
Important symbols: `parseIgnore`, `parseSubCommand`, `parseWords`, `parseNameVal`, `newKeyValueNode`, `appendKeyValueNode`, `parseEnv`, `parseLabel`, `parseNameOrNameVal`, `parseStringsWhitespaceDelimited`, `parseString`, `parseJSON`, `parseMaybeJSON`, `parseMaybeJSONToList`, `parseHealthConfig`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated as the first Dockerfile frontend stage: dockerui reads source bytes, parser.Parse builds AST, instructions.Parse converts nodes, and errors carry parser.Range locations.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/parser/directives_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/json_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers_test.go

## Purpose
Focused tests for name/value parsing in old and new ENV/ARG-like forms, including empty value rejection. The file has 59 lines and belongs to package `parser`.

## Important APIs, Types, and Functions
Test entry points: `TestParseNameValOldFormat`, `TestParseNameValNewFormat`, `TestParseNameValWithoutVal`.

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
Direct test coverage in this file: `TestParseNameValOldFormat`, `TestParseNameValNewFormat`, `TestParseNameValWithoutVal`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/parser.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/parser.go

## Purpose
Core Dockerfile parser that scans input, applies directives and continuations, builds AST nodes, extracts heredocs, preserves comments and line ranges, and emits warnings. The file has 582 lines and belongs to package `parser`.

## Important APIs, Types, and Functions
Important symbols: `Node`, `Location`, `Dump`, `lines`, `canContainHeredoc`, `AddChild`, `Heredoc`, `DefaultEscapeToken`, `directives`, `setEscapeToken`, `possibleParserDirective`, `newDefaultDirectives`, `init`, `newNodeFromLine`, `Result`, `Warning`, `PrintWarnings`, `Parse`, `heredocFromMatch`, `ParseHeredoc`, `MustParseHeredoc`, `heredocsFromLine`, `ChompHeredocContent`, `trimComments`, plus helper symbols used internally.

## Control Flow
Parse scans physical lines with a custom split function, strips BOM/comments, applies parser directives, joins continuations, emits empty-continuation warnings, constructs Nodes through splitCommand/line parsers, then consumes heredoc bodies before adding children to the root AST.

## State and Persistence
Parser state is per Parse call: directives, current line counter, comment buffer, continuation buffer, warnings, AST nodes, and heredoc content. It has no package-global mutation after dispatch initialization.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated as the first Dockerfile frontend stage: dockerui reads source bytes, parser.Parse builds AST, instructions.Parse converts nodes, and errors carry parser.Range locations.

## Risks and Edge Cases
Risks include line-continuation edge cases, bufio token limits, heredoc termination/chomp handling, comment/directive ordering, and location accuracy for multi-line instructions.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/parser/directives_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/json_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_heredoc_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_heredoc_test.go

## Purpose
Parser-level heredoc tests for extraction, quoted terminators, JSON exclusion, chomping, helper parsing, and malformed heredoc tokens. The file has 446 lines and belongs to package `parser`.

## Important APIs, Types, and Functions
Test entry points: `TestParseExtractsHeredoc`, `TestParseJSONHeredoc`, `TestHeredocChomp`, `TestParseHeredocHelpers`, `TestHeredocsFromLine`.

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
Direct test coverage in this file: `TestParseExtractsHeredoc`, `TestParseJSONHeredoc`, `TestHeredocChomp`, `TestParseHeredocHelpers`, `TestHeredocsFromLine`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_heredoc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_test.go

## Purpose
Parser corpus tests that parse positive and negative fixture directories, word parsing cases, line numbers, empty continuation warnings, and scanner limits. The file has 181 lines and belongs to package `parser`.

## Important APIs, Types, and Functions
Test entry points: `TestParseErrorCases`, `TestParseCases`, `TestParseWords`, `TestParseIncludesLineNumbers`, `TestParseWarnsOnEmptyContinutationLine`, `TestParseReturnsScannerErrors`.

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
Direct test coverage in this file: `TestParseErrorCases`, `TestParseCases`, `TestParseWords`, `TestParseIncludesLineNumbers`, `TestParseWarnsOnEmptyContinutationLine`, `TestParseReturnsScannerErrors`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/split_command.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/split_command.go

## Purpose
Command splitter that separates instruction name, builder flags, and remaining args while respecting escape tokens and flag terminators. The file has 122 lines and belongs to package `parser`.

## Important APIs, Types, and Functions
Important symbols: `splitCommand`, `extractBuilderFlags`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: strings; unicode.
Integrated as the first Dockerfile frontend stage: dockerui reads source bytes, parser.Parse builds AST, instructions.Parse converts nodes, and errors carry parser.Range locations.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/parser/directives_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/json_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/line_parsers_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_heredoc_test.go`, `sources/cloud-native/buildkit/frontend/dockerfile/parser/parser_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/split_command.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfile-line/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfile-line/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 35 lines and 14 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM brimstone/ubuntu:14.04`; `ENV GOPATH \`; `/go`; `RUN apt-get update \`; `&& dpkg -l | awk '/^ii/ {print $2}' > /tmp/dpkg.clean \`; `&& apt-get --no-install-recommends install -y git golang ca-certificates \`; `&& apt-get clean \`; `&& rm -rf /var/lib/apt/lists \`; `&& go get -v github.com/brimstone/consuldock \`; `&& mv $GOPATH/bin/consuldock /usr/local/bin/consuldock \`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 14 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfile-line/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/empty_dockerfile/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/empty_dockerfile/Dockerfile

## Purpose
Negative parser fixture that intentionally exercises Dockerfile rejection behavior or empty-input handling. The fixture has 0 lines and 0 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: empty/comment-only Dockerfile input.

## Control Flow
The fixture has no executable Dockerfile instructions; parser tests use it to verify empty/comment-only inputs fail with the expected no-instructions path.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is intentional invalid input: changing parser leniency can flip this fixture from error to success, weakening negative coverage.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/empty_dockerfile/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/env_no_value/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/env_no_value/Dockerfile

## Purpose
Negative parser fixture that intentionally exercises Dockerfile rejection behavior or empty-input handling. The fixture has 3 lines and 2 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM busybox`; `ENV PATH`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 2 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is intentional invalid input: changing parser leniency can flip this fixture from error to success, weakening negative coverage.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/env_no_value/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/only_comments/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/only_comments/Dockerfile

## Purpose
Negative parser fixture that intentionally exercises Dockerfile rejection behavior or empty-input handling. The fixture has 3 lines and 0 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: empty/comment-only Dockerfile input.

## Control Flow
The fixture has no executable Dockerfile instructions; parser tests use it to verify empty/comment-only inputs fail with the expected no-instructions path.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is intentional invalid input: changing parser leniency can flip this fixture from error to success, weakening negative coverage.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/only_comments/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/shykes-nested-json/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/shykes-nested-json/Dockerfile

## Purpose
Negative parser fixture that intentionally exercises Dockerfile rejection behavior or empty-input handling. The fixture has 1 lines and 1 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `CMD [ "echo", [ "nested json" ] ]`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 1 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is intentional invalid input: changing parser leniency can flip this fixture from error to success, weakening negative coverage.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles-negative/shykes-nested-json/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/ADD-COPY-with-JSON/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/ADD-COPY-with-JSON/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 11 lines and 10 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM	ubuntu:14.04`; `LABEL	maintainer	Seongyeol Lim <seongyeol37@gmail.com>`; `COPY	.	/go/src/github.com/docker/docker`; `ADD		.	/`; `ADD		null /`; `COPY	nullfile /tmp`; `ADD		[ "vimrc", "/tmp" ]`; `COPY	[ "bashrc", "/tmp" ]`; `COPY	[ "test file", "/tmp" ]`; `ADD		[ "test file", "/tmp/test file" ]`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 10 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/ADD-COPY-with-JSON/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/args/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/args/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 3 lines and 3 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `ARG foo bar=baz`; `FROM ubuntu`; `ARG abc="123 456" def`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 3 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/args/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/brimstone-consuldock/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/brimstone-consuldock/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 26 lines and 15 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM brimstone/ubuntu:14.04`; `LABEL maintainer brimstone@the.narro.ws`; `ENV GOPATH /go`; `ENTRYPOINT ["/usr/local/bin/consuldock"]`; `RUN apt-get update \`; `&& dpkg -l | awk '/^ii/ {print $2}' > /tmp/dpkg.clean \`; `&& apt-get --no-install-recommends install -y git golang ca-certificates \`; `&& apt-get clean \`; `&& rm -rf /var/lib/apt/lists \`; `&& go get -v github.com/brimstone/consuldock \`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 15 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/brimstone-consuldock/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/brimstone-docker-consul/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/brimstone-docker-consul/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 52 lines and 40 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM brimstone/ubuntu:14.04`; `CMD []`; `ENTRYPOINT ["/usr/bin/consul", "agent", "-server", "-data-dir=/consul", "-client=0.0.0.0",`; `EXPOSE 8500 8600 8400 8301 8302`; `RUN apt-get update \`; `&& apt-get --no-install-recommends install -y unzip wget \`; `&& apt-get clean \`; `&& rm -rf /var/lib/apt/lists`; `RUN cd /tmp \`; `&& wget https://dl.bintray.com/mitchellh/consul/0.3.1_web_ui.zip \`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 40 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/brimstone-docker-consul/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/continue-at-eof/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/continue-at-eof/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 3 lines and 2 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM alpine:3.5`; `RUN something \`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 2 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/continue-at-eof/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/continueIndent/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/continueIndent/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 36 lines and 30 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM ubuntu:14.04`; `RUN echo hello\`; `world\`; `goodnight  \`; `moon\`; `light\`; `ning`; `RUN echo hello  \`; `world`; `RUN echo hello  \`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 30 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/continueIndent/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/cpuguy83-nagios/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/cpuguy83-nagios/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 54 lines and 41 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM cpuguy83/ubuntu`; `ENV NAGIOS_HOME /opt/nagios`; `ENV NAGIOS_USER nagios`; `ENV NAGIOS_GROUP nagios`; `ENV NAGIOS_CMDUSER nagios`; `ENV NAGIOS_CMDGROUP nagios`; `ENV NAGIOSADMIN_USER nagiosadmin`; `ENV NAGIOSADMIN_PASS nagios`; `ENV APACHE_RUN_USER nagios`; `ENV APACHE_RUN_GROUP nagios`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 41 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/cpuguy83-nagios/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/docker/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/docker/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 94 lines and 46 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM	ubuntu:14.04`; `LABEL	maintainer	Tianon Gravi <admwiggin@gmail.com> (@tianon)`; `RUN	apt-get update && DEBIAN_FRONTEND=noninteractive apt-get --no-install-recommends insta`; `apt-utils \`; `aufs-tools \`; `automake \`; `btrfs-tools \`; `build-essential \`; `curl \`; `dpkg-sig \`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 46 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/docker/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/env/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/env/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 23 lines and 21 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM ubuntu`; `ENV name value`; `ENV name=value`; `ENV name=value name2=value2`; `ENV name="value value1"`; `ENV name=value\ value2`; `ENV name="value'quote space'value2"`; `ENV name='value"double quote"value2'`; `ENV name=value\ value2 name2=value2\ value3`; `ENV name="a\"b"`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 21 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/env/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escape-after-comment/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escape-after-comment/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 9 lines and 4 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM image`; `LABEL maintainer foo@bar.com`; `ENV GOPATH \`; `\go`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 4 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escape-after-comment/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escape-nonewline/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escape-nonewline/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 7 lines and 4 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM image`; `LABEL maintainer foo@bar.com`; `ENV GOPATH \``; `\go`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 4 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escape-nonewline/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escape-with-syntax/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escape-with-syntax/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 5 lines and 2 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM \``; `image`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 2 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escape-with-syntax/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escape/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escape/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 6 lines and 4 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM image`; `LABEL maintainer foo@bar.com`; `ENV GOPATH \``; `\go`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 4 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escape/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escapes/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escapes/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 14 lines and 9 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM ubuntu:14.04`; `LABEL maintainer Erik \\Hollensbe <erik@hollensbe.org>\"`; `RUN apt-get \update && \`; `apt-get \"install znc -y`; `ADD \conf\\" /.znc`; `RUN foo \`; `bar \`; `baz`; `CMD [ "\/usr\\\"/bin/znc", "-f", "-r" ]`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 9 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/escapes/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/flags/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/flags/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 10 lines and 10 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM scratch`; `COPY foo /tmp/`; `COPY --user=me foo /tmp/`; `COPY --doit=true foo /tmp/`; `COPY --user=me --doit=true foo /tmp/`; `COPY --doit=true -- foo /tmp/`; `COPY -- foo /tmp/`; `CMD --doit [ "a", "b" ]`; `CMD --doit=true -- [ "a", "b" ]`; `CMD --doit -- [ ]`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 10 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/flags/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/health/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/health/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 11 lines and 11 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM debian`; `ADD check.sh main.sh /app/`; `CMD /app/main.sh`; `HEALTHCHECK`; `HEALTHCHECK --interval=5s --timeout=3s --retries=3 \`; `CMD /app/check.sh --quiet`; `HEALTHCHECK CMD`; `HEALTHCHECK   CMD   a b`; `HEALTHCHECK --timeout=3s CMD ["foo"]`; `HEALTHCHECK CONNECT TCP 7000`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 11 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/health/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/influxdb/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/influxdb/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 15 lines and 11 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM ubuntu:14.04`; `RUN apt-get update && apt-get install wget -y`; `RUN wget http://s3.amazonaws.com/influxdb/influxdb_latest_amd64.deb`; `RUN dpkg -i influxdb_latest_amd64.deb`; `RUN rm -r /opt/influxdb/shared`; `VOLUME /opt/influxdb/shared`; `CMD /usr/bin/influxdb --pidfile /var/run/influxdb.pid -config /opt/influxdb/shared/config.`; `EXPOSE 8083`; `EXPOSE 8086`; `EXPOSE 8090`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 11 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/influxdb/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-json-inside-string-double/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-json-inside-string-double/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 1 lines and 1 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `CMD "[\"echo\", \"Phew, I just managed to escaped those double quotes\"]"`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 1 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-json-inside-string-double/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-json-inside-string/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-json-inside-string/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 1 lines and 1 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `CMD '["echo", "Well, JSON in a string is JSON too?"]'`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 1 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-json-inside-string/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-single-quotes/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-single-quotes/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 1 lines and 1 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `CMD ['echo','single quotes are invalid JSON']`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 1 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-single-quotes/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-unterminated-bracket/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-unterminated-bracket/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 1 lines and 1 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `CMD ["echo", "Please, close the brackets when you're done"`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 1 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-unterminated-bracket/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-unterminated-string/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-unterminated-string/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 1 lines and 1 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `CMD ["echo", "look ma, no quote!]`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 1 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/jeztah-invalid-json-unterminated-string/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/json/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/json/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 8 lines and 8 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `CMD []`; `CMD [""]`; `CMD ["a"]`; `CMD ["a","b"]`; `CMD [ "a", "b" ]`; `CMD [	"a",	"b"	]`; `CMD	[	"a",	"b"	]`; `CMD ["abc 123", "♥", "☃", "\" \\ \/ \b \f \n \r \t \u0000"]`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 8 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/json/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/kartar-entrypoint-oddities/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/kartar-entrypoint-oddities/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 7 lines and 7 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM ubuntu:14.04`; `LABEL maintainer James Turnbull "james@example.com"`; `ENV REFRESHED_AT 2014-06-01`; `RUN apt-get update`; `RUN apt-get --no-install-recommends install -y redis-server redis-tools`; `EXPOSE 6379`; `ENTRYPOINT [ "/usr/bin/redis-server" ]`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 7 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/kartar-entrypoint-oddities/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/lk4d4-the-edge-case-generator/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/lk4d4-the-edge-case-generator/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 48 lines and 32 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM busybox:buildroot-2014.02`; `LABEL maintainer docker <docker@docker.io>`; `ONBUILD RUN ["echo", "test"]`; `ONBUILD RUN echo test`; `ONBUILD COPY . /`; `RUN ["ls", "-la"]`; `RUN ["echo", "'1234'"]`; `RUN echo "1234"`; `RUN echo 1234`; `RUN echo '1234' && \`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 32 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/lk4d4-the-edge-case-generator/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/mail/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/mail/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 16 lines and 14 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM ubuntu:14.04`; `RUN apt-get update -qy && apt-get install mutt offlineimap vim-nox abook elinks curl tmux `; `ADD .muttrc /`; `ADD .offlineimaprc /`; `ADD .tmux.conf /`; `ADD mutt /.mutt`; `ADD vim /.vim`; `ADD vimrc /.vimrc`; `ADD crontab /etc/crontab`; `RUN chmod 644 /etc/crontab`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 14 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/mail/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/multiple-volumes/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/multiple-volumes/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 3 lines and 2 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM foo`; `VOLUME /opt/nagios/var /opt/nagios/etc /opt/nagios/libexec /var/log/apache2 /usr/share/snm`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 2 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/multiple-volumes/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/mumble/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/mumble/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 7 lines and 4 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM ubuntu:14.04`; `RUN apt-get update && apt-get install libcap2-bin mumble-server -y`; `ADD ./mumble-server.ini /etc/mumble-server.ini`; `CMD /usr/sbin/murmurd`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 4 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/mumble/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/nginx/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/nginx/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 14 lines and 11 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM ubuntu:14.04`; `LABEL maintainer Erik Hollensbe <erik@hollensbe.org>`; `RUN apt-get update && apt-get install nginx-full -y`; `RUN rm -rf /etc/nginx`; `ADD etc /etc/nginx`; `RUN chown -R root:root /etc/nginx`; `RUN /usr/sbin/nginx -qt`; `RUN mkdir /www`; `CMD ["/usr/sbin/nginx"]`; `VOLUME /www`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 11 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/nginx/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/tf2/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/tf2/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 23 lines and 20 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM ubuntu:12.04`; `EXPOSE 27015`; `EXPOSE 27005`; `EXPOSE 26901`; `EXPOSE 27020`; `RUN apt-get update && apt-get install libc6-dev-i386 curl unzip -y`; `RUN mkdir -p /steam`; `RUN curl http://media.steampowered.com/client/steamcmd_linux.tar.gz | tar vxz -C /steam`; `ADD ./script /steam/script`; `RUN /steam/steamcmd.sh +runscript /steam/script`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 20 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/tf2/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/trailing-backslash/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/trailing-backslash/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 17 lines and 14 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM hello-world`; `ENV A path`; `ENV B another\\path`; `ENV C trailing\\backslash\\`; `ENV D This should not be appended to C`; `ENV E hello\`; `\`; `world`; `ENV F hello\`; `\`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 14 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/trailing-backslash/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/weechat/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/weechat/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 9 lines and 6 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM ubuntu:14.04`; `RUN apt-get update -qy && apt-get install tmux zsh weechat-curses -y`; `ADD .weechat /.weechat`; `ADD .tmux.conf /`; `RUN echo "export TERM=screen-256color" >/.zshenv`; `CMD zsh -c weechat`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 6 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/weechat/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/znc/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/znc/Dockerfile

## Purpose
Parser fixture Dockerfile used as corpus input for AST dumps, line accounting, JSON parsing, continuation handling, and real-world instruction coverage. The fixture has 7 lines and 5 non-comment instruction/continuation lines.

## Important APIs, Types, and Functions
No Go API surface; the file is consumed as parser fixture data.
Representative fixture content: `FROM ubuntu:14.04`; `LABEL maintainer Erik Hollensbe <erik@hollensbe.org>`; `RUN apt-get update && apt-get install znc -y`; `ADD conf /.znc`; `CMD [ "/usr/bin/znc", "-f", "-r" ]`.

## Control Flow
Test code feeds the Dockerfile text to parser.Parse; the parser scans 5 non-comment instruction/continuation lines, applies directive and continuation rules, and compares the resulting AST/error against expected corpus output.

## State and Persistence
No runtime state or persistence; the file is immutable fixture input checked into the parser corpus.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated only through parser test discovery under parser/testfiles and parser/testfiles-negative.

## Risks and Edge Cases
Risk signal is corpus drift: formatting, continuation, quoting, or instruction edits can alter expected AST dumps and line-number assertions.

## Test Signals
Covered indirectly by parser corpus tests in parser_test.go and related JSON/heredoc/line-number assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/parser/testfiles/znc/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/shell/equal_env_unix.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/shell/equal_env_unix.go

## Purpose
Unix environment key equality implementation with case-sensitive comparison and identity normalization. The file has 17 lines and belongs to package `shell`.

## Important APIs, Types, and Functions
Important symbols: `EqualEnvKeys`, `NormalizeEnvKey`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated by parser heredoc detection, line parsers, and Dockerfile variable expansion paths that need shell-compatible quote/env semantics.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/shell/lex_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/shell/equal_env_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/shell/equal_env_windows.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/shell/equal_env_windows.go

## Purpose
Windows environment key equality implementation with case-insensitive comparison and uppercase normalization. The file has 17 lines and belongs to package `shell`.

## Important APIs, Types, and Functions
Important symbols: `EqualEnvKeys`, `NormalizeEnvKey`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated by parser heredoc detection, line parsers, and Dockerfile variable expansion paths that need shell-compatible quote/env semantics.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/shell/lex_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/shell/equal_env_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/shell/lex.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/shell/lex.go

## Purpose
Dockerfile shell-like lexer for word splitting, quote handling, variable expansion, modifier operations, heredoc token recognition, and environment capture. The file has 707 lines and belongs to package `shell`.

## Important APIs, Types, and Functions
Important symbols: `EnvGetter`, `Lex`, `NewLex`, `ProcessWord`, `ProcessWords`, `ProcessWordResult`, `ProcessWordWithMatches`, `initWord`, `process`, `shellWord`, `process`, `wordsStruct`, `addChar`, `addRawChar`, `addString`, `addRawString`, `getWords`, `processStopOn`, `processSingleQuote`, `processDoubleQuote`, `processDollar`, `processName`, `processPossibleHeredoc`, `isSpecialParam`, plus helper symbols used internally.

## Control Flow
Lex initializes a reusable shellWord scanner, walks runes until EOF or a requested terminator, delegates quotes/dollar/heredoc markers to specialized handlers, records matched/unmatched variables, and returns both expanded text and split words.

## State and Persistence
Lex is explicitly not concurrency-safe because a Lex instance reuses shellWord/scanner/buffers across calls. Environment maps are created per input slice.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated by parser heredoc detection, line parsers, and Dockerfile variable expansion paths that need shell-compatible quote/env semantics.

## Risks and Edge Cases
Risks include shell expansion compatibility gaps, unsupported ${} modifiers, pattern regex conversion mistakes, platform-specific env key behavior, and accidental concurrent use of one Lex instance.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/shell/lex_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/shell/lex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/shell/lex_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/shell/lex_test.go

## Purpose
Shell lexer tests for pattern conversion, variable expansion modifiers, mandatory env errors, word splitting, platform-specific environment matching, and match capture. The file has 658 lines and belongs to package `shell`.

## Important APIs, Types, and Functions
Test entry points: `TestConvertShellPatternToRegex`, `TestReverseString`, `TestReversePattern`, `TestShellParserMandatoryEnvVars`, `TestShellParser4EnvVars`, `TestShellParser4Words`, `TestGetEnv`, `TestProcessWithMatches`, `TestProcessWithMatchesPlatform`.

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
Direct test coverage in this file: `TestConvertShellPatternToRegex`, `TestReverseString`, `TestReversePattern`, `TestShellParserMandatoryEnvVars`, `TestShellParser4EnvVars`, `TestShellParser4Words`, `TestGetEnv`, `TestProcessWithMatches`, `TestProcessWithMatchesPlatform`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/shell/lex_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/version/dockerfile.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/version/dockerfile.go

## Purpose
Dockerfile frontend version parser that normalizes tags into semantic version values with labs/latest/channel handling. The file has 48 lines and belongs to package `version`.

## Important APIs, Types, and Functions
Important symbols: `Version`, `normalizeDockerfileVersion`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: wrapped error reporting.
Integrated by Dockerfile frontend version negotiation and syntax image tag interpretation.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/version/dockerfile_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/version/dockerfile.go -->

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/version/version.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/version/version.go

## Purpose
Tiny version package constant holder for the bundled Dockerfile frontend version value. The file has 3 lines and belongs to package `version`.

## Important APIs, Types, and Functions
Important symbols: `version`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: No external imports; behavior is local to the package or the file is a Dockerfile fixture.
Integrated by Dockerfile frontend version negotiation and syntax image tag interpretation.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerfile/version/dockerfile_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/attr.go -->
# sources/cloud-native/buildkit/frontend/dockerui/attr.go

## Purpose
dockerui option parsers for platforms, resolve mode, extra hosts, shm size, ulimits, Linux resources, network mode, local session IDs, and prefixed option filtering. The file has 207 lines and belongs to package `dockerui`.

## Important APIs, Types, and Functions
Important symbols: `parsePlatforms`, `parseResolveMode`, `parseExtraHosts`, `parseShmSize`, `parseUlimits`, `parseLinuxResources`, `parseNetMode`, `parseLocalSessionIDs`, `filter`.

## Control Flow
Control flow is direct and package-local: inputs are parsed or transformed into typed values, validation errors return immediately with context, and successful results are consumed by adjacent Dockerfile frontend packages.

## State and Persistence
State is limited to local variables, table-driven test data, or immutable package constants; there is no durable persistence in this file.

## Dependencies and Integration Points
Dependencies: BuildKit LLB state/options; wrapped error reporting; CSV-style flag value parsing; platform/test filesystem helpers.
Integrated with gateway/client BuildOpts, LLB source construction, exporter metadata, frontend inputs, named contexts, .dockerignore, and source-date-epoch behavior.

## Risks and Edge Cases
Risks center on preserving exact Dockerfile frontend compatibility: error text, validation strictness, source locations, and platform/build option semantics are externally observable.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerui/build_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/attr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/build.go -->
# sources/cloud-native/buildkit/frontend/dockerui/build.go

## Purpose
dockerui build coordinator that runs per-platform build functions, attaches refs/config metadata, handles multi-platform exporter metadata, and normalizes platform IDs. The file has 155 lines and belongs to package `dockerui`.

## Important APIs, Types, and Functions
Important symbols: `BuildResult`, `BuildFunc`, `Build`, `ResultBuilder`, `Finalize`, `EachPlatform`, `extendWindowsPlatform`, `makeExportPlatform`.

## Control Flow
Build expands target platforms, launches one errgroup task per platform, calls the provided BuildFunc, serializes image/base configs, stores refs and metadata with single- or multi-platform keys, and Finalize adds exporter platform metadata.

## State and Persistence
ResultBuilder accumulates refs and exporter metadata in client.Result memory. Per-platform writes share one result object, so correctness depends on BuildKit result APIs tolerating the errgroup write pattern.

## Dependencies and Integration Points
Dependencies: BuildKit gateway client/result APIs; wrapped error reporting; platform/test filesystem helpers.
Integrated with gateway/client BuildOpts, LLB source construction, exporter metadata, frontend inputs, named contexts, .dockerignore, and source-date-epoch behavior.

## Risks and Edge Cases
Risks include closure capture in concurrent platform loops, shared Result mutation under errgroup, platform ID/config metadata mismatches, and Windows OSVersion/OSFeatures normalization regressions.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerui/build_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/build.go -->

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/config.go -->
# sources/cloud-native/buildkit/frontend/dockerui/config.go

## Purpose
dockerui client configuration and build-context entrypoints that parse gateway opts, read Dockerfiles, load .dockerignore, expose build args/labels/cache/SBOM settings, and construct local contexts. The file has 576 lines and belongs to package `dockerui`.

## Important APIs, Types, and Functions
Important symbols: `Config`, `Client`, `SBOM`, `Source`, `ContextOpt`, `validateMinCaps`, `NewClient`, `BuildOpts`, `GatewayClient`, `init`, `buildContext`, `ReadEntrypoint`, `MainContext`, `NamedContext`, `IsNoCache`, `DockerIgnorePatterns`, `DefaultMainContext`, `WithInternalName`, `dockerIgnorePatterns`.

## Control Flow
NewClient validates gateway capabilities, snapshots BuildOpts, init parses all frontend options into Config fields, and methods lazily build context state, read Dockerfile/.dockerignore through LLB solves, and expose no-cache/named-context decisions.

## State and Persistence
Client caches BuildOpts, dockerignore bytes/name under a mutex, buildContext through flightcontrol.CachedGroup, parsed config fields in memory, and local session ID overrides. It persists nothing itself; LLB solves and gateway refs carry external state.

## Dependencies and Integration Points
Dependencies: Dockerfile linter rules/config; BuildKit LLB state/options; BuildKit gateway client/result APIs; wrapped error reporting; platform/test filesystem helpers; Docker ignore pattern parsing.
Integrated with gateway/client BuildOpts, LLB source construction, exporter metadata, frontend inputs, named contexts, .dockerignore, and source-date-epoch behavior.

## Risks and Edge Cases
Risks include subtle frontend option compatibility, cache import parsing across old/new APIs, .dockerignore caching races, capability-gated behavior, and errors masked while probing optional Dockerignore files.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerui/build_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/context.go -->
# sources/cloud-native/buildkit/frontend/dockerui/context.go

## Purpose
dockerui build context detection for local, Git, HTTP, frontend inputs, source date epoch metadata, archive unpacking, and subdirectory scoping. The file has 361 lines and belongs to package `dockerui`.

## Important APIs, Types, and Functions
Important symbols: `httpPrefix`, `buildContext`, `marshalOpts`, `initContext`, `ResolveMainContextSourceDateEpoch`, `archiveMaxTimeFromHTTPArchive`, `cloneSourceOp`, `sourceOpFromState`, `DetectGitContext`, `DetectHTTPContext`, `isArchive`, `scopeToSubDir`.

## Control Flow
initContext resolves local option names, then chooses Git, HTTP, frontend input, or local context paths; remote states are marshaled to SourceOp metadata, optional subdirectories are scoped with LLB Copy, and source-date-epoch helpers query metadata or scan archive mtimes.

## State and Persistence
buildContext holds selected context/dockerfile LLB states, source op metadata, HTTP reference details, and archive flags in memory. Remote context content is read through gateway references, not persisted by this package.

## Dependencies and Integration Points
Dependencies: BuildKit LLB state/options; BuildKit gateway client/result APIs; wrapped error reporting.
Integrated with gateway/client BuildOpts, LLB source construction, exporter metadata, frontend inputs, named contexts, .dockerignore, and source-date-epoch behavior.

## Risks and Edge Cases
Risks include misdetecting HTTP archives from short headers, remote metadata errors affecting reproducibility, Git ref option parsing, multiple source ops from composed states, and subdirectory scoping changing source roots.

## Test Signals
Covered by adjacent tests such as `sources/cloud-native/buildkit/frontend/dockerui/build_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/context.go -->
