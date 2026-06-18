# sources/cloud-native/buildkit/util/bkslices/dedupe.go

## Purpose
Generic stable de-duplication helper. It returns the first occurrence of each comparable value while preserving input order.

## Important APIs, Types, And Functions
Package: `bkslices`. Build tags: `none`. Key declarations observed in the file: `Dedupe`.

## Control Flow, State, And Persistence
Control flow keeps a seen map and appends unseen values to an output slice preallocated to input length. No persistence.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is memory proportional to input cardinality. No local tests.
