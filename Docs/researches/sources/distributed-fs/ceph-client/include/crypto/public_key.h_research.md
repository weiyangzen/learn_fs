# sources/distributed-fs/ceph-client/include/crypto/public_key.h

Purpose: declares the kernel public-key subtype, signature container, keyring restriction policies, query API, and signature verification entry points.

Important APIs, types, and flow: `struct public_key` stores key payload, length, algorithm IDs, key identifier, and extension flags for CA/digital signature/key-cert-sign use. `struct public_key_signature` stores signature bytes, digest bytes, encoding, hash algorithm, public-key algorithm, and key IDs. Free helpers release both structures. Restriction functions gate keyring links by signatures, trusted keys/keyrings, CA flags, or digital-signature usage. `query_asymmetric_key()`, `verify_signature()`, and `public_key_verify_signature()` drive verification; a stub returns `-ENOPKG` when public-key crypto is disabled.

State and persistence: keys may be persisted in kernel keyrings; structures here represent allocated runtime payloads. Signature and digest buffers are owned by parsed data until freed.

Dependencies and integration: integrates with asymmetric key subtype, kernel keyrings, PKCS#7/X.509 parsers, and crypto signature/akcipher implementations.

Risks and test signals: risks include key usage flag enforcement, trust-chain bypass, algorithm-name mismatches, and optional Kconfig stubs. Signals include keyring restriction tests, X.509/PKCS#7 verification, invalid digest/signature tests, disabled-public-key Kconfig builds, and CA/digitalSignature extension policy tests.
