# sources/distributed-fs/ipfs-kubo/core/coreiface/idfmt.go

## Purpose
Formats IPNS key identifiers in a canonical CIDv1 base36 form.

## Important APIs, Types, and Functions
Provides `FormatKeyID(peer.ID) string` and `FormatKey(Key) string`.

## Control Flow and State
`FormatKeyID` converts a peer ID to a CID and encodes it with multibase base36, panicking only if base encoding unexpectedly fails. `FormatKey` delegates to `Key.ID`.

## Dependencies and Integration Points
Depends on libp2p peer IDs and multibase. Key and name APIs use this formatting for `/ipns/` paths and conformance tests validate base36 paths.

## Risks and Test Signals
Risks are canonical format drift and panic assumptions if upstream peer/CID conversion changes. Tests in key conformance verify generated/listed keys use `/ipns/` base36 CID strings.
