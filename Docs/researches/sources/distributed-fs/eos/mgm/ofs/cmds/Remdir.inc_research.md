## sources/distributed-fs/eos/mgm/ofs/cmds/Remdir.inc

Purpose: implements directory deletion for `XrdMgmOfs`. The public `remdir()` entrypoint maps the XRootD security entity into a `VirtualIdentity`, performs namespace mapping, token scope checks, authorization for `AOP_Delete`, write access mode, stall/redirect checks, and delegates to `_remdir()`.

Important APIs and types: `XrdMgmOfs::remdir`, `XrdMgmOfs::_remdir`, `eos::common::VirtualIdentity`, `eos::common::Path`, `eos::IContainerMD`, `Acl`, `Quota`, `ProcCommand`, `RWMutexWriteLock`, and FuseX broadcast helpers. `_remdir()` supports a `simulate` parameter used by callers that need permission/existence validation without mutation.

Control flow: `_remdir()` rejects quota-node paths first, then takes the EOS view write lock, resolves the target container and its parent, builds the ACL path from the symlink-free parent URI, and returns `ENOENT` if the container is missing. If `mgm.option=r` is passed, it releases the namespace lock and runs the recursive `/proc/user` `rm -r` command instead of doing direct container removal. Non-recursive deletion evaluates immutable ACLs, public-access restrictions, explicit ACL delete/write denies, POSIX parent `W_OK|X_OK`, token-based UNIX-permission bypass, and sticky-bit ownership rules before mutating metadata.

State and persistence behavior: successful deletion updates parent directory mtime, notifies the directory service, persists the parent container, removes the child container from the view, releases the namespace lock, and broadcasts FuseX deletion/refresh events. It emits an audit `RMDIR` event with a trailing slash for directory paths when audit is enabled and `AllowAuditModification()` permits it.

Dependencies and integration points: integrates with quota-node checks (`Quota::Exists` and `QUOTA_NODE_FLAG`), ACL evaluation, public-access policy, the `/proc/user` command interface for recursive deletion, MGM stats/timing, EOS namespace services, and FuseX client cache invalidation. It is called directly from the XRootD `rmdir` API and indirectly by rename overwrite handling for empty target directories.

Risks: the expression `(dh->getFlags() && eos::QUOTA_NODE_FLAG)` is logical rather than bitwise and will treat any nonzero flags as a quota-node match for non-root users. Recursive mode releases the view lock before invoking `ProcCommand`, so state can change between permission checks and recursive execution. Permission behavior differs between ACL, sticky-bit, and token cases and should be regression-tested around explicit `!d`/`!w` ACLs.

Test signals: cover non-empty directory deletion (`ENOTEMPTY`), quota-node rejection, immutable ACL denial, explicit ACL delete/write denial, sticky-bit owner-only deletion, token-authorized deletion bypassing UNIX mode checks, recursive `mgm.option=r` dispatch, parent mtime/FuseX notifications, and audit emission on successful deletion.
