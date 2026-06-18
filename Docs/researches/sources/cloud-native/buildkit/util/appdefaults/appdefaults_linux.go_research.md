# sources/cloud-native/buildkit/util/appdefaults/appdefaults_linux.go

## Purpose
Linux system defaults for BuildKit daemon sockets. It sets Address to unix:///run/buildkit/buildkitd.sock and traceSocketPath under /run/buildkit.

## Important APIs, Types, And Functions
Package: `appdefaults`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
No control flow; appdefaults_unix.go uses traceSocketPath in TraceSocketPath. Build tags select this on Linux.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is distribution path differences. No local tests.
