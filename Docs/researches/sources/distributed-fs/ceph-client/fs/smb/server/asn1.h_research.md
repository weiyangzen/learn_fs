# sources/distributed-fs/ceph-client/fs/smb/server/asn1.h

Purpose: declares the KSMBD SPNEGO ASN.1 parse/build entry points used by authentication and SMB2 session setup code.

Important APIs/types/functions: exports `ksmbd_decode_negTokenInit()`, `ksmbd_decode_negTokenTarg()`, `build_spnego_ntlmssp_neg_blob()`, and `build_spnego_ntlmssp_auth_blob()`. The decode functions take a security blob and mutate a `struct ksmbd_conn`; the builders allocate a returned buffer and set a 16-bit length.

Control flow: callers decode client-provided SPNEGO tokens before deciding whether to run NTLMSSP or Kerberos authentication. They call the builder helpers when returning NTLMSSP challenge or final session-setup status inside a SPNEGO envelope.

State and persistence behavior: the header declares functions only. State is in the connection and caller-owned allocated buffers.

Dependencies and integration points: relies on forward visibility of `struct ksmbd_conn` from includers and integrates with `auth.c`, generated ASN.1 decoders, and SMB2 session setup response construction.

Risks: the builder APIs allocate memory through output parameters; callers must free on every response/error path. `u16 *buflen` limits practical output length and must match SMB session-setup security buffer sizing.

Test signals: compile coverage for authentication paths, SPNEGO NTLM challenge/final response generation, malformed token decode errors, and memory cleanup on failed session setup.
