<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/blowfish_generic.c -->
# sources/distributed-fs/ceph-client/crypto/blowfish_generic.c

## Purpose

`blowfish_generic.c` registers the generic single-block Blowfish cipher implementation with the Crypto API. It supplies block encrypt/decrypt functions and reuses `blowfish_setkey()` from the common module.

## Important APIs, Types, and Flow

`bf_encrypt()` and `bf_decrypt()` read a 64-bit block as big-endian halves, run the unrolled Blowfish Feistel rounds using the P-box and S-box data stored in `struct bf_ctx`, then write big-endian output. Encryption applies rounds 0 through 15 and post-whitening P[16]/P[17]. Decryption applies the P-array in reverse order and finishes with P[1]/P[0].

The registered `crypto_alg` is named `blowfish` with driver `blowfish-generic`, type `CRYPTO_ALG_TYPE_CIPHER`, block size `BF_BLOCK_SIZE`, context size `sizeof(struct bf_ctx)`, and key bounds from `BF_MIN_KEY_SIZE` to `BF_MAX_KEY_SIZE`.

## State, Dependencies, and Integration

Persistent state is the Blowfish expanded key in the transform context. The file depends on unaligned big-endian accessors, `crypto/algapi.h`, and `crypto/blowfish.h`. It integrates with modes/templates such as CBC, ECB, CMAC, or other cipher users that request `blowfish` or `blowfish-generic`.

## Risks and Test Signals

Risks are byte-order correctness, round-order correctness, and module dependency on the exported common key setup. Tests should use known-answer vectors for encryption/decryption, mode-level round trips, invalid key lengths through Crypto API setkey, and generic-versus-accelerated equivalence where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/blowfish_generic.c -->
