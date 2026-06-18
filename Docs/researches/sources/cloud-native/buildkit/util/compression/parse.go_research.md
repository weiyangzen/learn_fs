# sources/cloud-native/buildkit/util/compression/parse.go

## Purpose
Public wrappers for compression type parsing. Parse and FromMediaType delegate to package-level function variables so extensions such as nydus can wrap them.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `!nydus`. Key declarations observed in the file: `Parse, FromMediaType`.

## Control Flow, State, And Persistence
No state besides the mutable function variables defined elsewhere. Control flow is a single delegation.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is init-order/global wrapper complexity. No local tests.
