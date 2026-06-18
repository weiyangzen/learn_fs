# sources/distributed-fs/ceph-client/fs/smb/server/auth.h

Purpose: declares authentication, signing, key-derivation, and encryption helpers for the KSMBD server and centralizes authentication-related constants.

Important APIs/types/functions: defines `AUTH_GSS_LENGTH`/`AUTH_GSS_PADDING` depending on Kerberos support, NTLM hash/session key sizes, SMB1 signature/session-key sizes, and `KSMBD_AUTH_*` mechanism bits for NTLMSSP, Kerberos, Microsoft Kerberos, and Kerberos user-to-user. It declares NTLMSSP decode/build/auth functions, optional Kerberos authentication, SMB2/SMB3 signing helpers, SMB3.0/3.1.1 signing and encryption key generation, `ksmbd_gen_preauth_integrity_hash()`, and `ksmbd_crypt_message()`.

Control flow: SMB negotiate/session-setup code includes this header to select offered mechanisms, copy the GSS header, validate NTLM/Kerberos authentication, derive keys once a session is authenticated, and protect subsequent PDUs.

State and persistence behavior: the header owns no state; declared functions operate on `struct ksmbd_conn`, `struct ksmbd_session`, and `struct ksmbd_work` runtime objects.

Dependencies and integration points: includes `ntlmssp.h` and forward-declares core KSMBD structs. It links authentication code to SMB2 session setup, transform encryption, signing verification, and negotiated dialect/cipher policy.

Risks: constants such as GSS length and key sizes must match protocol structs in `ntlmssp.h` and session setup response sizing. Callers must respect that many functions return negative errno and may leave output buffers uninitialized on failure.

Test signals: build both Kerberos and non-Kerberos configs, compile all signing/encryption users, and exercise NTLMSSP, Kerberos, SMB2/SMB3 signing, preauth, and transform encryption paths.
