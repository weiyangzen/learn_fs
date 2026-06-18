## sources/cloud-native/buildkit/util/pgpsign/pgpsign.go

Purpose: OpenPGP signature parsing and verification helpers with BuildKit policy checks for hashes, key algorithms, key expiry/revocation, RSA size, and precomputed digest verification.

Important APIs/types: `VerifyPolicy{RejectExpiredKeys}`, `ParseArmoredDetachedSignature`, `ReadAllArmoredKeyRings`, `VerifyArmoredDetachedSignature`, `VerifySignatureWithDigest`. Internal helpers map signature hash to OCI digest algorithm and validate entities/signature times.

Control flow: signature parsing decodes armor and returns the first packet signature. keyring reading accepts concatenated public or private armored key blocks. Detached verification parses signature/keyring, rejects weak hash and unsupported public-key algorithms, optionally sets OpenPGP verification time to signature creation time when expired keys are allowed, runs `openpgp.CheckDetachedSignature`, then validates signer usability, revocation, RSA length, and future creation time. Digest verification constructs a `staticHash` with precomputed sum and tries primary/subkeys.

State/persistence: stateless, operates on in-memory key/signature data and signed streams. Dependencies: ProtonMail OpenPGP, OCI digest, crypto hash/RSA.

Integration points: called by Git signature verification and provenance/trust features. Risks: accepts private key blocks as keyrings; policy defaults allow expired keys by verifying at signature creation time; only SHA-256/384/512 and selected pubkey algos are accepted; `staticHash.Write` discards bytes by design for prehashed verification. Test signals: no local tests in this subset, but `gitobject` and `gitsign` rely on this behavior.
