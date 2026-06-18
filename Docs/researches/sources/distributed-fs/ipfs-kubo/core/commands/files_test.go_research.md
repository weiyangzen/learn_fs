<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/files_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/files_test.go

## Purpose

Tests that `ipfs files cp` rejects a copied DAG root that is not valid UnixFS.

## Important APIs, Types, and Functions

`TestFilesCp_DagCborNodeFails` constructs a mock command context and node, creates a protobuf DAG node with invalid UnixFS data, adds it to the DAG, and runs `filesCpCmd.Run`.

## Control Flow

The test builds a request copying `/ipfs/<cid>` to `/test-destination`, creates a writer response emitter, invokes the command with the mock context, and asserts the returned error contains the UnixFS validation message.

## State and Persistence Behavior

Uses an in-memory/mock node DAG. It writes a test node to the mock DAG but does not persist repo state.

## Dependencies and Integration Points

Depends on `core/mock`, boxo merkledag, command response emitters, and the `filesCpCmd` UnixFS validation path.

## Risks and Edge Cases

The test targets invalid dag-pb data, not every invalid codec path. It does not test valid raw or valid dag-pb copies, force behavior, or parent creation.

## Test Signals

Strong signal for the security/validity guard introduced around lazy MFS copy. Limited signal for broader MFS command behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/files_test.go -->
