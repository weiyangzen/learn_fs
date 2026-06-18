# sources/distributed-fs/ipfs-kubo/core/coreunix/metadata_test.go

## Purpose
Tests UnixFS metadata wrapping and retrieval.

## Important APIs, Types, and Functions
Defines helper `getDagserv` and `TestMetadata`.

## Control Flow and State
The test builds an in-memory DAG service, imports random data into a UnixFS DAG, wraps it with metadata, reads metadata back, loads the wrapper node, creates a DAG reader, and verifies the original bytes are still readable through the wrapper.

## Dependencies and Integration Points
Depends on blockservice, merkledag, UnixFS importer/io, offline exchange, blockstore, datastore, random data, and a minimal `IpfsNode{DAG: ds}`.

## Risks and Test Signals
Signals include metadata serialization, dag-pb wrapper shape, and content readability through the `file` link. It does not test malformed metadata, non-protobuf nodes, or missing target CIDs.
