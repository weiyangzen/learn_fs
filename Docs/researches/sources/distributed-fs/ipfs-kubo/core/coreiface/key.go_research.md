# sources/distributed-fs/ipfs-kubo/core/coreiface/key.go

## Purpose
Defines CoreAPI keystore and key identity operations.

## Important APIs, Types, and Functions
Declares `Key` with `Name`, `Path`, and `ID`, and `KeyAPI` with `Generate`, `Rename`, `List`, `Self`, `Remove`, `Sign`, and `Verify`.

## Control Flow and State
No implementation flow is in this file. The contract controls persistent keystore entries, the immutable self key, signing with named keys, and verification by key name or encoded key identity.

## Dependencies and Integration Points
Depends on context, Boxo path, key options, and libp2p peer IDs. It integrates with IPNS names and is tested by key conformance tests.

## Risks and Test Signals
Risks include accidental mutation of `self`, overwrite semantics, signature domain separation, and accepting multiple key formats during verify. Tests cover generate/list/rename/remove restrictions, overwrite force behavior, signing, and verification across PeerID/CID/IPNS path encodings.
