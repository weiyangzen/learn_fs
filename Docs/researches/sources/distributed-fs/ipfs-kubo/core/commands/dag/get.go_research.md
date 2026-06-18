<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/get.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dag/get.go

## Purpose

Implements `ipfs dag get`, resolving an IPLD path and serializing the target node in a requested output codec.

## Important APIs, Types, and Functions

`dagGet(req, res, env)` is the handler. It uses `output-codec`, CoreAPI `ResolvePath`, `Dag().Get`, IPLD legacy `UniversalNode`, `traversal.Get`, and multicodec encoder lookup.

## Control Flow

The handler obtains CoreAPI, parses the output multicodec, converts the input to a path, resolves root plus remainder, fetches the root DAG node, casts it to a universal IPLD node, traverses any remainder path, looks up the requested encoder, and streams encoded output through an `io.Pipe`.

## State and Persistence Behavior

Read-only. It may fetch DAG blocks through CoreAPI depending on online/offline request state.

## Dependencies and Integration Points

Depends on boxo path conversion, `go-ipld-legacy`, IPLD prime traversal and multicodec registries, `cmdenv`, and `cmdutils`.

## Risks and Edge Cases

The fetched object must implement `ipldlegacy.UniversalNode`; unsupported node implementations error. Encoder errors occur in the goroutine and are propagated through `CloseWithError`. Remainder traversal can fail on schema/path mismatches.

## Test Signals

No direct tests. Good coverage would include codec lookup failures, path remainder traversal, unsupported node type, and pipe error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/get.go -->
