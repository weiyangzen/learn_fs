# sources/distributed-fs/ceph/src/rgw/driver/posix/rgw_sal_posix.h

## Purpose
`rgw_sal_posix.h` declares the POSIX-backed RGW SAL driver, filesystem entity hierarchy, bucket/object/user/account wrappers, multipart classes, writers, and lightweight zone/notification/lua stubs. It is the public contract for `rgw_sal_posix.cc`.

## Important APIs, Types, and Functions
`ObjectType` encodes the filesystem representation: file, directory, versioned directory, multipart directory, symlink, or unknown. `FSEnt` is the abstract base for filesystem entries and declares create/open/close/stat/remove/read/write/xattr/copy/cache-fill operations. `File`, `Directory`, `Symlink`, `MPDirectory`, and `VersionedDirectory` specialize those operations.

`POSIXDriver` inherits `StoreDriver` and owns `CephContext`, `POSIXUserDB`, `POSIXAccountDB`, `POSIXZone`, `BucketCache`, root directory, sync module, and quota handler. It declares user/account lookup and store methods, bucket/object factories, listing and metadata APIs, writer factories, notification creation, and internal helpers such as `mint_listing_entry()`.

`POSIXBucket` inherits `StoreBucket` and declares object lookup, list, attrs, stats, remove/create/load, multipart operations, quota checks, and filesystem helpers. `POSIXObject` inherits `StoreObject` and declares delete/copy/read ops, attrs, object state, transitions, multipart serializer, file entity construction, temp linking, cache filling, version handling, and ETag generation. Multipart support is declared through `POSIXMPObj`, `POSIXUploadPartInfo`, `POSIXMultipartPart`, `POSIXMultipartUpload`, `POSIXMultipartWriter`, and `POSIXAtomicWriter`.

## Control Flow
The header establishes the object model used by the implementation. Driver initialization creates roots and caches. Buckets wrap `Directory` instances. Objects wrap an `FSEnt` selected by object type and bucket versioning. Writers create file or versioned-directory entities and later link temp files into place. Multipart uploads create hidden shadow buckets and eventually rename them into the target namespace.

## State and Persistence Behavior
Class state mirrors persisted filesystem state: filenames, parent directories, fds, `statx` data, xattrs, bucket info, object attrs, version instance IDs, multipart parts, and manifest metadata. `POSIXDriver` also owns SQLite DB handles for users/accounts and an ephemeral bucket listing cache.

## Dependencies and Integration Points
The header depends on Ceph SAL base classes, RGW quota, RGW common types, `bucket_cache.h`, and `posixDB.h`. It is used by the dynamic driver entrypoint, RGW frontend code through SAL virtual methods, the bucket cache through `POSIXDriver`/`POSIXBucket` template parameters, and DBStore for identity metadata.

## Risks
The declaration surface is much broader than the implementation maturity: many virtual methods are stubs or partial. Ownership relies heavily on raw parent pointers plus cloned `unique_ptr` entries, so lifetime assumptions matter. File descriptors are cached inside mutable objects and many methods implicitly open them. The driver is Linux/POSIX-specific despite implementing generic SAL interfaces. Versioned and multipart object representations are non-obvious and require strict filename/xattr compatibility.

## Test Signals
Compile coverage should validate all SAL overrides against current RGW interfaces. Behavioral tests should instantiate the driver, exercise each `FSEnt` subclass, user/account DB paths, bucket and object lifecycle, writers, multipart classes, versioned directories, bucket cache integration, and unsupported APIs returning expected errors.
