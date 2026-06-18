# sources/control-plane/rook/pkg/util/sys/parse.go

## Purpose
`parse.go` provides a small grep-like helper for finding the first matching line in text.

## Important APIs, Types, and Functions
`Grep(input, searchFor string) string` returns an empty string for empty input or pattern, otherwise scans lines and returns the first line whose content matches the regular expression.

## Control Flow, State, and Persistence
The function is pure. It ignores regex compilation/matching errors by treating them as no match.

## Dependencies and Integration Points
It depends on regexp and strings. System parsing code can use it to extract specific lines from command output.

## Risks
Invalid regex patterns are silently ignored. The function returns only the first match and preserves original whitespace. Callers needing literal matching must escape regex characters.

## Test Signals
`parse_test.go` covers empty inputs, single-line prefix and substring matching, and multi-line first-match behavior.
