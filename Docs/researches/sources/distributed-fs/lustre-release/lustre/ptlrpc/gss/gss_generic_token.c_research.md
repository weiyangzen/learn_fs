# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_generic_token.c

Purpose: implements minimal DER/ASN.1 token header construction and verification for GSS tokens carrying mechanism OIDs.

Important APIs/types/functions: private helpers `der_length_size()`, `der_write_length()`, and `der_read_length()` handle definite-form DER lengths. `g_token_size()` computes sequence-tag plus length plus OID plus body size. `g_make_token_header()` writes application tag `0x60`, sequence length, OID tag `0x06`, OID length, and OID bytes. `g_verify_token_header()` validates the token header and leaves the caller's buffer pointer and body size advanced only on success. `g_get_mech_oid()` extracts and allocates a copy of the OID from an input token.

Control flow: token creation sizes the final buffer, writes the generic header, and leaves mechanism-specific code to append token type and body. Verification rejects short buffers, wrong tags, invalid DER lengths, sequence-length mismatches, wrong OIDs, and insufficient two-byte inner token type space.

State/persistence: allocates only the OID copy in `g_get_mech_oid()`; no persistent state.

Dependencies/integration: uses `gss_asn1.h`, `gss_err.h`, raw object allocation, and is used by GSS mechanism negotiation paths that need OID-tagged tokens.

Risks/test signals: integer overflow is noted but not fully guarded in token size calculation. OID length is assumed to fit one byte. Tests should cover all malformed-token branches, multi-byte DER lengths, OID mismatch versus structurally bad token precedence, correct output pointer/body size on success, and cleanup of allocated OID data.
