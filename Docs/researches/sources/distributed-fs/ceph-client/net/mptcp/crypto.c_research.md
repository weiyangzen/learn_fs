<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/crypto.c -->
# sources/distributed-fs/ceph-client/net/mptcp/crypto.c

## Purpose
Implements MPTCP cryptographic primitives for deriving tokens/IDSNs from keys and computing HMAC-SHA256 authentication values used by MPTCP options.

## Important APIs, Types, and Functions
`mptcp_crypto_key_sha()` SHA256-hashes a 64-bit key in network byte order and returns the token from the first digest word and the IDSN from the final digest bytes. `mptcp_crypto_hmac_sha()` computes HMAC-SHA256 using two 64-bit keys as the raw 16-byte key. `mptcp_crypto_hmac_sha()` is exported when the KUnit crypto test is modular.

## Control Flow
Both functions are straight-line wrappers over crypto library helpers. They explicitly convert keys to big endian before hashing to match protocol wire format and use unaligned/big-endian reads from the digest for protocol outputs.

## State and Persistence
No persistent state is stored. Outputs are deterministic for input keys/messages and are consumed by token lookup, MP_JOIN validation, and ADD_ADDR HMAC validation.

## Dependencies and Integration Points
Depends on `crypto/sha2.h`, `CRYPTO_LIB_SHA256`, and `CRYPTO_LIB_UTILS`. Integrated by option parsing/writing, token handling, path manager ADD_ADDR HMAC generation, and KUnit tests.

## Risks
Endianness is the primary correctness risk: protocol-visible tokens, IDSNs, and HMACs depend on big-endian key/message layout. The raw-key HMAC API assumes a fixed 16-byte key made from key1/key2. Test modules require the conditional export.

## Test Signals
KUnit vectors in `crypto_test.c`, MP_CAPABLE token/IDSN interop, MP_JOIN HMAC validation, ADD_ADDR HMAC acceptance/rejection, and cross-endian build testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/crypto.c -->
