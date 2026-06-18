# sources/distributed-fs/ipfs-kubo/core/coreunix/metadata.go

## Purpose
Adds and reads UnixFS metadata wrapper nodes around existing DAG content.

## Important APIs, Types, and Functions
Exports `AddMetadataTo` and `Metadata`.

## Control Flow and State
`AddMetadataTo` decodes a CID string, loads the target DAG node, serializes UnixFS metadata, creates a new dag-pb node with metadata data and a `file` link to the target, adds it to the DAG, and returns the wrapper CID string. `Metadata` decodes and loads a CID, requires a dag-pb node, and parses metadata bytes from its data.

## Dependencies and Integration Points
Depends on Kubo core node DAG service, Boxo merkledag and UnixFS metadata, and CIDs. It supports legacy metadata wrapping around UnixFS file data.

## Risks and Test Signals
Risks include assuming the loaded metadata node is dag-pb, invalid metadata bytes, and hardcoded `file` link semantics. Tests verify adding metadata and reading the original file through the wrapper.
