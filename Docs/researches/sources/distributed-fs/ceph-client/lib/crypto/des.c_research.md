# sources/distributed-fs/ceph-client/lib/crypto/des.c

## Purpose
Generic DES and Triple DES EDE block cipher implementation for the kernel crypto API.

## Important APIs, Types, And Functions
Exports `des_expand_key()`, `des_encrypt()`, `des_decrypt()`, `des3_ede_expand_key()`, `des3_ede_encrypt()`, and `des3_ede_decrypt()`. Internal pieces include permutation tables `pc1`, `rs`, `pc2`, S-box tables `S1` through `S8`, key schedule helpers `des_ekey()` and `dkey()`, and round/permutation macros `IP`, `FP`, and `ROUND`.

## Control Flow
DES key expansion validates key length, builds 16 round subkeys using PC1/PC2 lookup tables and rotations, and rejects weak keys by returning `-ENOKEY`. Encryption/decryption load a 64-bit block little-endian, apply initial permutation, run 16 Feistel rounds with subkeys forward or reverse, apply final permutation, and store output. 3DES verifies keying material, builds encrypt/decrypt/encrypt schedules for three keys, and runs three DES phases in EDE order for encryption or reverse order for decryption.

## State, Persistence, And Dependencies
Expanded keys are stored in caller-owned `des_ctx` or `des3_ede_ctx`. No runtime global state exists; tables are static read-only. It depends on internal DES verification helpers, unaligned accessors, and Linux crypto error codes.

## Integration Points
Used by legacy cipher registrations and compatibility paths. FIPS mode may reject DES/3DES use elsewhere, but this file provides the primitives and weak-key handling.

## Risks
DES is cryptographically obsolete and 3DES is legacy with small block-size risks. Table lookups are key/data dependent and not designed as a modern constant-time side-channel-resistant implementation. Weak-key and keying-option handling must align with `des3_ede_verify_key()`.

## Test Signals
NIST DES/3DES known-answer vectors, weak-key rejection, invalid key length errors, encrypt-decrypt round trips, and keying-option tests for 3DES are required.
