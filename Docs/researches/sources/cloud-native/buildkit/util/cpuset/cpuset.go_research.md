# sources/cloud-native/buildkit/util/cpuset/cpuset.go

## Purpose
Parser, validator, and formatter for Linux cpuset-style strings such as 0-3,5.

## Important APIs, Types, And Functions
Package: `cpuset`. Build tags: `none`. Key declarations observed in the file: `MaxCPU, Parse, Validate, Format`.

## Control Flow, State, And Persistence
Parse splits comma parts, trims whitespace, expands inclusive ranges, rejects negative/reversed/non-numeric entries, and caps indices at MaxCPU to avoid huge allocations. Format sorts and collapses contiguous ranges.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are hard MaxCPU assumptions and accepting empty string as unset. cpuset_test.go covers parse, format, validation, whitespace, bounds, and round-trip.
