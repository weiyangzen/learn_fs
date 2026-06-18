## sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSLowLevelOutputStream.java

### Purpose
`OBSLowLevelOutputStream` implements streaming/multipart OBS uploads by specializing Alluxio's `ObjectLowLevelOutputStream`.

### Important APIs, Types, And Functions
It holds an `IObsClient`, synchronized part ETags, upload id, and optional content hash. It implements multipart hooks: `initMultiPartUploadInternal`, `uploadPartInternal`, `completeMultiPartUploadInternal`, `abortMultiPartUploadInternal`, plus single-object hooks `createEmptyObject` and `putObject`. `getContentHash` returns the OBS ETag.

### Control Flow
Initialization starts a multipart upload and stores the upload id. Each part upload builds an `UploadPartRequest`, optionally sets MD5, uploads the file part, and records the returned ETag/part number. Completion submits all tags and stores the final ETag. Abort cancels by upload id. Small or empty object paths call put-object APIs directly.

### State, Persistence, And Dependencies
State includes multipart upload id, synchronized tag list, content hash, bucket/key inherited from the base class, and executor inherited from `ObjectLowLevelOutputStream`. Persistent effects are OBS objects and intermediate multipart upload state.

### Integration Points
`OBSUnderFileSystem.createObject` returns this stream when `UNDERFS_OBS_STREAMING_UPLOAD_ENABLED` is true.

### Risks
Part tag ordering relies on the OBS SDK accepting the synchronized list order as tasks complete; if completion requires sorted part numbers, parallel uploads may need explicit sorting. Abort error messages say "complete" in one path. Correct cleanup depends on base-class error handling invoking abort.

### Test Signals
No direct tests are present. Tests should cover multipart success, parallel part ordering, abort on failure, empty object creation, MD5 propagation, and content hash exposure.
