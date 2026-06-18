# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_lint_test.go

## Purpose
This file is the central integration suite for Dockerfile linter behavior. It validates warning generation, warning metadata, skip/error control through `#check` directives and `BUILDKIT_DOCKERFILE_CHECK`, progress-stream warnings, and JSON output from the `frontend.lint` subrequest. It covers rule families for casing, stage names, ignored files, secret-looking ARG/ENV names, undefined variables, malformed defaults in `FROM`, platform flags, duplicate instructions, legacy key/value syntax, EXPOSE formatting, and definition-description comments.

## Important APIs, Types, and Functions
The suite registers `lintTests` with `integration.TestFuncs`. Main test functions include `testDefinitionDescription`, `testCopyIgnoredFiles`, `testSecretsUsedInArgOrEnv`, `testAllTargetUnmarshal`, `testRuleCheckOption`, `testStageName`, `testNoEmptyContinuation`, `testConsistentInstructionCasing`, `testDuplicateStageName`, `testReservedStageName`, `testJSONArgsRecommended`, `testMaintainerDeprecated`, `testWarningsBeforeError`, `testUndeclaredArg`, `testWorkdirRelativePath`, `testUnmatchedVars`, `testMultipleInstructionsDisallowed`, `testLegacyKeyValueFormat`, `testRedundantTargetPlatform`, `testInvalidDefaultArgInFrom`, `testFromPlatformFlagConstDisallowed`, `testExposeProtoCasing`, and `testExposeInvalidFormat`. Shared helpers are `checkLinterWarnings`, `checkProgressStream`, `checkUnmarshal`, `checkVertexWarning`, `checkLintWarning`, and `unmarshalLintResults`. Data carriers are `expectedLintWarning` and `lintTestParams`.

## Control Flow and Assertions
Each rule-specific test builds a Dockerfile fixture and expected warning list, then calls `checkLinterWarnings`. That helper normalizes warning order, creates temp Dockerfile and optional `.dockerignore`, opens a BuildKit client, and runs two subtests: `warntype=progress`, which solves the Dockerfile and collects `client.VertexWarning` values from the status stream, and `warntype=unmarshal`, which invokes gateway subrequest `frontend.lint` and unmarshals `result.json` into `lint.LintResults`. Expected rule names, descriptions, URLs, detail text, levels, lines, and build-error locations are compared precisely.

## State, Persistence, and Dependencies
The file persists only temporary test inputs. State is carried through `lintTestParams`: client reuse, temp dir, Dockerfile bytes, dockerignore bytes, expected warnings, optional unmarshal-only warnings, expected build errors, and frontend attrs. Dependencies include Go `maps`, `slices`, `cmp`, sorting, regexes, BuildKit linter formatting, gateway subrequests, and platform-aware base image names.

## Integration Points
This file bridges Dockerfile parsing, linter rule implementations, frontend solve status output, gateway subrequest output, `.dockerignore` evaluation, frontend attrs, build-arg check controls, and multi-platform solve defaults. It ensures warnings are not just emitted internally but also transported through the two public observation channels.

## Risks and Test Signals
Risks include mismatched warning line numbers, divergent progress versus subrequest outputs, incorrect skip/error precedence, overzealous secret-name detection, wrong suggestions for similar variable names, ignored-file warnings conflicting with real build failures, and unreachable-target warnings being lost during lint unmarshalling. The strongest signals are duplicate validation through both progress and JSON paths, exact metadata checks, and targeted negative fixtures with no warnings.
