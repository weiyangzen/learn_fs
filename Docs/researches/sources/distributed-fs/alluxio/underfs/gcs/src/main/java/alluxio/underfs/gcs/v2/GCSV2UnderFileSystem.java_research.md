## sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/v2/GCSV2UnderFileSystem.java

### Purpose
`GCSV2UnderFileSystem` is the Google Cloud Storage UFS implementation based on `com.google.cloud.storage`. It implements the `ObjectUnderFileSystem` primitives using the newer GCS client library.

### Important APIs, Types, And Functions
`createInstance` loads explicit service-account credentials from `GCS_CREDENTIAL_PATH` or application-default credentials, configures retry settings, and creates a `Storage` service. Core overrides include `copyObject`, `createEmptyObject`, `createObject`, `deleteObject`, `getObjectListingChunk`, `getObjectStatus`, `getPermissions`, `getRootKey`, and `openObject`. The nested `GCSObjectListingChunk` wraps paged `Blob` listings.

### Control Flow
Listings normalize prefixes and either call `Storage.list` with a prefix only for recursive scans or with `currentDirectory` for one-level scans. Each page is converted to object statuses and followed with `getNextPage`. Metadata lookup treats null and 404 as not found. Writes use `GCSV2OutputStream`; reads use `GCSV2InputStream`.

### State, Persistence, And Dependencies
State is the storage client, bucket name, and UFS config. Persistent data is in the GCS bucket. Dependencies include Google auth, gax retry settings, `StorageOptions`, Alluxio object UFS support, and `ModeUtils` for default permissions.

### Integration Points
`GCSUnderFileSystemFactory` selects this implementation when `UNDERFS_GCS_VERSION` is `2`. It provides the same `getUnderFSType` value as legacy GCS, so upper layers see it as `"gcs"`.

### Risks
ACL inheritance is not implemented; permissions always use configured default mode and empty owner/group. `getCommonPrefixes` returns an empty array even for directory listings, relying on `currentDirectory` blobs instead of explicit common prefixes. Empty object creation does not set the static directory hash in metadata.

### Test Signals
There are no direct v2 tests in this subset. Useful coverage would mock `Storage` for listing pagination, copy/delete failures, credentials selection, retry settings, open offsets, and empty-object behavior.
