# sources/control-plane/rook/pkg/util/sys/parse_test.go

## Purpose
This file tests the `Grep()` helper.

## Important APIs, Types, and Functions
`TestGrep()` delegates to `testGrep()` for empty input/patterns, single-line matches, anchored regexes, and multi-line matches.

## Control Flow, State, and Persistence
The test is pure and deterministic.

## Dependencies and Integration Points
It depends on testify. It protects command-output parsing helpers that need first matching lines.

## Risks
Invalid regex handling is not tested. Multiple matching lines are only indirectly covered by expecting the first `test` line in a multi-line fixture.

## Test Signals
Signals include substring matching, start anchors, no-match empty result, preserved leading whitespace, and first-line-wins behavior.
