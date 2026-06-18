# sources/distributed-fs/ipfs-kubo/core/coreiface/coreapi.go

## Purpose
Defines the top-level Go CoreAPI interface for interacting with an IPFS node.

## Important APIs, Types, and Functions
The `CoreAPI` interface exposes sub-APIs `Unixfs`, `Block`, `Dag`, `Name`, `Key`, `Pin`, `Object`, `Swarm`, `PubSub`, and `Routing`, plus `ResolvePath`, `ResolveNode`, and `WithOptions`.

## Control Flow and State
There is no implementation here. The contract partitions node behavior into sub-interfaces while allowing option-derived API views, such as offline or no-fetch views, over the same underlying node state.

## Dependencies and Integration Points
Depends on Boxo path, IPLD nodes, context, and global API options. It is consumed by commands, tests, and embedders using Kubo as a Go library.

## Risks and Test Signals
Risks include API implementations returning nil sub-APIs, inconsistent option behavior across sub-APIs, and path resolution differences between IPLD and UnixFS. `tests/api.go` orchestrates conformance coverage across all sub-APIs and checks context cleanup.
