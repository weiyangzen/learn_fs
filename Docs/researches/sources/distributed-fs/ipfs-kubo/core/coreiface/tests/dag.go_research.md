# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/dag.go

## Purpose
Conformance tests for DAG service add/get/path/tree/batch behavior.

## Important APIs, Types, and Functions
Defines `treeExpected` and tests `TestPut`, `TestPutWithHash`, `TestDagPath`, `TestTree`, and `TestBatch`.

## Control Flow and State
Tests create dag-cbor nodes with default and custom hashes, add them, compare exact CIDs, resolve links through `ResolvePath`, inspect `Tree` output, and verify `AddMany` makes a previously missing node retrievable.

## Dependencies and Integration Points
Depends on dag-cbor, Boxo path, CoreAPI DAG service, and `ResolvePath`.

## Risks and Test Signals
Signals include CID stability, custom multihash support, IPLD link traversal, tree enumeration, and batch commit behavior. It does not exercise pinning node adder or large DAG streaming.
