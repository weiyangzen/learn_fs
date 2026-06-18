# sources/cloud-native/buildkit/util/cpuset/cpuset_test.go

## Purpose
Unit tests for cpuset parsing, formatting, and validation. They exercise valid empty/single/range/list forms and invalid negative, non-numeric, reversed, and oversized forms.

## Important APIs, Types, And Functions
Package: `cpuset`. Build tags: `none`. Key declarations observed in the file: `TestParse, TestFormat, TestValidate`.

## Control Flow, State, And Persistence
Tests call Parse, Format, and Validate with table-style subtests and assert exact sets or formatted strings.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signal is protection against unbounded allocation through the MaxCPU checks and preservation of round-trip formatting.
