# sources/cloud-native/buildkit/util/appcontext/appcontext_windows.go

## Purpose
Windows signal list for appcontext. It maps terminationSignals to os.Interrupt.

## Important APIs, Types, And Functions
Package: `appcontext`. Build tags: `none`. Key declarations observed in the file: `terminationSignals`.

## Control Flow, State, And Persistence
Build-tagged for Windows; appcontext.go consumes the slice during signal.Notify. No persistence.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is Windows console signal semantics; build tags are the test signal.
