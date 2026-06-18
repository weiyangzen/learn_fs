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
