# sources/cloud-native/containerd/core/transfer/plugins/plugins.go

## Purpose
This file provides a process-local registry mapping API protobuf type URLs to concrete transfer endpoint Go types.

## Important APIs, Types, and Functions
`Register` records the type URL of an API object and the reflect type of a transfer object. `ResolveType` constructs a new registered concrete value for a received `typeurl.Any`.

## Control Flow
Endpoint packages call `Register` in `init`. Transfer proxy/server code can later inspect an incoming type URL and instantiate the matching object before unmarshalling it.

## State and Persistence
State is an in-memory global map guarded by an RW mutex. Duplicate registration and invalid type URL generation panic.

## Dependencies and Integration Points
Uses `typeurl`, `reflect`, `sync`, and `errdefs`. Archive, image store, and registry endpoints register here.

## Risks
Registration is global and panic-based for duplicates, so package initialization order and duplicate imports matter. Unknown type URLs return `ErrNotFound`.

## Test Signals
No direct tests in this file; exercised by proxy transfer marshaling/unmarshaling.
