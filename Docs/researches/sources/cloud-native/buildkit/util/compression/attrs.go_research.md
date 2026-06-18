# sources/cloud-native/buildkit/util/compression/attrs.go

## Purpose
Parser for exporter compression attributes. It accepts compression, force-compression, and compression-level strings and returns a Config.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `none`. Key declarations observed in the file: `ParseAttributes`.

## Control Flow, State, And Persistence
ParseAttributes defaults to Gzip, parses type through Parse, treats empty force-compression as true, and validates bool/integer forms before setting Config fields.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are user input validation and default semantics. No local tests in this subset.
