## sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoClient.java

### Purpose
`KodoClient` centralizes Qiniu SDK and OkHttp operations used by the Kodo UFS.

### Important APIs, Types, And Functions
The constructor wires `Auth`, bucket/download host/endpoint, Qiniu `BucketManager`, `UploadManager`, and `OkHttpClient`. Methods include `getBucketName`, `getFileInfo`, `getObject`, `uploadFile`, `copyObject`, `createEmptyObject`, `deleteObject`, and `listFiles`.

### Control Flow
Metadata, copy, delete, and list delegate to Qiniu SDK managers. `getObject` signs a private download URL, rewrites it through the configured endpoint, adds a byte `Range` header and `Host`, executes OkHttp, maps 404 to Alluxio `NotFoundException`, and returns the response body stream for 200/206 responses. Uploads and empty-object creation close Qiniu responses after put/delete operations.

### State, Persistence, And Dependencies
State is client configuration and SDK client instances. Persistent state is the Kodo bucket. Dependencies include Qiniu SDK, OkHttp, HTTP status codes, and Alluxio `NotFoundException`.

### Integration Points
`KodoUnderFileSystem`, `KodoInputStream`, and `KodoOutputStream` call this client for all object-store operations.

### Risks
`getObject` returns a body stream without separately managing the OkHttp `Response`, so lifecycle depends on stream close behavior. The signed URL is rewritten to `http://` endpoint, which may be inappropriate for HTTPS-only deployments. Parameter names use uppercase in upload methods but are behaviorally normal.

### Test Signals
No direct tests mock `KodoClient` internals in this subset. UFS tests mock it at the method level, and output stream tests verify upload invocation paths indirectly.
