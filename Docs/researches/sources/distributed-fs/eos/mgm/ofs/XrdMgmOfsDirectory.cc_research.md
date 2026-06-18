# sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsDirectory.cc

## Purpose
`XrdMgmOfsDirectory.cc` implements the XRootD `XrdSfsDirectory` surface for EOS MGM directory listings. It maps and authorizes callers, resolves namespace paths, loads container metadata and child names, optionally caches listing snapshots, returns entries through `nextEntry()`, and emits audit/listing metrics.

## Important APIs and functions
- `XrdMgmOfsDirectory::XrdMgmOfsDirectory` initializes the object with an empty path and `VirtualIdentity::Nobody()`.
- `getCacheName(id, mtime_sec, mtime_nsec, nofiles, nodirs)` builds an LRU key from container identity, mtime, and listing filter flags.
- `open(const char*, const XrdSecEntity*, const char*)` is the authenticated XRootD entry point. It runs namespace mapping, illegal-name checks, external authorization, identity mapping, access-mode routing macros, and delegates to `_open`.
- `open(const char*, VirtualIdentity&, const char*)` is the already-mapped identity variant, used by internal callers.
- `_open` does the actual metadata fetch, permission/ACL/public-access check, listing construction, optional cache lookup/insert, stats, and audit emission.
- `nextEntry()` returns the current cached string pointer and advances the iterator.
- `close()` drops the shared listing.
- `Emsg()` formats errors into `XrdOucErrInfo`, logging `ENOENT` as debug and other failures as errors.

## Control flow
The public `open` path first applies `NAMESPACEMAP`, `BOUNCE_ILLEGAL_NAMES`, `AUTHORIZE`, `Mapping::IdMap`, `BOUNCE_NOT_ALLOWED`, `ACCESSMODE_R`, `MAYSTALL`, and `MAYREDIRECT`. `_open` records the token validation scope as the directory path with a trailing slash, logs non-conversion listings, increments `OpenDir`, parses opaque filters, and prefetches the target container plus children.

Under `eosViewRWMutex`, `_open` retrieves the `IContainerMD`, obtains mtime for the cache key, releases the namespace lock, evaluates POSIX `R_OK | X_OK` access for non-token identities, then evaluates ACL browse permissions. If browsing is allowed, it locks `mDirLsMutex`, tries `dirCache` when `EOS_MGM_LISTING_CACHE` enabled it, and otherwise builds a `std::set<std::string>` from `FileMapIterator` and `ContainerMapIterator`. The opaque flags `ls.skip.files` and `ls.skip.directories` suppress file or directory entries. Directory listings include `.` and include `..` except for root. The iterator is initialized to `begin`, and the listing is stored in the static LRU cache when enabled.

Failures to fetch metadata become `errno` from `MDException` and return `Emsg`. After metadata success, `_open` rejects failed permission checks with `EPERM` and rejects paths failing global public access restrictions with `EACCES`. On success it stores `dirName`, ends timing, and optionally emits an audit `LIST` event depending on global audit mode or per-directory `sys.audit`.

## State and persistence behavior
The object stores `dirName`, `vid`, a shared pointer to immutable-ish listing content, and an iterator into that listing. `dirCache` is static process-wide LRU state; enabling and sizing it is controlled by `EOS_MGM_LISTING_CACHE` at first `_open` execution. No namespace state is modified by directory listing, but stats counters and audit logs are emitted. Prefetching may populate metadata caches outside this class.

## Dependencies and integration points
The implementation depends on XRootD SFS and auth types, `XrdOucEnv` opaque parsing, EOS security macros, `Mapping`, `Acl`, `Access`, `Path`, `Prefetcher`, namespace `IView`/`IContainerMD`, file/container child iterators, global `gOFS`, `MgmStats`, `allow_public_access`, and `common::Audit`. The class is declared in `XrdMgmOfsDirectory.hh` and used as the MGM directory plugin object returned to XRootD.

## Risks and edge cases
- Listing cache invalidation relies on container id plus mtime and filter flags. If child changes do not reliably update mtime with nanosecond precision, stale listings are possible.
- The cache stores complete `std::set` listings, so large directories can consume memory even with LRU bounds.
- `nextEntry()` returns `c_str()` from strings owned by `dh_list`; callers must not use returned pointers after `nextEntry`, `close`, or object destruction assumptions change.
- `vid.scope.back()` assumes non-empty `dir_path` after `dir_path` truthiness; empty string input could be unsafe.
- ACL construction receives an empty `attrmap` in this file; correctness depends on `Acl` fetching or interpreting attributes through other mechanisms.
- Token identities skip POSIX access by setting `permok` false initially and rely on ACL browse permissions or other auth layers.

## Test signals
Tests should cover successful listings with files/directories, root `..` omission, `ls.skip.files`, `ls.skip.directories`, cache enable/disable and mtime invalidation, ACL allow/deny browse overriding POSIX mode, token and non-token identities, public access restriction rejection, missing container errors, `nextEntry()` EOF behavior, `close()` idempotence, and audit `LIST` emission in global and attribute-only modes.
