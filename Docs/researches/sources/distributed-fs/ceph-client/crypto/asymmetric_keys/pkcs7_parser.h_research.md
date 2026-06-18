# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_parser.h

Purpose: defines internal PKCS#7 parser and verifier structures shared by parsing, signature verification, and trust validation.

Important APIs/types/functions: `struct pkcs7_signed_info` stores signer certificate pointer, index, unsupported/blacklisted flags, authenticated attribute state, signing time, message digest attribute, authattrs byte range, and `struct public_key_signature`. `struct pkcs7_message` stores certificate/CRL lists, signed-info list, version, authattrs flags, content type, content length/header length, and content pointer. Debug macros `kenter` and `kleave` wrap `pr_devel()`.

Control flow: parser code fills these structures, verifier code resolves `signer`, computes digests, and trust code walks signer chains using `seen` and `verified` fields in linked X.509 certificates.

State and persistence: all state is per parsed message and freed by `pkcs7_free_message()`. Pointers to content and authenticated attributes often reference the original PKCS#7 buffer, so caller lifetime matters.

Dependencies and integration points: includes OID registry, public PKCS#7 API declarations, and `x509_parser.h`. Used by `pkcs7_parser.c`, `pkcs7_verify.c`, and `pkcs7_trust.c`.

Risks: structure field semantics are shared across files; changing ownership of `sig->m`, `authattrs`, or `data` can cause use-after-free or double-free. Bit indexes for `aa_set` must remain synchronized with parser checks.

Test signals: compile coverage of all PKCS#7 files, multi-signer verification, detached data lifetime tests, and authattrs parsing/verification tests.
