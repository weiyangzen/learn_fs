# sources/distributed-fs/ceph/src/rgw/driver/posix/rgw_sal_posix.cc

## Purpose
`rgw_sal_posix.cc` implements the Ceph RGW Store Abstraction Layer backend that stores buckets and objects directly on a POSIX filesystem. Bucket directories, object files/directories/symlinks, extended attributes, a SQLite user/account DB, and the LMDB listing cache together emulate enough RGW behavior for the POSIX driver.

## Important APIs, Types, and Functions
Helper functions encode object filenames (`get_key_fname()`), bucket directory names (`bucket_fname()`), random instance/upload names, xattr reads/writes/removals, owner decode, and recursive directory deletion. `FSEnt` implements common stat/xattr/fill-cache behavior. `File`, `Directory`, `Symlink`, `MPDirectory`, and `VersionedDirectory` implement concrete filesystem object shapes.

`POSIXDriver::initialize()` creates the bucket cache, opens or creates the root directory, and initializes quota handling. User/account methods delegate to `POSIXUserDB` and `POSIXAccountDB`. `POSIXBucket` implements create/load/list/remove/stats/xattrs/multipart listing. `POSIXObject` implements stat/open/read/write/delete/copy/xattrs/version selection. `POSIXAtomicWriter`, `POSIXMultipartUpload`, and `POSIXMultipartWriter` implement write paths and multipart completion.

## Control Flow
Object names are URL-encoded for filenames; namespaced objects are hidden by a leading dot. Buckets are directories under `rgw_posix_base_path`. Bucket metadata is stored as xattrs, including encoded `RGWBucketInfo`. Objects store RGW attrs as `user.X-RGW-*` xattrs and have a `POSIX-Object-Type` xattr.

Reads call `POSIXReadOp::prepare()`, stat the object, load attrs, generate an MD5 ETag once for side-loaded files if missing, validate conditional headers, then stream data with `read()`. Atomic writes create an unnamed `O_TMPFILE`, write buffers, write xattrs including `POSIXOwner`, link the temp file into the bucket, rename it to the final object, update the bucket cache, and update quota stats.

Versioned objects are directories. A version file is named with the encoded oid including instance; a symlink named like the base object points to the current version. Removing a base object creates a delete marker by moving the current symlink to a generated missing target; removing a specific version deletes the matching file and repoints or removes the symlink. Multipart uploads use hidden `.multipart_*` shadow buckets containing part files and a metadata object; completion validates parts/ETags, computes final multipart ETag, writes manifest attrs, and renames the shadow directory to the final object.

Bucket listing flows through `POSIXBucket::list()`, which normalizes marker/prefix and delegates to `BucketCache::list_bucket()`. The callback applies visibility, version, namespace, prefix, delimiter, marker, truncation, and common-prefix logic.

## State and Persistence Behavior
Durable state is filesystem entries plus xattrs and SQLite user/account DB rows. The LMDB bucket listing cache is transient and rebuilt from directories. Quota stats are updated through `RGWQuotaHandler`, but many stats/index APIs are stubs. File close fsyncs regular files. Directory operations use fd-relative syscalls (`openat`, `mkdirat`, `unlinkat`, `renameat2`, `statx`) to reduce path races.

## Dependencies and Integration Points
The file depends on Linux/POSIX syscalls, xattrs, Ceph RGW SAL interfaces, quota, MD5, bufferlist encoding, DBStore, `bucket_cache.h`, `posixDB.h`, and RGW notification/lifecycle/multipart interfaces. It exports `newPOSIXDriver(CephContext*)` for dynamic driver creation.

## Risks
Many SAL surfaces return `0`, `nullptr`, or `-ENOTSUP`, including lifecycle, sync, roles, Lua, cloud transition, omap, usage, and some stats/index operations. `if_nomatch == "*"` logic in atomic complete appears inverted relative to "must not exist" semantics. `std::string value; value.reserve(); vp = &value[0]` in xattr read writes into un-sized storage, which is unsafe. `copy_file_range()` is called once and may not copy full files. `renameat2(RENAME_EXCHANGE)` and `O_TMPFILE` are Linux-specific. Version/delete marker behavior is subtle and needs broad tests.

## Test Signals
High-value tests include bucket create/load/list/remove, xattr round trips, side-loaded file ETag generation, atomic writer conditionals, quota delta updates, list prefix/delimiter/marker/version cases, inotify cache coherence, versioned put/delete/specific-version delete/copy, multipart init/upload/list/complete/abort, recursive removal, fsync/error paths, and sanitizer coverage for xattr buffer handling and cache reference lifetimes.
