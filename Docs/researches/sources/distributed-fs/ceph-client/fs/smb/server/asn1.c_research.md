# sources/distributed-fs/ceph-client/fs/smb/server/asn1.c

Purpose: parses SPNEGO ASN.1/BER security blobs for SMB session setup and builds SPNEGO-wrapped NTLMSSP response blobs. It connects generated ASN.1 decoders to KSMBD connection authentication state.

Important APIs/types/functions: `ksmbd_decode_negTokenInit()` and `ksmbd_decode_negTokenTarg()` run generated `asn1_ber_decoder()` instances against client security blobs. `build_spnego_ntlmssp_neg_blob()` builds a negTokenTarg containing a negotiation result, NTLMSSP OID, and NTLMSSP challenge token. `build_spnego_ntlmssp_auth_blob()` builds the final authentication result token. Decoder callbacks include `ksmbd_gssapi_this_mech()`, `ksmbd_neg_token_init_mech_type()`, `ksmbd_neg_token_init_mech_token()`, and `ksmbd_neg_token_targ_resp_token()`.

Control flow: session setup passes the security blob to the appropriate decode function. The generated decoder calls back for the GSS mechanism OID, offered mechanism types, and embedded mech tokens. Valid OIDs update `conn->auth_mechs` and `conn->preferred_auth_mech`; token callbacks duplicate the mech token into `conn->mechToken`. Response construction computes ASN.1 header lengths, emits nested context-specific/sequence/octet-string fields, copies the NTLMSSP payload, and returns the allocated buffer and length to SMB2 session setup code.

State and persistence behavior: no stable state is kept. Runtime side effects are on `struct ksmbd_conn`: authentication mechanism bitmasks, preferred mechanism, `mechToken`, and `mechTokenLen`. Allocated response blobs are caller-owned. `conn->mechToken` is later freed by connection teardown.

Dependencies and integration points: depends on Linux ASN.1 BER decoder, OID registry, generated SPNEGO decoder headers, `connection.h`, `auth.h`, and KSMBD allocation/debug helpers. It integrates directly with NTLMSSP and Kerberos selection during SMB2 SESSION_SETUP.

Risks: length encoding is hand-built and must match BER definite-length rules; off-by-one errors produce security blobs that clients reject. Decoder callbacks must reject unexpected OIDs and zero-length tokens to avoid ambiguous authentication state. Repeated token allocation without prior cleanup would leak unless session setup code controls call ordering. Large token lengths can increase allocation pressure.

Test signals: NTLMSSP-over-SPNEGO negotiation, Kerberos-capable mechanism lists, unsupported OID rejection, malformed BER input, zero-length token rejection, client validation of challenge/final SPNEGO blobs, and leak checks on failed session setup.
