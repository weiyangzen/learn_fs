# sources/cloud-native/moby/daemon/logger/templates/templates_test.go

## Purpose
This file provides a minimal smoke test for logger template parsing and execution.

## Important APIs, Types, And Functions
`TestNewParse` calls `NewParse("foo", "this is a {{ . }}")`, executes the template with a string, and compares the rendered output.

## Control Flow
The test parses, executes into a `bytes.Buffer`, then asserts no parse/execute error and exact output `this is a string`.

## State, Persistence, And Dependencies
No persistent state. Dependencies include `bytes`, `testing`, and `gotest.tools/v3/assert`.

## Integration Points
The test verifies the template wrapper is usable by logger tag formatting code, but does not cover the custom function map.

## Risks And Edge Cases
Coverage is intentionally shallow; JSON, split/join, case conversion, padding, truncation, and malformed templates are not tested.

## Test Signals
The file confirms the happy path for `NewParse`; deeper behavior depends on consumers or future targeted tests.
