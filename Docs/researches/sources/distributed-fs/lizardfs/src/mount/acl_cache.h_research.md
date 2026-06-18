# sources/distributed-fs/lizardfs/src/mount/acl_cache.h

## Purpose
`acl_cache.h` defines the ACL cache entry type and loader function used by mount-side permission handling.

## Important APIs, Types, And Functions
- `AclAcquisitionException` wraps non-ENOATTR ACL retrieval failures.
- `RichACLWithOwner` stores a `RichACL` plus owner uid.
- `AclCacheEntry` is `std::shared_ptr<RichACLWithOwner>`.
- `AclCache` is an `LruCache` keyed by inode, uid, and gid, configured with `UseTreeMap` and `Reentrant`.
- `getAcl(uint32_t inode, uint32_t uid, uint32_t gid)` calls `fs_getacl` and returns an entry, null on `ENOATTR`, or throws on other errors.

## Control Flow
`getAcl` allocates a cache entry, asks master communication (`fs_getacl`) for ACL and owner, returns the entry on success, returns an empty shared pointer if no ACL attribute exists, and throws `AclAcquisitionException(status)` for all other statuses.

## State And Persistence
The file defines cache value structure but not a global cache instance. Persistence remains in master metadata; cached ACLs are transient and credential-scoped by key.

## Dependencies And Integration Points
It depends on `mount/mastercomm.h` for `fs_getacl`, `RichACL`, `LruCache`, and LizardFS status codes. It integrates with any caller using `LruCache` to memoize ACL fetches.

## Risks
- Empty `AclCacheEntry` is a meaningful negative-cache value; callers must distinguish missing ACL from acquisition errors.
- Exceptions from `getAcl` cross cache loader boundaries and must be handled by permission code.
- The cache key includes uid/gid, which is correct for credential-sensitive ACL evaluation but can increase cache cardinality.

## Test Signals
Tests should stub `fs_getacl` for OK, `ENOATTR`, and other error codes, ensuring returned owner/ACL propagation, negative result behavior, and exception status preservation.
