# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/block.go

## Purpose
Conformance tests for BlockAPI CID creation, retrieval, removal, stat, and pin-on-put behavior.

## Important APIs, Types, and Functions
Defines known CIDs, fixture readers `pbBlock`/`cborBlock`, and tests `TestBlock*` for put formats/codecs/hash, get, remove, stat, and pin.

## Control Flow and State
Tests create offline APIs, put fixture blocks with different options, compare exact CIDs, read data back, resolve paths, remove blocks with and without force, and inspect pin lists after `Block.Pin(true)`.

## Dependencies and Integration Points
Depends on BlockAPI, PinAPI, ResolvePath, multihash, IPLD not-found checks, and block options.

## Risks and Test Signals
Strong signals cover default raw CIDv1, legacy `Format` compatibility, custom hash/CID codec, not-found handling, force removal, stat sizes, and recursive pin creation. It does not cover concurrent remove or pinned block removal edge cases deeply.
