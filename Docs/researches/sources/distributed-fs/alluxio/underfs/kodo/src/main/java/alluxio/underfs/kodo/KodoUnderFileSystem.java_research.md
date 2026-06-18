## sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoUnderFileSystem.java

### Purpose
`KodoUnderFileSystem` adapts Qiniu Kodo to Alluxio's `ObjectUnderFileSystem` abstraction.

### Important APIs, Types, And Functions
`creatInstance` validates Kodo access key, secret key, download host, and endpoint; creates Qiniu auth/configuration and OkHttp client; and returns the UFS. Core overrides include `copyObject`, `createEmptyObject`, `createObject`, `deleteObject`, `getObjectListingChunk`, `getObjectStatus`, `getPermissions`, `openObject`, and `getRootKey`. The nested `KodoObjectListingChunk` wraps `FileListing`.

### Control Flow
Object primitives call `KodoClient` and map `QiniuException` to false/null/logging. Listings normalize prefixes, choose delimiter based on recursive mode, request chunks, return object statuses and common prefixes, and page using the returned marker until EOF. Reads and writes use Kodo stream wrappers.

### State, Persistence, And Dependencies
State is the Kodo client and inherited configuration. Persistent data lives in the Kodo bucket. Dependencies include Qiniu SDK models, OkHttp configuration, Alluxio object UFS support, and configured tmp dirs/chunk sizes.

### Integration Points
`KodoUnderFileSystemFactory` creates this UFS for `kodo://` paths. Higher-level object-store rename/delete behavior is inherited from `ObjectUnderFileSystem`.

### Risks
The static factory name is misspelled `creatInstance`, but callers use it consistently. `initializeKodoClientConfig` creates a dispatcher and sets max requests but does not attach it to the OkHttp builder, so that setting appears ineffective. Listing errors return null, causing high-level operations to fail as not found.

### Test Signals
`KodoUnderFileSystemTest` mocks listing failures and verifies recursive/nonrecursive directory delete and rename return false.
