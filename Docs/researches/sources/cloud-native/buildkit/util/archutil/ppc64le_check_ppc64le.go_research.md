# sources/cloud-native/buildkit/util/archutil/ppc64le_check_ppc64le.go

## Purpose
Native linux/ppc64le support stub. On matching host architecture it reports support without executing a foreign probe.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `ppc64le`. Key declarations observed in the file: `ppc64leSupported`.

## Control Flow, State, And Persistence
ppc64leSupported returns empty variant and nil error, except amd64 native support is handled separately by go-archvariant in amd64_check_amd64.go.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is assuming the native runtime is executable for its own architecture. Build tags select this file only on matching GOARCH.
