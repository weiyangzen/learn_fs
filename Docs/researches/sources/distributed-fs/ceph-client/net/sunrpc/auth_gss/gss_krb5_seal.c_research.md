# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_seal.c

## Purpose
`gss_krb5_seal.c` implements Kerberos v2 MIC token generation for RPCSEC_GSS. It constructs RFC 4121-style MIC headers, attaches a 64-bit sequence number, computes the keyed checksum, and reports context expiration.

## Important APIs, Types, and Functions
`setup_token_v2()` writes the MIC token header into a caller-provided `xdr_netobj`, setting flags for acceptor-sent direction and acceptor subkey use and reserving checksum space. `gss_krb5_get_mic_v2()` chooses `initiator_sign` or `acceptor_sign` based on `ctx->initiate`, writes the sequence number with `atomic64_fetch_inc(&ctx->seq_send64)`, computes `gss_krb5_checksum()`, and returns a GSS major status.

## Control Flow
The generic GSS switch calls `gss_get_mic()`, the Kerberos mechanism dispatches to the descriptor's `get_mic`, and this file fills the token. The checksum covers the message body and token header according to the crypto helper's RFC 4121 order. After checksum calculation, current wall-clock time is compared with `ctx->endtime`.

## State and Persistence
The only persistent mutation is incrementing the Kerberos 64-bit send sequence counter. The token buffer is caller-owned and updated in place. The context's flags and end time are read but not changed.

## Dependencies and Integration Points
It depends on Kerberos token constants, `gss_krb5_checksum()`, kernel time, atomics, and the per-context sign transforms created in `gss_krb5_mech.c`. It is used by RPCSEC_GSS verifier and integrity MIC generation.

## Risks and Edge Cases
Direction flags must match the receiver's expectations or unseal will reject the token. The checksum buffer must have enough room for `GSS_KRB5_TOK_HDR_LEN + cksumlength`; this is arranged by higher-level auth slack. Context expiration is reported after checksum generation, so callers may still have a valid token while needing credential renewal.

## Test Signals
There is no direct KUnit test for the token wrapper here, but checksum primitives and key derivation are covered. Integration tests should validate verifier generation and acceptance for initiator and acceptor roles.
