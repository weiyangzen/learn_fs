## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ObjectUnderFileSystem.java

### Purpose
`ObjectUnderFileSystem` is the shared abstract implementation for object-store-backed UFS adapters. It translates Alluxio filesystem operations into object operations, synthesizes directory semantics from zero-byte directory marker objects plus common-prefix listings, implements retry behavior for eventual consistency, and provides batched concurrent delete/rename support for stores where rename is copy plus delete.

### Important APIs, Types, And Functions
The class extends `BaseUnderFileSystem`, so it inherits fingerprint, async listing, recursive listing fallback, ACL defaults, and rate limiting. Key nested types are `ObjectStatus` for object metadata, `ObjectListingChunk` for paginated listings, `ObjectPermissions` for bucket-level owner/group/mode, and the generic `OperationBuffer<T>` used by `DeleteBuffer` and `RenameBuffer`.

Subclass extension points are `createEmptyObject`, `createObject`, `copyObject`, `deleteObject`, `getPermissions`, `getObjectStatus`, `getFolderSuffix`, `getObjectListingChunk`, `getRootKey`, `openObject`, and `getUnderFSType`. Public UFS overrides cover create, delete, status, listing, mkdirs, open, rename, object-storage detection, unsupported file locations, and unsupported flush.

### Control Flow
Create optionally creates the parent path unless parent creation is skipped by configuration, then calls `createObject` on the stripped key. File status calls `getObjectStatus`; directory status uses `isDirectory`; general status checks root, then file metadata, then directory status. Directory existence is inferred from root, explicit marker object, or a listing whose first chunk has objects or common prefixes. `getObjectListingChunkForPath` may create a breadcrumb marker for discovered pseudo-directories when breadcrumbs are enabled and the mount is writable.

Listing obtains a first chunk, handles explicit empty-directory markers, normalizes the key prefix, then repeatedly calls `populateUfsStatus`. That method converts marker objects to `UfsDirectoryStatus`, ordinary objects to `UfsFileStatus`, and common prefixes or inferred recursive prefixes to directory statuses. `UfsStatusIterator` lazily fetches chunks and uses a sorted `TreeMap`, trimming entries already returned from a prior chunk by `mLastKey`.

Recursive delete lists descendants recursively, sorts them in reverse name order, batches file and marker deletes, then validates that all entries were deleted. Directory rename first copies the source marker, recursively copies children, queues deletes after successful copies, and fails if any batch has missing successes. File rename validates source file and destination absence, then copies and deletes. `retryOnException` retries only transient IO classes such as EOF, DNS, connection timeout, and socket errors; `retryOnFalse` retries false returns.

### State And Persistence
In-memory state includes the object-service executor, memoized root key supplier, breadcrumbs flag, and operation buffers. Persistent state is entirely in the object store: uploaded file objects, zero-byte directory marker objects using `getFolderSuffix`, copied destination objects, and deleted source keys. CRC64 metadata from `ObjectStatus` is propagated into `UfsFileStatus` xattrs under `Constants.CRC64_KEY`.

### Dependencies And Integration Points
This class depends on Alluxio configuration keys for object-store threads, breadcrumbs, listing length, block size, parent creation skipping, and eventual-consistency retry tuning. It integrates with `BaseUnderFileSystem` for async metadata sync and with provider implementations for S3, OSS, GCS, and similar stores. It uses `PathUtils`, `CommonUtils`, `RetryPolicy`, and executor factories.

### Risks
Object-store directory semantics are inherently inferred; marker-object and common-prefix handling must stay consistent or Alluxio metadata sync can miss or duplicate directories. Rename is non-atomic and can leave copied-but-not-deleted objects after partial failures. `OperationBuffer` suppresses per-batch IO exceptions into empty success lists, so callers must compare success counts. Breadcrumb creation during read/list paths mutates storage unless read-only. `handleRetriablException` appears misspelled but functional; expanding retry classes can hide permanent errors.

### Test Signals
`ObjectUnderFileSystemTest` verifies transient `SocketException` retry and non-retry for `FileNotFoundException`, plus object-store async listing behavior for `DescendantType.NONE`. `MockObjectUnderFileSystem` supplies a minimal subclass for these tests. Broader correctness depends on concrete object-store modules and metadata-sync tests.
