# sources/distributed-fs/ceph-client/lib/digsig.c

## Purpose
Implements legacy digital signature verification using RSA public keys stored in kernel keyrings and SHA-1 hashing.

## APIs, Types, and Functions
Exports `digsig_verify(struct key *keyring, const char *sig, int siglen, const char *data, int datalen)`. Internal helpers are `pkcs_1_v1_5_decode_emsa()` for decoding RSA PKCS#1 v1.5 EMSA padding and `digsig_verify_rsa()` for MPI-based RSA verification. It consumes `struct signature_hdr`, `struct pubkey_hdr`, user-key payloads, MPI values, and SHA-1 contexts.

## Control Flow
`digsig_verify()` validates the signature header, requires RSA, derives a hex key name from the big-endian key ID, searches the supplied keyring or requests a user key, hashes the data plus signature header with SHA-1, and calls `digsig_verify_rsa()` on the signature MPI payload. The RSA helper locks the key payload, validates public-key header version/algorithm/MPI count, reads modulus and exponent MPIs, computes `sig^e mod n`, left-pads the result to modulus length, decodes PKCS#1 v1.5 padding, compares the recovered digest with the computed hash, frees all MPIs/buffers, and releases the key semaphore.

## State and Persistence
The code does not persist verifier state. It reads key payload state under the key semaphore and allocates temporary MPI/output buffers per call. Key lifetime is managed by the keyring subsystem through `key_put()`.

## Dependencies and Integration Points
Depends on the key management subsystem, user-key payload format, MPI library, SHA-1 crypto implementation, endian helpers, and `linux/digsig.h` signature/public-key structures. It integrates with kernel consumers needing simple RSA signature verification against keyrings.

## Risks and Test Signals
Risks include SHA-1's weak collision resistance, strict support for only RSA and a legacy padding format, malformed MPI parsing, key revocation races, signature length edge cases, and leaking distinction between key lookup and verification failures. Test signals include valid/invalid RSA signature vectors, revoked or malformed user keys, wrong key ID, unsupported algorithm returns, padding corruption, and memory-failure tests through MPI/buffer allocation paths.
