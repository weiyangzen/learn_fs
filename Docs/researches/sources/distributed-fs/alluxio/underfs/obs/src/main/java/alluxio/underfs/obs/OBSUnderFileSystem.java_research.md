## sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSUnderFileSystem.java

### Purpose
`OBSUnderFileSystem` adapts Huawei OBS buckets to Alluxio's `ObjectUnderFileSystem`, including special handling for OBS PFS buckets and optional streaming multipart uploads.

### Important APIs, Types, And Functions
`createInstance` validates OBS access key, secret key, endpoint, and bucket type, constructs `ObsClientExt`, and extracts the bucket name. Core overrides include `cleanup`, `copyObject`, `createEmptyObject`, `createObject`, `deleteObject`, `deleteObjects`, `getObjectListingChunk`, `getObjectStatus`, `isDirectory`, `getPermissions`, `getRootKey`, `openObject`, and `renameDirectory`. The nested `OBSObjectListingChunk` wraps OBS object listings.

### Control Flow
Cleanup lists multipart uploads and aborts those older than configured age. Creates choose streaming `OBSLowLevelOutputStream` or local-temp `OBSOutputStream`. Listings normalize prefixes, set delimiter and max keys, then page by marker. In PFS mode, listings and object status distinguish explicit directories via metadata mode bits. Bulk delete converts keys to `KeyAndVersion` and returns deleted keys. PFS directory rename uses OBS `renameFolder`; non-PFS delegates to inherited object-store rename.

### State, Persistence, And Dependencies
State includes `ObsClient`, bucket name, bucket type, and memoized streaming-upload executor. Persistent state is OBS objects and multipart uploads. Dependencies include Huawei OBS SDK models, Alluxio object UFS base classes, executor factories, and configuration keys for streaming upload and cleanup.

### Integration Points
The OBS factory outside this file creates this class for OBS schemes. Input/output stream classes implement read and write behavior. `ObjectUnderFileSystem` supplies higher-level directory/file semantics over the primitive object calls.

### Risks
PFS directory detection parses metadata `mode` without guarding missing/non-numeric values. Listing errors return null and can be interpreted as not found. `copyObject` writes to stdout on failure. Streaming upload executor is memoized but no explicit shutdown appears in `cleanup`. PFS and object-bucket behavior diverge in status and rename paths, requiring separate tests.

### Test Signals
No OBS tests are included in this subset. Coverage should include credential validation, PFS directory metadata, listing pagination, multipart cleanup, streaming/local output selection, bulk delete, and PFS rename status handling.
