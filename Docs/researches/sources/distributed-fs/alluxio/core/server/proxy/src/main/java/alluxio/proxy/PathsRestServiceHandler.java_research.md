# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/PathsRestServiceHandler.java

## Purpose
`PathsRestServiceHandler` exposes Alluxio filesystem metadata and stream-opening operations through the proxy REST API under `/paths`. It is the metadata side of the proxy REST gateway.

## Important APIs, Types, and Functions
Endpoints include `create-directory`, `create-file`, `delete`, `download-file`, `exists`, `free`, `get-status`, `list-status`, `mount`, `open-file`, `rename`, `set-attribute`, and `unmount`. Methods accept Alluxio gRPC option objects such as `CreateDirectoryPOptions`, `CreateFilePOptions`, `DeletePOptions`, `ListStatusPOptions`, and others. `createFile` and `openFile` place `FileOutStream` or `FileInStream` instances into `StreamCache` and return integer IDs.

## Control Flow, State, and Persistence
The constructor obtains `FileSystem` and `StreamCache` from the proxy servlet context. Each endpoint wraps a filesystem call in `RestUtils.call`, constructs `AlluxioURI` from the path parameter, and uses no-options overloads when the JSON body is null. Mount and rename validate required query parameters with `Preconditions.checkNotNull`. `downloadFile` returns a live input stream directly with a `Content-Disposition` header. Persistent effects are the filesystem mutations requested by callers: create, delete, mount, rename, set attributes, free, and unmount.

## Dependencies and Integration Points
The handler integrates Jersey and Swagger annotations, Alluxio filesystem client APIs, gRPC option messages, `StreamCache`, `ProxyWebServer` servlet resources, and `RestUtils` error/response conversion.

## Risks
The catch-all `{path:.*}/` path parameter makes URL encoding and slash handling important. Returning open streams through `StreamCache` requires clients to close stream IDs or rely on timeout eviction. Null option bodies silently choose default filesystem overloads. The handler is annotated not thread-safe but Jersey may create/request instances depending on configuration; correctness relies on shared dependencies being thread-safe.

## Test Signals
Signals should cover each REST endpoint, null and non-null option bodies, required query validation for `src` and `dst`, stream ID creation, direct download headers, and error conversion for invalid or missing paths.
