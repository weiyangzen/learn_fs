# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_asn1.h

Purpose: declares minimal ASN.1/DER helpers for generic GSS token headers and defines generic GSS token parsing error constants adapted from upstream SunRPC/MIT Kerberos code.

Important APIs/types/functions: `g_OID_equal()` compares mechanism OIDs. `g_verify_token_header()` validates the application sequence tag, DER length, OID tag/length/value, and token body availability. `g_get_mech_oid()` extracts a copied mechanism OID from a token. `g_token_size()` calculates full token size for a mechanism OID and body length. `g_make_token_header()` writes the DER header and OID.

Control flow: mechanism code computes token size, writes headers before message-specific bytes, or verifies/extracts OIDs before processing received tokens. The implementation lives in `gss_generic_token.c`.

State/persistence: no state. Constants encode stable error values used internally by mechanism code.

Dependencies/integration: depends on `rawobj_t`, `memcmp()`, and the GSS generic token implementation. Kerberos and mechanism negotiation code use this layer for OID-tagged token handling.

Risks/test signals: the comments note an assumption that mechanism OIDs fit in one length byte. Tests should cover short tokens, bad sequence/OID tags, mismatched OIDs, malformed DER lengths, large body size calculations, and correct pointer advancement without modification on error.
