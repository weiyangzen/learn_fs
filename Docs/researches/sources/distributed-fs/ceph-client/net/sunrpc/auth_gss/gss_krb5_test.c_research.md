# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_test.c

## Purpose
`gss_krb5_test.c` is a KUnit test module for the RPCSEC_GSS Kerberos 5 implementation. It validates key derivation, checksum, CBC-CTS encryption, encrypt-then-MAC checksums, and encrypt/decrypt round trips against RFC test vectors and internal self-tests.

## Important APIs, Types, and Functions
`struct gss_krb5_test_param` carries parameterized test data: descriptor, enctype, fold length, constants, keys, usage labels, plaintext, confounder, expected ciphertext/HMAC, and next IV. Shared test helpers are `kdf_case()`, `checksum_case()`, `rfc3961_nfold_case()`, `rfc3962_encrypt_case()`, `rfc6803_encrypt_case()`, `rfc8009_encrypt_case()`, and `encrypt_selftest_case()`. Macros `DEFINE_HEX_XDR_NETOBJ` and `DEFINE_STR_XDR_NETOBJ` create static XDR netobjects for vectors. KUnit suites are registered for RFC 3961, RFC 3962, RFC 6803, RFC 8009, and generic encryption self-tests.

## Control Flow
Each parameterized case looks up the enctype with `gss_krb5_lookup_enctype()` and skips when the algorithm is unavailable under the current config. KDF and checksum tests derive keys through the descriptor and compare exact bytes. Encryption tests allocate crypto transforms, build an `xdr_buf` over KUnit memory, call CBC-CTS helpers and checksum helpers, and compare ciphertext, HMAC, IV, or plaintext after decrypt.

## State and Persistence
The module owns static immutable test vectors. Runtime allocations are KUnit-scoped where possible; crypto transforms are manually freed. It imports symbols from the `EXPORTED_FOR_KUNIT_TESTING` namespace.

## Dependencies and Integration Points
It depends on KUnit, the kernel crypto API, XDR buffers, Kerberos internal headers, and Kconfig-selected enctypes. It integrates with the Makefile through `CONFIG_RPCSEC_GSS_KRB5_KUNIT_TEST`.

## Risks and Edge Cases
Because tests skip unavailable enctypes, a green run does not imply every possible enctype was compiled. The vectors mainly test primitive behavior and do not fully exercise RPCSEC_GSS token framing, rpc_pipefs upcalls, credential cache behavior, or request retransmission. Some string vectors note possible platform encoding assumptions, though the kernel normally uses ASCII-compatible bytes.

## Test Signals
This file is itself the primary test signal. It covers RFC 3961 n-fold, RFC 3962 AES CBC-CTS encryption and IV behavior, RFC 6803 Camellia KDF/checksum/encryption, RFC 8009 AES-SHA2 KDF/checksum/encryption, and encrypt/decrypt round trips for each compiled enctype.
