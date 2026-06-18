# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_mech.c

## Purpose
`gss_krb5_mech.c` registers the Kerberos 5 GSS mechanism with SUNRPC, defines supported enctypes, imports Kerberos contexts from gssd, derives per-direction keys, dispatches MIC/wrap/unwrap operations to enctype implementations, and advertises krb5/krb5i/krb5p pseudoflavors.

## Important APIs, Types, and Functions
The central data is `supported_gss_krb5_enctypes[]`, conditionally compiled for AES-SHA1, Camellia-CMAC, and AES-SHA2. `gss_krb5_prepare_enctype_priority_list()` builds the comma-separated enctype list sent in gssd upcalls. `gss_krb5_lookup_enctype()` returns descriptor metadata. Crypto allocation helpers create keyed skcipher and ahash transforms. `gss_krb5_import_ctx_v2()` derives initiator/acceptor encryption, signing, and integrity keys. `gss_import_v2_context()` parses flags, expiration, sequence, enctype, and session key from the imported context. `gss_krb5_get_mic()`, `gss_krb5_verify_mic()`, `gss_krb5_wrap()`, and `gss_krb5_unwrap()` are `gss_api_ops` dispatchers.

## Control Flow
Module init prepares the enctype priority string and calls `gss_mech_register()`. During context import, the GSS switch allocates a `gss_ctx` and calls `gss_krb5_import_sec_context()`. This parses the v2 context token, rejects unsupported enctypes, stores the Kerberos OID in `mech_used`, derives six transforms for initiator/acceptor seal, sign, and integrity use, and publishes the `krb5_ctx` into the generic GSS context. Per-message operations then select the descriptor function pointers.

## State and Persistence
Persistent mechanism state includes `gss_kerberos_mech`, its pseudoflavor descriptors, and the enctype priority string. Per-context state lives in `krb5_ctx` with transform pointers, sequence counters, and end time. Delete frees all transforms, mechanism OID storage, and the context.

## Dependencies and Integration Points
This file depends on Kconfig-selected crypto algorithms, public SUNRPC GSS definitions, `gss_mech_switch.c`, key derivation and crypto helpers, KUnit visibility exports, and module autoload aliases for names, pseudoflavors, and OID. It maps `RPC_AUTH_GSS_KRB5`, `RPC_AUTH_GSS_KRB5I`, and `RPC_AUTH_GSS_KRB5P` to none, integrity, and privacy services.

## Risks and Edge Cases
Context import rejects trailing bytes, unsupported enctypes, sequence overflow into the 32-bit compatibility field, allocation failures, and crypto transform setup failures. The enctype priority string is fixed at 64 bytes; new enctypes could be silently omitted if the string grows too large. Direction-specific key selection is security-sensitive: initiator and acceptor transforms are deliberately separate.

## Test Signals
KUnit exercises `gss_krb5_lookup_enctype()` and all KDF/crypto behavior behind the descriptors. Runtime tests should verify module autoload aliases, gssd enctype negotiation, and each pseudoflavor service.
