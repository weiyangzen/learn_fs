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
