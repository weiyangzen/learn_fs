<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_spnego.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_spnego.c

Purpose: implements CIFS SPNEGO key management and request-key upcalls used to obtain Kerberos/SPNEGO session setup blobs from userspace helpers.

Important APIs: `cifs_spnego_key_type` defines the `cifs.spnego` key type. `cifs_get_spnego_key()` builds a key description and calls `request_key()`. `init_cifs_spnego()` registers the key type and installs a dedicated `.cifs_spnego` thread keyring under override credentials. `exit_cifs_spnego()` revokes and unregisters the key type. Key payload lifecycle is handled by `cifs_spnego_key_instantiate()` and `cifs_spnego_key_destroy()`.

Control flow: session setup calls `cifs_get_spnego_key()` with session and server state. The function constructs `ver`, host, IP, security mechanism, uid, cred uid, optional username, pid, and upcall target fields; then it uses `scoped_with_creds(spnego_cred)` so request-key caching occurs in the special keyring. The returned key payload is expected to contain `struct cifs_spnego_msg` with session key and security blob.

State and persistence: `spnego_cred` and its thread keyring persist for module lifetime. Individual keys are cached by the kernel keyring subsystem and hold copied payload bytes.

Dependencies and integration: depends on Linux keyrings/request-key, CIFS session/server state, address formatting, security mechanism flags from ASN.1 negotiation, tracepoints, and userspace cifs.upcall behavior.

Risks: key description formatting is ABI with userspace helpers; buffer length calculations must cover all fields. Usernames and hostnames are embedded directly in descriptions. Unknown server auth type falls back to `krb5`, which may hide negotiation issues. Debug2 can dump SPNEGO reply blobs.

Test signals: request-key upcalls for IPv4 and IPv6 servers, krb5/mskrb5/iakerb selection, mount versus app upcall target, user and cred uid fields, username omission, malformed helper payloads, key reuse/caching, module init failure unwinding, and module exit revocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_spnego.c -->
