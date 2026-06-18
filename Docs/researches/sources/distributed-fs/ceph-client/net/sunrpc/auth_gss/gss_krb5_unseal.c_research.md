# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_unseal.c

## Purpose
`gss_krb5_unseal.c` verifies Kerberos v2 MIC tokens. It validates token structure, direction flags, checksum bytes, and context expiration for messages protected by RPCSEC_GSS integrity/verifier operations.

## Important APIs, Types, and Functions
The only function is `gss_krb5_verify_mic_v2()`. It selects the opposite-direction signing transform (`acceptor_sign` for initiators verifying server tokens, `initiator_sign` for acceptors), constructs a temporary checksum buffer, validates the `KG2_TOK_MIC` token ID, verifies flags and filler bytes, computes `gss_krb5_checksum()`, compares the expected checksum with the token checksum, and returns GSS major status.

## Control Flow
Generic RPC verifier validation calls into the GSS switch, then the Kerberos mechanism dispatches to this descriptor callback. The function checks token syntax before doing crypto. It intentionally does not validate the sequence number in the token; RPCSEC_GSS handles sequence validation outside the Kerberos MIC token per comments referencing RFC 2203.

## State and Persistence
No persistent state is mutated. The context's role and end time are read. A stack checksum buffer of `GSS_KRB5_MAX_CKSUM_LEN` is used.

## Dependencies and Integration Points
It depends on Kerberos token constants, `gss_krb5_checksum()`, kernel time, and sign transforms derived by context import. It is the counterpart to `gss_krb5_get_mic_v2()` in `gss_krb5_seal.c`.

## Risks and Edge Cases
Malformed token IDs, unexpected sealed flag, wrong direction bit, non-0xff filler bytes, checksum mismatch, and expired contexts return distinct GSS major statuses. The checksum comparison uses `memcmp()` on local and received checksum bytes; higher-level code maps failures to access errors. The sequence number is deliberately skipped, so sequence validation must remain correct in callers.

## Test Signals
No direct KUnit suite covers full MIC token verification. Indirect signals are checksum tests and integration tests that validate reply verifiers and integrity service responses.
