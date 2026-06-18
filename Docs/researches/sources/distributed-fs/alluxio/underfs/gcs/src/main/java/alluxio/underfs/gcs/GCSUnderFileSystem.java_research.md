## sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSUnderFileSystem.java

### Purpose
`GCSUnderFileSystem` is the legacy Google Cloud Storage UFS implementation backed by jets3t. It adapts GCS buckets and objects to Alluxio's `ObjectUnderFileSystem` contract, including object creation, copy, deletion, listing, metadata lookup, opening streams, and best-effort object permission discovery.

### Important APIs, Types, And Functions
The public factory entry is `createInstance(AlluxioURI, UnderFileSystemConfiguration)`, which requires `GCS_ACCESS_KEY` and `GCS_SECRET_KEY` and builds a `GoogleStorageService`. Important overrides are `copyObject`, `createEmptyObject`, `createObject`, `deleteObject`, `getObjectListingChunk`, `getObjectStatus`, `getPermissions`, `getRootKey`, and `openObject`. The nested `GCSObjectListingChunk` wraps jets3t `StorageObjectsChunk` into Alluxio `ObjectListingChunk`. `mPermissions` memoizes bucket permissions.

### Control Flow
Object operations call the jets3t client directly. Copies retry three times. Listings normalize prefixes, choose a delimiter based on recursive mode, request chunked listings, and expose objects, common prefixes, and follow-up chunks. Metadata lookup maps 404 to `null` and other service failures to `IOException`. Opening delegates to `GCSInputStream`; writing delegates to `GCSOutputStream`; empty directory markers upload zero-byte objects with a precomputed MD5 hash.

### State, Persistence, And Dependencies
Persistent state lives in the GCS bucket. The class holds the bucket name, jets3t client, configuration, and cached `ObjectPermissions`. It depends on jets3t GCS APIs, Alluxio object-store base behavior, `PathUtils`, `ModeUtils`, and static owner-id mapping from configuration.

### Integration Points
The class is selected by `GCSUnderFileSystemFactory` when GCS v2 is not configured. `ObjectUnderFileSystem` supplies high-level file, directory, rename, and recursive-delete behavior around these object primitives. ACLs are not mutable through Alluxio; owner and mode setters are no-ops.

### Risks
The permission cache assumes bucket ACL and owner data do not change during the UFS lifetime. `deleteObject` and copy failures are logged and returned as booleans, so callers must inspect return values. Listing returns `null` on service errors, which can be interpreted as not found by higher layers. Permission inheritance is best effort and falls back to defaults on API failures.

### Test Signals
`GCSUnderFileSystemTest` mocks listing failures and verifies nonrecursive delete, recursive delete, and rename return false. Permission translation is covered separately in `GCSUtilsTest`; factory registration is covered by `GCSUnderFileSystemFactoryTest`.
