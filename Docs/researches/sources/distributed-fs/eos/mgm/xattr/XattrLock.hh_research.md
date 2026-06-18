## sources/distributed-fs/eos/mgm/xattr/XattrLock.hh

Purpose: Implements application-level file locks stored in EOS extended attributes, including shared/exclusive mode, owner matching with limited wildcards, expiry, and FUSE open-state bypass.

Important APIs and types: `XattrLock` can parse an `IFileMD::XAttrMap`, `Parse` decodes `expires/type/owner`, `foreignLock` decides whether access is blocked, `Lock` writes `EOS_APP_LOCK_ATTR`, `Unlock` removes it, and `Value` serializes the lock attribute.

Control flow: `Lock` prefetches and write-locks file metadata, reads any existing app-lock xattr, rejects active foreign locks, validates lifetime and wildcard rules, computes owner and expiry, and sets the xattr. `Unlock` performs the same prefetch/write-lock/get/foreign-lock check before removing the xattr.

State and persistence: object state mirrors the xattr fields plus `isfuseopen`, and persisted state is the `EOS_APP_LOCK_ATTR` string. `sys.fusex.state` ending without `|` disables foreign-lock enforcement while a FUSE commit is open.

Dependencies and integration: depends on MGM `gOFS`, namespace `Prefetcher`, `MDLocking::writeLock`, `_attr_get/_attr_set/_attr_rem`, `VirtualIdentity`, and common lock attribute constants.

Risks: the constructor uses `attr["sys.fusex.state"]`, which inserts an empty entry into the copied map. Expiry parsing uses `atoi`, so malformed or overflowing values can become zero. Locks longer than one week are ignored for access and rejected on create; tests should keep those semantics aligned. `foreignLock` owner matching only supports exact, wildcard-user, or wildcard-app, not both.

Test signals: cover parse failures, shared read pass-through, exclusive write blocking, expired lock behavior, illegal lifetime, wildcard validation, FUSE open bypass, errno values (`EBUSY`, `EINVAL`, metadata errno), and xattr removal.
