# sources/distributed-fs/seaweedfs/weed/filer/tarantool/doc.go

## Purpose

`tarantool/doc.go` documents the Tarantool filer store package. It was read as a complete 7-line file.

## Important APIs, Types, and Functions

There are no executable declarations beyond package `tarantool`. The comment notes the Tarantool library is large and enabled through `make full_install`.

## Control Flow

No runtime control flow exists.

## State and Persistence Behavior

No persistence is implemented here; see `tarantool_store.go` and `_kv.go`.

## Dependencies and Integration Points

Documentation-only integration with build/install expectations.

## Risks and Edge Cases

The comment can drift if build tags or install targets change.

## Test Signals

Compile/package documentation only.
