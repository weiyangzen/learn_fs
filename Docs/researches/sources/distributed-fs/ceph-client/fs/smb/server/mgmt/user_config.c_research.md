# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/user_config.c

Purpose: imports user account data from the userspace IPC daemon and converts login responses into in-kernel `ksmbd_user` objects used by authentication and authorization.

Important APIs/types/functions: `ksmbd_login_user()` requests account data and optional extension data from userspace. `ksmbd_alloc_user()` allocates/copies name, flags, uid/gid, password hash, and supplementary groups. `ksmbd_free_user()` sends logout notification and frees user memory. `ksmbd_anonymous_user()` and `ksmbd_compare_user()` provide simple identity checks.

Control flow: authentication code calls `ksmbd_login_user()` or, for Kerberos, allocates a user from a login response embedded in the SPNEGO response. Login rejects missing responses and responses without `KSMBD_USER_FLAG_OK`; if the extension flag is set, it requests supplementary groups. Allocation copies all relevant fields into kernel memory. Freeing notifies userspace that the account logged out.

State and persistence behavior: `ksmbd_user` is runtime session state. Persistent account data and password hashes remain owned by userspace configuration. The copied passkey and supplementary group array live until session destruction.

Dependencies and integration points: depends on transport IPC and KSMBD netlink login structures. It integrates with NTLMv2 hash validation, Kerberos session setup, VFS credential override, tree connect authorization, and session reconnect identity checks.

Risks: extension payload length must be trustworthy or validated by IPC code; this file copies `ngroups * sizeof(gid_t)`. `ksmbd_compare_user()` compares passkeys using `u1->passkey_sz` and assumes sizes match from caller context, so callers should check sizes when needed. Passkeys are freed with `kfree`, not explicitly scrubbed in this file.

Test signals: valid/invalid login responses, guest and anonymous users, extension supplementary groups, allocation failure paths, logout notifications, NTLM passkey use, and session reuse attempts with same/different user credentials.
