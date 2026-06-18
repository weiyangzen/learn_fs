# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/share_config.c

Purpose: obtains, validates, caches, references, and frees KSMBD share configuration imported from the userspace IPC daemon.

Important APIs/types/functions: public APIs are `ksmbd_share_config_get()`, `ksmbd_share_config_put()` through the header, `ksmbd_share_config_del()`, `__ksmbd_share_config_put()`, and `ksmbd_share_veto_filename()`. Internals include the `shares_table` hashtable keyed by `jhash(name)`, `shares_table_lock`, `struct ksmbd_veto_pattern`, `parse_veto_list()`, `share_config_request()`, and `kill_share()`.

Control flow: lookup first tries the in-kernel cache under a read lock and increments the share refcount if present. On miss, `share_config_request()` asks userspace for the share, rejects invalid flags or mismatched casefolded share names, allocates a `ksmbd_share_config`, copies flags/masks/force uid-gid/name, parses veto patterns, normalizes trailing slashes from the path, temporarily overrides fsids for path lookup, and caches the share under a write lock unless another racing lookup already inserted it. Share updates from tree-connect responses delete the stale cache entry so a fresh request is made.

State and persistence behavior: runtime share configs are cached in `shares_table` with atomic refcounts. Disk path state is pinned by `struct path vfs_path` and released with `path_put()`. Veto patterns, share name, and path strings are kernel allocations. Persistent share definitions remain in userspace configuration.

Dependencies and integration points: depends on transport IPC, user/session context for fsuid/fsgid override, Unicode casefolding, VFS path lookup, wildcard matching, KSMBD share flag ABI, and tree-connect management.

Risks: variable payload parsing from userspace must keep veto-list and path lengths consistent. Path lookup under overridden fsids is security-sensitive and must always revert credentials. Cache races are handled by rechecking under the write lock; missed refcounting would use freed share configs. Share update invalidation must not drop a share still referenced by active tree connections.

Test signals: share cache hits/misses, case-insensitive share name matching, invalid userspace responses, disk and IPC pipe shares, veto list matching, trailing slash normalization, inaccessible path handling, forced modes/uid/gid, share update flag behavior, concurrent tree connects to the same share, and cleanup after disconnect.
