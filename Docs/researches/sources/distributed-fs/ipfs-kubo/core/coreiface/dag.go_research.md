# sources/distributed-fs/ipfs-kubo/core/coreiface/dag.go

## Purpose
Defines the DAG service exposed through CoreAPI.

## Important APIs, Types, and Functions
Declares `APIDagService`, embedding `ipld.DAGService` and adding `Pinning() ipld.NodeAdder`.

## Control Flow and State
No runtime flow is present. The interface requires normal DAG get/add/batch operations and a special node adder that recursively pins added nodes.

## Dependencies and Integration Points
Depends on `go-ipld-format`. It is used by CoreAPI implementations and conformance tests for DAG add/get/tree/batch behavior.

## Risks and Test Signals
Risks include divergence between normal DAG additions and pinning additions, and preserving custom CID builders/hashes. Tests in `tests/dag.go` cover dag-cbor CIDs, path traversal, tree output, and batch add.
