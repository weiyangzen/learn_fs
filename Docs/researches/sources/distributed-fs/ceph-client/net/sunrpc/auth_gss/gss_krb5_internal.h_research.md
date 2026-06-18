# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_internal.h

## Purpose
This header defines Kerberos 5 RPCSEC_GSS internal data structures, enctype descriptors, context fields, and cross-file function prototypes. It is the contract between the Kerberos mechanism adapter, key derivation, crypto, seal/unseal, and wrap/unwrap files.

## Important APIs, Types, and Functions
`struct gss_krb5_enctype` describes an encryption type: numeric enctype/checksum type, crypto transform names, checksum and key lengths, key-derivation callback, and per-message callbacks. `struct krb5_ctx` stores direction, flags, selected enctype, crypto transforms, derived session and subkeys, sequence counters, end time, and mechanism OID. Important prototypes include MIC functions, wrap/unwrap functions, KDFs (`krb5_derive_key_v2()`, `krb5_kdf_hmac_sha2()`, `krb5_kdf_feedback_cmac()`), `krb5_derive_key()` inline label construction, crypto helpers, AES/EtM encrypt/decrypt, `krb5_nfold()`, and `gss_krb5_lookup_enctype()`.

## Control Flow
The import path fills a `krb5_ctx`, locates an enctype descriptor, derives keys through the descriptor's `derive_key`, allocates transforms, and then uses the descriptor's per-message callbacks for MIC and wrap operations. The inline `krb5_derive_key()` builds the 5-byte key usage label from a 32-bit usage and one-byte seed, then delegates to the enctype KDF.

## State and Persistence
`krb5_ctx` is the persistent security context used after gssd imports a context. It holds crypto transform pointers that must be freed on context deletion, sequence counters that advance per message, and `endtime` for expiration checks. `Ksess` and derived key buffers are sensitive and should be cleared or freed carefully by implementation files.

## Dependencies and Integration Points
The header depends on public Kerberos/SUNRPC definitions, XDR netobjects, crypto transform types, GSS token constants, and page-backed XDR buffers. It integrates the `gss_api_ops` mechanism adapter with lower-level crypto and KUnit-visible test hooks.

## Risks and Edge Cases
Because the descriptor table controls algorithms, key lengths, and function pointers, mismatched lengths or wrong transform names can break interoperability or weaken security. The 32-bit `seq_send` compatibility field must not overflow when importing a 64-bit sequence value for older enctypes. `krb5_derive_key()` assumes `GSS_KRB5_K5CLENGTH` is at least 5 bytes.

## Test Signals
Many prototypes are marked visible/exported under KUnit. `gss_krb5_test.c` exercises descriptor lookup, n-fold, KDFs, checksums, CBC-CTS, EtM checksum, and encryption round trips, with skips when a compiled enctype is unavailable.
