# sources/cloud-native/containerd/internal/cri/io/logger_test.go

## Purpose

This test file validates CRI log line formatting and line-splitting behavior implemented by `redirectLogs`.

## Important APIs, Types, and Functions

`TestRedirectLogs` is table-driven. Each case defines raw input, stream, max length, expected CRI tags, and expected content chunks. It invokes `redirectLogs` with an in-memory reader/writer and parses the resulting lines.

## Control Flow

For each test case, the test creates an `io.NopCloser` over the input, writes formatted logs into a buffer, splits output by newline, then validates line count and fields. It parses the timestamp with `timestampFormat`, compares stream names, compares full/partial tags, and compares payload content.

## State and Persistence Behavior

The test uses only in-memory buffers. It does increment global metrics indirectly through `redirectLogs`, but does not assert metric state.

## Dependencies and Integration Points

It depends on `testify/assert`, `testify/require`, CRI runtime log tags, and `pkg/ioutil` for a no-op write closer. It directly exercises unexported package functions because it is in package `io`.

## Risks and Edge Cases

The tests focus on log framing and splitting but not write errors, metrics, concurrent `NewCRILogger` behavior, pipe close semantics, or malformed UTF-8. The table includes important boundary cases: exact buffer size, longer than buffer, exact max, max plus one, multiple max chunks, max shorter than buffer, no limit, negative limit, and CRLF at buffer boundary.

## Test Signals

Passing tests strongly signal that CRI log format remains compatible for common and boundary line lengths. Failures identify regressions in tags, timestamp format, stream names, or payload splitting.
