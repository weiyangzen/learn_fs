<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_spnego.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_spnego.h

Purpose: declares the userspace-helper payload format and public SPNEGO key acquisition API for the CIFS client.

Important APIs and types: `CIFS_SPNEGO_UPCALL_VERSION` is the request-key protocol version. `struct cifs_spnego_msg` contains version, flags, session-key length, security-blob length, and flexible data containing session key followed by security blob. It declares `cifs_spnego_key_type` and `cifs_get_spnego_key()`.

Control flow: session setup includes this header to request a key and interpret the returned payload from `cifs_spnego.c` and userspace.

State and persistence: no state in the header; the struct layout is a stable kernel/userspace protocol for cifs.upcall-style helpers.

Dependencies and integration: depends on keyring type declarations and CIFS session/server types. It is enabled by `CONFIG_CIFS_UPCALL`.

Risks: any layout or version change needs userspace coordination. Flexible payload parsing must validate both lengths before use.

Test signals: compile with SPNEGO enabled, verify helper payload version matching, session-key/security-blob length validation, and compatibility with existing cifs.upcall implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_spnego.h -->
