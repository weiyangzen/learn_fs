# sources/distributed-fs/ipfs-kubo/core/coreapi/key.go

Purpose: implements CoreAPI key management plus signing and verification over Kubo/libp2p keys.

Important APIs/types/functions: `KeyAPI`, private `key` implementation, `newKey`, methods `Generate`, `List`, `Rename`, `Remove`, `Self`, `Sign`, and `Verify`, and `signedMessagePrefix`.

Control flow: generation rejects `self`, checks for existing key, creates RSA or Ed25519 private/public keys, stores private key in repo keystore, derives peer ID, and returns an IPNS key object. Listing includes `self` first, sorts keystore names, skips unreadable/bad keys with logs. Rename rejects `self`, fetches old key, optionally deletes destination when forced, writes new key, then deletes old. Remove rejects `self`, derives removed peer ID, deletes key, and returns key info. Sign chooses self or keystore key, prefixes data with a domain string, and signs. Verify accepts self, keystore name, IPNS name, or PeerID with embedded public key, prefixes data the same way, and verifies.

State and persistence behavior: `Generate`, `Rename`, and `Remove` mutate repo keystore. `Sign` and `Verify` are read-only. No explicit keystore sync is visible here; durability is delegated to the keystore implementation.

Dependencies and integration points: used by name publishing and CLI key commands. Integrates repo keystore, libp2p crypto/peer IDs, IPNS name paths, CoreAPI options, and tracing.

Risks: rename is not atomic: after writing new key, delete old can fail, leaving duplicates. Force rename deletes destination before writing old key, so a later write failure can lose destination. Verify by PeerID only works when the public key can be extracted from the peer ID.

Test signals: covered through CoreAPI interface tests; no file-local unit tests.
