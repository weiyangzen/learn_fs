# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/share_config.h

Purpose: defines the in-kernel KSMBD share configuration object and helper APIs used by tree connects and VFS operations.

Important APIs/types/functions: `struct ksmbd_share_config` stores name, path, path size, share flags, veto list, pinned VFS path, refcount, hash node, create/directory masks, forced modes, and forced uid/gid. `KSMBD_SHARE_INVALID_UID/GID` mark absent forced IDs. Inline helpers `share_config_create_mode()` and `share_config_directory_mode()` apply mask/force rules, while `test_share_config_flag()` checks share flags. APIs include get/put/delete and veto filename matching.

Control flow: tree-connect code obtains a referenced share config, VFS code consults flags/modes/path, and disconnect code drops references. The put helper decrements the atomic refcount and calls the full deletion/free path on the last reference.

State and persistence behavior: share configs are runtime cache entries, not durable config. `vfs_path` pins the resolved path while the share object is alive. Mode masks and force IDs are copied from userspace and remain fixed until cache invalidation/update.

Dependencies and integration points: depends on Linux workqueue/hashtable/path/unicode headers, KSMBD netlink share flags, and VFS/share-management code.

Risks: mode helper behavior treats zero POSIX mode as all bits before masking, so callers must pass zero only when they want default mask behavior. Put/delete ordering must not remove an object still reachable without a refcount.

Test signals: file and directory create mode calculations, read-only/writeable/pipe flag behavior, refcounted share lifetime across multiple tree connects, and veto filename checks.
