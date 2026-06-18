<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSParametersProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSParametersProvider.java

## Purpose
`HttpFSParametersProvider` defines the request parameter schema for every `HttpFSFileSystem.Operation`. It is the validation layer that tells the shared WSRS parameter framework which query parameters are accepted and how they are parsed.

## Important APIs, Types, And Functions
The class extends `ParametersProvider` and initializes `PARAMS_DEF`, mapping each operation to an ordered array of `Param` classes. Nested param types cover booleans (`data`, `noredirect`, `recursive`, `allusers`), longs/integers (`offset`, `length`, times, block size, new length, snapshot diff index), strings (`filter`, owner/group, destination, sources, xattr names/values, storage/snapshot/ec policy names), shorts (`permission`, `unmaskedpermission`, replication), enums (`OperationParam`, `XAttrEncodingParam`), enum sets (`XAttrSetFlagParam`), and validated strings (`FsActionParam`, ACL spec, xattr name).

## Control Flow
`HttpFSServer.getParams(request)` delegates to this provider. The provider reads the `op` query parameter, resolves it to `HttpFSFileSystem.Operation`, then instantiates only the params registered for that operation. Endpoint methods then retrieve typed values by name and class.

## State And Persistence
The static `PARAMS_DEF` map is process-wide immutable after class loading in practice, though it is a mutable `HashMap`. Parameter objects are request-scoped. No persistent state is written.

## Dependencies And Integration Points
It depends on `HttpFSFileSystem` constants and operation enum, `org.apache.hadoop.lib.wsrs` parameter classes, Hadoop xattr enums, HDFS ACL regex config, and `HttpFSServerWebApp.get().get(FileSystemAccess.class)` for the ACL permission pattern.

## Risks
Adding an operation in `HttpFSServer` or `HttpFSFileSystem.Operation` without updating `PARAMS_DEF` breaks request parsing. `AclPermissionParam` consults the singleton webapp at construction time; it requires the `FileSystemAccess` service to be initialized. Some params default to permissive values (`overwrite=true`, default permission, replication/block size `-1`) and endpoint behavior depends on those sentinels. `SnapshotDiffIndexParam` defaults to null while the executor expects an `int`, so invalid missing input would fail during unboxing.

## Test Signals
Tests should validate each operation's accepted parameter set, default values, invalid enum/action/xattr/ACL formats, ACL regex configuration wiring, and parity between switch cases in `HttpFSServer` and `PARAMS_DEF`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSParametersProvider.java -->
