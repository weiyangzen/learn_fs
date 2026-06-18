# Research: sources/distributed-fs/ipfs-kubo/config/identity.go

Purpose: Stores and decodes the local node identity.

Important APIs/types/functions: Constants identify config selectors. `Identity` stores `PeerID` and base64 private key. `DecodePrivateKey(passphrase)` decodes the base64 key and unmarshals a libp2p private key.

Control flow, state, and persistence: Private keys are persisted unencrypted in the config. `passphrase` is unused. Decode returns libp2p crypto errors for bad base64 or invalid key bytes.

Dependencies and integration points: `CreateIdentity` in `init.go` populates this struct. Node construction uses it for libp2p identity.

Risks and test signals: Plaintext private key storage is explicitly noted as a security TODO. `init_test.go` verifies RSA and Ed25519 identities can be decoded.
