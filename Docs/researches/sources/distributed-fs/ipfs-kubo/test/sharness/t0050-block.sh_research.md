## sources/distributed-fs/ipfs-kubo/test/sharness/t0050-block.sh

Purpose: sharness coverage for `ipfs block put/get/stat/rm`, CID codec/hash options, pin safety, and block size limits.

Important control flow: creates blocks from stdin/files, validates put output and get bytes, stats block size, removes blocks, verifies pinned and indirectly pinned blocks cannot be removed, tests multi-block removal with invalid/valid inputs, `-f` and `-q` modes, deprecated `--format=protobuf`, `--cid-codec=dag-pb`, raw blocks with custom multihash type/length, conflict between legacy format and codec, empty stdin handling, sha3 with CIDv0 rejection, and oversized block rejection.

State and dependencies: mutates blockstore and pins; uses fixture protobuf data. Depends on `ipfs block`, `ipfs add`, `ipfs pin`, and exact CID/multihash behavior.

Risks: block command semantics are low-level and compatibility-sensitive. Test signals include exact command output, block presence/absence, pin-protection errors, no panic on empty stdin, and expected limit errors.
