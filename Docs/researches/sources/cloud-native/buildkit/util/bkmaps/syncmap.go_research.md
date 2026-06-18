# sources/cloud-native/buildkit/util/bkmaps/syncmap.go

## Purpose
Generic typed wrapper around sync.Map. It provides Delete, Load, LoadOrStore, Range, and Store without repeated type assertions at call sites.

## Important APIs, Types, And Functions
Package: `bkmaps`. Build tags: `none`. Key declarations observed in the file: `SyncMap, Delete, Load, LoadOrStore, Range, Store`.

## Control Flow, State, And Persistence
State is the embedded sync.Map. Methods type-assert keys/values to K/V and return zero values when absent.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is panic if mixed untyped access stores incompatible values. No local tests.
