<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/asn1.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/asn1.c

Purpose: glue between the generated SPNEGO NegTokenInit ASN.1 decoder and CIFS session negotiation state. It validates the outer SPNEGO OID and records advertised security mechanisms on `TCP_Server_Info`.

Important APIs: `decode_negTokenInit()` invokes `asn1_ber_decoder()`. `cifs_gssapi_this_mech()` validates the top-level mechanism is `OID_spnego`. `cifs_neg_token_init_mech_type()` handles each advertised mechanism OID and sets `server->sec_mskerberos`, `sec_kerberosu2u`, `sec_kerberos`, `sec_ntlmssp`, or `sec_iakerb`.

Control flow: SMB session setup passes the security blob and server object to `decode_negTokenInit()`. Generated decoder callbacks parse OIDs. Unknown outer OID fails with `-EBADMSG`; unknown inner mechanism OIDs are logged but not fatal, allowing negotiation to continue if a supported mechanism is also present.

State and persistence: state changes are boolean capability flags in the in-memory `TCP_Server_Info`. There is no allocation or persisted data in this file.

Dependencies and integration: depends on `asn1_ber_decoder`, `oid_registry`, generated `cifs_spnego_negtokeninit.asn1.h`, CIFS debug macros, and SMB session negotiation code.

Risks: security mechanism selection depends on accurate OID mapping. Treating unsupported inner mechanisms as non-fatal is flexible but requires later code to reject sessions with no usable mechanism. Blob length and BER validity are delegated to the ASN.1 core.

Test signals: feed valid SPNEGO blobs with Kerberos, MS Kerberos, NTLMSSP, IAKERB, and mixed mechanisms; invalid top-level OID; truncated BER; unsupported mechanism-only blobs; and verify server flags used by session setup and SPNEGO upcall selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/asn1.c -->
