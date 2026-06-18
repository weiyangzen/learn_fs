# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/object.go

## Purpose
Conformance tests for ObjectAPI dag-pb link mutation, UnixFS validation, and diffs.

## Important APIs, Types, and Functions
Defines helper `putDagPbNode` and tests `TestObjectAddLink`, `TestObjectAddLinkCreate`, `TestObjectAddLinkValidation`, `TestObjectRmLink`, `TestObjectRmLinkValidation`, and `TestDiffTest`.

## Control Flow and State
Tests build raw dag-pb, UnixFS directory/file, and HAMT shard nodes; attempt add/remove link operations with and without validation bypass; check expected errors; inspect resulting link lists; and compare object diffs.

## Dependencies and Integration Points
Depends on DAG service, ObjectAPI, UnixFS protobuf metadata, IPLD links, and object options.

## Risks and Test Signals
This file directly guards against data-loss/corruption risks from dag-pb-level mutation of UnixFS files and HAMT shards. It also signals bypass semantics and link-create behavior.
