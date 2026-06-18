<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/crypto_test.c -->
# sources/distributed-fs/ceph-client/net/mptcp/crypto_test.c

## Purpose
Provides KUnit coverage for MPTCP HMAC-SHA256 helper behavior using fixed protocol-shaped key and message vectors.

## Important APIs, Types, and Functions
`struct test_case` stores hex-like byte strings for key, message, and expected digest. `mptcp_crypto_test_basic()` converts test bytes through the same endian path used by MPTCP, invokes `mptcp_crypto_hmac_sha()`, renders the digest as hex, and compares with `KUNIT_EXPECT_STREQ()`. `mptcp_crypto_suite` registers the `mptcp-crypto` test suite.

## Control Flow
The test iterates each vector, splits the 16-byte key into two 64-bit values, splits the 8-byte message into two nonce words, writes the message in big-endian order, computes HMAC, converts the 32-byte digest to a 64-character hex string, and asserts equality.

## State and Persistence
The file owns static test vectors only. It does not mutate MPTCP runtime state.

## Dependencies and Integration Points
Depends on KUnit, `protocol.h`, and `mptcp_crypto_hmac_sha()` from `crypto.c`. It is built through `CONFIG_MPTCP_KUNIT_TEST`.

## Risks
The test covers HMAC only, not token/IDSN derivation. Vector strings are used as raw bytes rather than parsed hexadecimal, so future edits must preserve that convention. The comment typo "hmap" is harmless but indicates the code relies on matching crypto helper byte conversions.

## Test Signals
Running the `mptcp-crypto` KUnit suite should pass all vectors. Failures indicate changes in HMAC implementation, endian conversion, raw-key layout, or digest formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/crypto_test.c -->
