# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/scheduler/testhelpers_test.go

## Purpose
This file provides an in-memory fake filer client and streaming list response used by scheduler config-load tests.

## Important APIs and types
`fakeListStream` implements `grpc.ServerStreamingClient[filer_pb.ListEntriesResponse]` with `Recv`, metadata methods, `Context`, `SendMsg`, and `RecvMsg`. `fakeFilerClient` embeds `filer_pb.SeaweedFilerClient` and implements `LookupDirectoryEntry` plus `ListEntries`. Helper constructors `dirEntry` and `fileEntry` build test entries.

## Control flow and state behavior
`fakeListStream.Recv` returns context cancellation errors, then streams prebuilt responses until `io.EOF`. `fakeFilerClient.ListEntries` records listed directories, increments an atomic count, filters by `StartFromFileName` and `InclusiveStartFrom`, sorts names stably, applies `Limit`, and wraps entries as list responses. `LookupDirectoryEntry` searches the configured tree and returns `filer_pb.ErrNotFound` on misses. State is protected by a mutex for tree/listed access and an atomic counter for listing count.

## Dependencies and integration points
The helpers depend on `filer_pb`, `grpc`, and `metadata`. They model enough of the Seaweed filer API for `filer_pb.SeaweedList` and direct lookup calls used by config loading.

## Risks and edge cases
This fake assumes entries are all available in memory and sorted lexicographically by name. It does not model streaming backpressure, server errors other than context cancellation, permissions, or concurrent mutation during pagination. Tests depending on it should not overgeneralize to real filer behavior.

## Test signals
The helper is indirectly validated by `configload_test.go`, especially pagination and continuation token behavior around page boundaries.
