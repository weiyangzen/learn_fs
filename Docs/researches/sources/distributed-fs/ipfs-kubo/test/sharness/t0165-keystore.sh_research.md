## sources/distributed-fs/ipfs-kubo/test/sharness/t0165-keystore.sh

Purpose: comprehensive keystore command coverage for key generation, export/import formats, OpenSSL compatibility, protected self key operations, online behavior, and HTTP API restrictions.

Important APIs and helpers: defines `test_key_cmd`, private-key size checks, `test_key_import_export_all_formats`, `test_key_import_export`, `test_openssl_compatibility`, and `test_openssl_compatibility_all_types`. Uses `ipfs key gen/list/export/import/rm/rename`, `ipfs key rotate`, `curl`, OpenSSL fixture PEMs, and peer ID validation helpers.

Control flow and state: generates RSA and Ed25519 keys in b58mh/base36 IPNS bases, validates exported secret key sizes, round-trips PEM PKCS8 cleartext and libp2p protobuf formats, imports OpenSSL-generated keys, rejects unsupported key types unless `--allow-any-key-type`, verifies `-o` export, blocks export/import/remove/rename of `self`, checks list and long-list output, then starts a daemon to test online import/export compatibility, HTTP `key/export` 404, and disabled online key rotation.

Dependencies and integration points: covers keystore persistence, libp2p key encoding, PeerID bases, PEM/protobuf converters, API route exposure policy, and daemon keystore access.

Risks and test signals: protects secret key handling and self identity invariants. Signals include exact key IDs after import, sorted key lists, expected error text for protected operations, OpenSSL byte-for-byte round trips, and HTTP 404 for export.
