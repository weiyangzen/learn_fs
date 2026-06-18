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
