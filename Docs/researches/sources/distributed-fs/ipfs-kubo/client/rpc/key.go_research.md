# sources/distributed-fs/ipfs-kubo/client/rpc/key.go

## Purpose
This file implements key management, signing, and verification over the HTTP API.

## Important APIs, Types, And Functions
`KeyAPI` wraps `HttpApi`. `key` implements `iface.Key` with `Name`, `Path`, and `ID`. Methods include `Generate`, `Rename`, `List`, `Self`, `Remove`, `Sign`, and `Verify`.

## Control Flow
RPC responses with name and peer ID are converted by `newKey` into peer IDs and `/ipns/<name>` paths. Signing uploads data to `key/sign` and decodes the returned multibase signature. Verification sends key/name, multibase signature, and data to `key/verify`.

## State And Persistence Behavior
Generate, rename, remove, sign, and verify act on remote key material; signing/verification read private/public key state through the daemon. Client state is transient.

## Dependencies And Integration Points
It integrates Kubo key commands, IPNS name derivation, peer ID decoding, coreiface key options, and shared multibase encoding.

## Risks And Test Signals
Risks include unexpected key count on remove, malformed peer IDs, and signature multibase compatibility. Signals are CoreAPI key tests for lifecycle and signature validity.
