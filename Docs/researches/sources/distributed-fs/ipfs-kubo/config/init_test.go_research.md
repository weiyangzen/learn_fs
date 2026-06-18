# Research: sources/distributed-fs/ipfs-kubo/config/init_test.go

Purpose: Tests identity creation behavior.

Important APIs/types/functions: `TestCreateIdentity` generates Ed25519 and RSA identities and decodes the private key type. `TestCreateIdentityOptions` verifies Ed25519 rejects an explicit bit size.

Control flow, state, and persistence: Tests use an in-memory `bytes.Buffer` for progress output. They generate real keys but write no files.

Dependencies and integration points: Uses Kubo key generation options and libp2p crypto protobuf key types. Protects `Init`/identity setup compatibility with node construction.

Risks and test signals: Key generation can consume entropy and is slower than pure unit tests. Tests do not verify PeerID/public key matching beyond successful decode/type.
