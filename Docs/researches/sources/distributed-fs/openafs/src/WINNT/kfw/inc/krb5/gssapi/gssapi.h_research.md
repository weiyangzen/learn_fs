## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/gssapi/gssapi.h

Purpose: GSS-API C binding declarations used by Kerberos mechanisms for credential acquisition, security context establishment, MIC/wrap operations, name/OID management, and status reporting.

Important APIs/types/functions: Defines opaque `gss_name_t`, `gss_cred_id_t`, `gss_ctx_id_t`, `OM_uint32`, OID/buffer/channel-binding structs, context flag bits, credential usage constants, major status bit fields, `GSS_ERROR`, and static OID variables such as `GSS_C_NT_USER_NAME` and `GSS_C_NT_HOSTBASED_SERVICE`. Prototypes include `gss_acquire_cred`, `gss_init_sec_context`, `gss_accept_sec_context`, `gss_get_mic`, `gss_verify_mic`, `gss_wrap`, `gss_unwrap`, status/display/name import/release functions, OID-set helpers, context export/import, and V1 compatibility names `gss_sign`, `gss_seal`, `gss_unseal`.

Control flow: Initiators import a target name, acquire credentials, loop `gss_init_sec_context` tokens with an acceptor running `gss_accept_sec_context`, then protect messages with MIC/wrap APIs until context deletion.

State and persistence: Opaque credentials, names, contexts, buffers, and OID sets are implementation-owned handles. Callers must release returned buffers, names, credentials, OID sets, and contexts with matching GSS APIs. Exported contexts can be serialized for interprocess transfer.

Dependencies and integration points: Uses Kerberos calling-convention macros and Windows DLL import/export decoration. Integrated by `gssapi_generic.h`, `gssapi_krb5.h`, Kerberos-aware clients, and OpenAFS authentication glue.

Risks: Ownership rules are strict and easy to leak. Major status combines calling, routine, and supplementary bits, so tests must use masks. The header exposes deprecated OIDs and V1 entrypoints for compatibility. Channel-binding/address constants must match peer expectations.

Test signals: GSS init/accept loop, name import/export/canonicalization, wrap/MIC round trips, major/minor status display, context export/import, OID-set creation/release, and Windows DLL import linkage.
