# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/user_config.h

Purpose: defines KSMBD's runtime user object and small helpers for user flags, identity fields, and passkey access.

Important APIs/types/functions: `struct ksmbd_user` stores flags, uid, gid, account name, password hash/passkey size, supplementary group count, and supplementary group IDs. Inline helpers include `user_guest()`, `set_user_flag()`, `test_user_flag()`, `user_passkey()`, `user_name()`, `user_uid()`, and `user_gid()`. Declared APIs cover login, allocation, free, anonymous check, and comparison.

Control flow: authentication populates a `ksmbd_user`, sessions hold it, VFS paths use uid/gid/groups for credential override, and logoff frees it through `ksmbd_free_user()`.

State and persistence behavior: user objects are transient copies of userspace account data. Passkeys remain in memory for session lifetime because NTLMv2 validation needs them.

Dependencies and integration points: includes KSMBD globals and netlink user flag definitions through includers. It integrates with auth, sessions, share config, and VFS credential handling.

Risks: `set_user_guest()` is a no-op, so code must set guest status via flags rather than that helper. Accessors expose mutable pointers to name/passkey; callers must not retain them past user lifetime.

Test signals: guest flag behavior, anonymous user name handling, VFS uid/gid use, supplementary group propagation, and cleanup after failed or completed sessions.
