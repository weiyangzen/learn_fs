# sources/distributed-fs/ipfs-kubo/client/rpc/path.go

## Purpose
This file resolves mutable or IPLD paths through the HTTP API into immutable paths and nodes.

## Important APIs, Types, And Functions
`HttpApi.ResolvePath` returns an immutable path plus remaining path segments. `ResolveNode` resolves a path and then fetches the root DAG node.

## Control Flow
IPNS paths are first resolved through `Name().Resolve`. All paths then call `dag/resolve`, rebuild a path from namespace, returned CID, and remaining path, convert it to an immutable path, and return string segments.

## State And Persistence Behavior
The file is read-only against the daemon, though resolver caches may be involved server-side.

## Dependencies And Integration Points
It integrates name resolution, `dag/resolve`, Boxo path constructors, CID JSON decoding, and DAG service fetching.

## Risks And Test Signals
Risks include incorrect handling of remaining path segments and `ResolveNode` only fetching the root CID rather than traversed remainder. Signals are CoreAPI path/node resolution tests.
