# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/key.go

## Purpose
Conformance tests for KeyAPI generation, listing, renaming, removal, signing, and verification.

## Important APIs, Types, and Functions
Includes `TestKey`, `verifyIPNSPath`, and tests for self handling, generate size/type/existing, list, rename variants, remove, sign, and verify across key encodings.

## Control Flow and State
Tests create APIs, inspect the default `self` key, generate named keys, validate `/ipns/` base36 CID paths, enforce self immutability, exercise force/no-force rename overwrite paths, remove keys, sign with domain-separated libp2p key data, and verify signatures by name, empty self selector, base58 PeerID, CIDv1 PeerID, IPNS name, and prefixed IPNS path.

## Dependencies and Integration Points
Depends on KeyAPI, key options, libp2p peer/IPNS formatting, multibase, and testify.

## Risks and Test Signals
Signals are broad for keystore semantics and signature compatibility. The Ed25519 generate-type path is skipped for a linked upstream issue, so supported key algorithm validation still needs implementation-specific coverage.
