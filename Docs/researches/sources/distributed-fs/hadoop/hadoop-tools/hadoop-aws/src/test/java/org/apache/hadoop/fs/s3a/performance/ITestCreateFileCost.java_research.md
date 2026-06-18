# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestCreateFileCost.java

Purpose: parameterized integration cost tests for S3A create paths with `fs.s3a.create.performance` disabled and enabled. It validates legacy `create`, `createFile`, builder `must()` options, recursive/nonrecursive creation, overwrite behavior, custom create headers exposed as xattrs, and the intentional safety tradeoff of performance creation.

Important APIs/types/functions: `ITestCreateFileCost` extends `AbstractS3ACostTest`; `params()` runs `{false,true}`; `expected()` maps normal `OperationCost` expectations to `NO_HEAD_OR_LIST` under the performance flag; tests call `create`, `file`, `buildFile`, `verifyMetrics`, `interceptOperation`, and raw `S3AFileSystem` builders. It checks `OBJECT_BULK_DELETE_REQUEST`, `OBJECT_DELETE_REQUEST`, `FS_S3A_CREATE_HEADER`, `FS_S3A_CREATE_PERFORMANCE`, `FS_S3A_CONDITIONAL_CREATE_ENABLED`, and `RemoteFileChangedException`.

Control flow: setup disables filesystem caching and toggles performance flags. Each test constructs an isolated method path, performs one create variant, then verifies HEAD/LIST/delete metrics or expected exceptions. The final invalid-store test creates a child beneath a path, writes a file over that parent with performance mode, verifies both objects coexist, then repairs state in `finally`.

State and persistence: creates and deletes real S3A objects and directory markers; custom headers persist as object metadata/xattrs. Performance mode can produce an ill-formed namespace where a path is both file and parent prefix.

Dependencies/integration: S3A create builder, contract utilities, cost constants, S3A instrumentation, conditional create support, and object metadata headers.

Risks: expected request costs vary with conditional-create availability and third-party stores; performance mode deliberately skips safety checks; failed cleanup can leave inconsistent test data.

Test signals: success is exact counter diffs, expected `FileAlreadyExistsException`/`RemoteFileChangedException`, progress callback activity, xattr header equality, and final namespace assertions.
