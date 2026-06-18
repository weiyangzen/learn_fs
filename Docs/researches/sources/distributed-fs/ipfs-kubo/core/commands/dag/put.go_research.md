<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/put.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dag/put.go

## Purpose

Implements `ipfs dag put`, decoding input IPLD data, re-encoding it with a storage codec, hashing it, adding it to the DAG service, and optionally pinning it.

## Important APIs, Types, and Functions

`dagPut` is the handler. Important options are `input-codec`, `store-codec`, `hash`, `pin`, and `allow-big-block`. It uses IPLD prime multicodec lookup, `cid.Prefix`, `blocks.NewBlockWithCid`, and `ipldlegacy.LegacyNode`.

## Control Flow

The handler gets CoreAPI and node config, chooses default hash from import config, parses multicodec codes, builds a CID prefix, looks up decoder and encoder, chooses a pinning or non-pinning DAG adder, and creates a batch. For each input file it decodes to an IPLD node, encodes storage bytes, computes the CID, constructs a legacy node, checks block size, adds it to the batch, and emits the CID. Finally it commits the batch.

## State and Persistence Behavior

Writes new DAG blocks and optionally pins them when `--pin` is set. Batch commit persists the additions.

## Dependencies and Integration Points

Uses CoreAPI DAG service, node repo import config, IPLD prime codecs, legacy node wrapper, command file iterators, and shared block-size safety.

## Risks and Edge Cases

Unsupported codecs or hashes fail before import. Batch add/commit errors can occur after some emitted CIDs, so clients should treat command failure as potentially partial. Oversized blocks are rejected unless explicitly allowed.

## Test Signals

No direct tests. Good tests include codec combinations, hash defaults, pinning path, multiple files, malformed input, and `--allow-big-block`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/put.go -->
