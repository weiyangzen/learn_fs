# sources/cloud-native/buildkit/util/appcontext/appcontext_unix.go

## Purpose
Unix signal list for appcontext. It maps terminationSignals to SIGTERM and SIGINT.

## Important APIs, Types, And Functions
Package: `appcontext`. Build tags: `!windows`. Key declarations observed in the file: `terminationSignals`.

## Control Flow, State, And Persistence
Build-tagged for non-Windows; appcontext.go consumes the slice during signal.Notify. No state beyond the package variable.

## Dependencies And Integration Points
Important dependencies/imports: `golang.org/x/sys/unix`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is platform signal behavior; build tags are the main test signal.
