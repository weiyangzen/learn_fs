# sources/distributed-fs/ceph-client/fs/smb/client/smb1session.c

## Purpose
`smb1session.c` implements SMB1 `SESSION_SETUP_ANDX` authentication flows. It supports legacy NTLMv2, Kerberos/SPNEGO when upcalls are enabled, and raw NTLMSSP extended-security negotiate/authenticate sequences.

## Important APIs, types, and functions
The exported entry point is `CIFS_SessSetup`. Internal state is `struct sess_data`, which carries xid, session, server, NLS table, current auth-state function, result, request length, buffer type, and three kvecs. Important helpers include `cifs_ssetup_hdr`, unicode/ascii string encoders, unicode/ascii response decoders, `sess_alloc_buffer`, `sess_free_buffer`, `sess_establish_session`, `sess_sendreceive`, `sess_auth_ntlmv2`, `sess_auth_kerberos`, `_sess_auth_rawntlmssp_assemble_req`, `sess_auth_rawntlmssp_negotiate`, `sess_auth_rawntlmssp_authenticate`, and `select_sec`.

## Control flow
`CIFS_SessSetup` allocates `sess_data`, selects a security flow using shared `cifs_select_sectype`, and runs auth-state callbacks until no next callback remains. NTLMv2 builds a non-extended-security session setup with NTLMv2 response and account/domain/OS strings, sends it, validates word count, records UID, decodes server strings, and establishes the session. Kerberos obtains a SPNEGO key, sends the service ticket blob with extended security, validates the response blob length, decodes strings, and establishes the session. Raw NTLMSSP first sends a negotiate blob and expects `NT_STATUS_MORE_PROCESSING_REQUIRED`, decodes the challenge, then sends an authenticate blob using the challenge UID and establishes the session.

## State and persistence
Runtime state includes session UID (`Suid`), server OS/NOS/domain strings, server/session key material, auth response buffers, NTLMSSP state, session establishment flag, and SMB1 signing sequence number. Sensitive buffers are zeroed or freed with sensitive free helpers. No persistent storage is used.

## Dependencies and integration points
It depends on SMB1 PDU definitions, shared NTLMSSP blob builders/parsers from `sess.c`, NTLMv2 response setup, SPNEGO upcall keys, NLS conversion, SMB1 transport `SendReceive2`, and SMB1 signing/session state. It is registered as `smb1_operations.sess_setup`.

## Risks and test signals
Risks include BCC length and Unicode alignment errors, response word-count mismatches, security blob length overreads, stale UID across raw NTLMSSP phases, sensitive buffer lifetime mistakes, missing Kerberos support when upcalls are disabled, anonymous login edge cases, and session signing key setup failures. Test signals include NTLMv2, Kerberos, raw NTLMSSP two-step auth, guest and anonymous logins, Unicode and ASCII sessions, malformed word counts, malformed blob lengths, wrong SPNEGO upcall version, signing-required sessions, and cleanup after allocation/send failures.
