<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServer.java

## Purpose
`HttpFSServer` is the Jersey REST resource that exposes the HttpFS/WebHDFS API under the service version path. It binds HTTP verbs plus the `op` query parameter to `FSOperations` executors, applies access-mode restrictions, performs user/file-system setup, handles upload/open redirects, and builds HTTP responses.

## Important APIs, Types, And Functions
The class is annotated `@Path(HttpFSFileSystem.SERVICE_VERSION)`. Public endpoints are `getRoot`, `get`, `delete`, `postRoot`, `post`, `putRoot`, and `put`. Helpers include `getHttpUGI`, `getParams`, `fsExecute`, `createFileSystem`, `enforceRootPath`, `makeAbsolute`, `createOpenRedirectionURL`, and `createUploadRedirectionURL`. `AccessMode` supports `READWRITE`, `WRITEONLY`, and `READONLY` via `httpfs.access.mode`.

## Control Flow
Each endpoint parses parameters through `HttpFSParametersProvider`, records MDC fields, normalizes paths, switches on `op.value()`, constructs an `FSOperations` command, and either calls `fsExecute` or uses an unmanaged `FileSystem` for streaming. GET handles read/status/list/instrumentation/snapshot/defaults/ec/block-location operations. DELETE handles delete and delete snapshot. POST handles append, concat, truncate, and unset policy operations. PUT handles create, mkdirs, rename, metadata mutation, ACL/xattr mutation, snapshots, storage policy, and EC policy changes. Upload operations use a two-step redirect/data flow controlled by `data` and `noredirect`; `OPEN` and checksum support `noredirect`.

## State And Persistence
Per-instance state is limited to `accessMode`; request state is held in local variables and MDC. Persistent effects occur through delegated filesystem operations. Streaming `OPEN` stores an unmanaged `FileSystem` in the release filter for cleanup after response completion.

## Dependencies And Integration Points
It integrates with Jersey, servlet requests, `HttpUserGroupInformation`, `UserGroupInformation`, `FileSystemAccess`, `Groups`, `Instrumentation`, `InputStreamEntity`, `HttpFSExceptionProvider`, `HttpFSParametersProvider`, `FSOperations`, audit logging, and the metrics accessed from executors.

## Risks
Some methods call `HttpUserGroupInformation.get()` directly rather than the fallback `getHttpUGI`, so deployments without that filter path need coverage. Access-mode restrictions are verb-level and GET write-only allows only status/list. Streaming `OPEN` catches `InterruptedException` but may continue with a null stream. Operation/parameter mismatches can surface as runtime failures. Admin-only instrumentation depends on group service accuracy.

## Test Signals
Tests should cover every verb switch case, invalid operation errors, read-only/write-only forbiddance, root-only operations, upload redirect/no-redirect/data modes, unmanaged filesystem release for open, admin group enforcement, audit MDC/logging, and JSON/content-type/status-code compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServer.java -->
