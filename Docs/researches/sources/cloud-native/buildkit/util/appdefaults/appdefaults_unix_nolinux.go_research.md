# sources/cloud-native/buildkit/util/appdefaults/appdefaults_unix_nolinux.go

## Purpose
Non-Linux Unix system defaults for BuildKit daemon sockets. It uses /var/run/buildkit paths.

## Important APIs, Types, And Functions
Package: `appdefaults`. Build tags: `unix && !linux`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
No control flow beyond constants. Build tags select unix && !linux.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is OS-specific path convention mismatch. No local tests.
