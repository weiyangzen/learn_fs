# sources/cloud-native/buildkit/util/converter/tarconverter/tarconverter.go

## Purpose
Streaming tar header transformer. It rebuilds a tar stream while applying an optional HeaderConverter to each header.

## Important APIs, Types, And Functions
Package: `tarconverter`. Build tags: `none`. Key declarations observed in the file: `HeaderConverter, NewReader`.

## Control Flow, State, And Persistence
A goroutine reads src tar entries, mutates headers, writes headers and file bodies to an io.Pipe tar.Writer, then drains the source after EOF to preserve reader behavior.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are malformed tar streams, decompression-bomb concerns acknowledged by nolint, and goroutine error propagation through pipe close. tarconverter_test.go checks output padding length.
