# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AFileSystem.java

## Purpose

`S3AFileSystem` is Hadoop's primary `FileSystem` implementation for the `s3a://` scheme. It translates Hadoop filesystem operations into S3 object, multipart upload, list, copy, and delete operations while layering in S3A-specific concerns such as request auditing, retry translation, change detection, delegation tokens, client-side encryption, directory markers, magic commit paths, IO statistics, and capability reporting.

## Important APIs, Types, and Functions

The class extends `FileSystem` and implements stream/capability interfaces. Public filesystem APIs include `initialize`, `open`, `openFileWithOptions`, `create`, `createFile`, `createNonRecursive`, `rename`, `delete`, `mkdirs`, `listStatus`, `listFiles`, `listLocatedStatus`, `getFileStatus`, `exists`, `isFile`, `isDirectory`, xattr/header accessors, checksum access, multipart uploader creation, bulk delete creation, delegation token methods, and `close`. Test/private integration APIs expose `getInstrumentation`, `getListing`, `getS3AInternals`, `getRequestFactory`, `createStoreContext`, `getInputPolicy`, `getChangeDetectionPolicy`, and write helpers.

Key internal collaborators are `S3AStore`, `ClientManager`, AWS SDK `S3Client`, `RequestFactory`, `Listing`, `S3AFileSystemOperations` variants for CSE/non-CSE behavior, `OpenFileSupport`, `S3AReadOpContext`, `WriteOperationHelper`, `MagicCommitIntegration`, `AuditManagerS3A`, `S3AInstrumentation`, `S3AStatisticsContext`, `ChangeDetectionPolicy`, `S3ADelegationTokens`, and operation classes such as `RenameOperation`, `DeleteOperation`, `MkdirOperation`, `GetContentSummaryOperation`, and `BulkDeleteOperation`.

## Control Flow

Initialization is a long staged setup. `initialize` derives the bucket, propagates bucket-specific configuration, handles access point ARNs, patches classloader and credential-provider settings, determines delegation-token support, sets the canonical URI, initializes instrumentation/statistics, builds encryption secrets, retry policy, CSE/analytics flags, filesystem operation handler, owner/working directory, paging and multipart settings, endpoint/region/FIPS/S3 Express flags, list version, conditional create, signer/audit service, request factory, client manager, input policy, change detection policy, magic committer integration, upload block factory, performance flags, listing/open-file helpers, store, S3 client, stream factory requirements, vector IO context, thread pools, bucket probe, and multipart upload purge. Failures during AWS SDK, IO, or runtime setup close created services and translate SDK failures.

Read flow starts in `open` or `openFileWithOptions`, which prepare `OpenFileInformation`, create input stream statistics and an audit span, fetch or validate file status, build a `S3AReadOpContext`, allocate a per-stream semaphored executor from the bounded thread pool, build `ObjectReadParameters`, and delegate actual stream construction to `S3AStore.readObject`.

Write flow goes through `create`/`createFile`/`createNonRecursive` into `innerCreateFile`. It rejects root writes, evaluates overwrite/performance/conditional-create/magic-path options, decides which HEAD/LIST probes are needed, constructs `PutTracker` and `PutObjectOptions`, validates output settings, and returns an `S3ABlockOutputStream` configured with block factory, multipart state, statistics, write helper, executor, CSE flag, and IO statistics aggregator. Append is explicitly unsupported.

Rename validates source/destination status with `initiateRename`, then executes `RenameOperation`, which implements S3 rename as copy plus delete and directory-marker fixup. Delete obtains status and executes `DeleteOperation`; on success it may recreate a parent directory marker. Listing uses the `Listing` helper to issue async/paged list requests, with fallbacks to status probes when a path may be a file or empty directory.

Status checks flow through `innerGetFileStatus` and `s3GetFileStatus`. The status algorithm first tries a HEAD for non-directory-marker keys when requested, then LISTs the slash-suffixed prefix to identify directory markers or child entries, returning file statuses, directory statuses with optional empty-directory state, root status, or `FileNotFoundException`.

Low-level S3 calls are wrapped with `Invoker`, duration tracking, statistics increments, and exception translation. `listObjects` and continuation pick V1 or V2 list APIs. `deleteObject`, `deleteObjects`, `putObject`, `putObjectDirect`, `uploadPart`, `copyFile`, multipart listing/abort, bucket metadata, and object metadata are routed through `S3AStore`, `S3Client`, or transfer manager as appropriate. `close` is one-shot and calls `stopAllServices` to close store, thread pools, delegation tokens, signer manager, audit manager, credentials, and instrumentation.

## State and Persistence Behavior

The class maintains per-filesystem in-memory state: URI, bucket/access point, working directory, owner/username, S3 store/client, credentials, request factory, retry invoker, thread pools, statistics, audit manager, listing helper, open-file helper, encryption secrets, multipart settings, performance flags, input policy, change detection policy, delegation tokens, magic committer integration, CSE and endpoint flags, and `deleteOnExit` paths. `closed` and `isClosed` gate lifecycle state.

Persistent data lives in S3 rather than in local metadata stores. Files are S3 objects; directories are inferred from prefixes and sometimes represented by zero-byte slash-suffixed directory markers. Creates and writes persist objects through PUT or multipart upload. Deletes remove objects in single or batch calls. Renames are non-atomic copy/delete sequences. Multipart uploads can persist as pending S3 state until completed or aborted. Delegation-token and credential state may influence authentication but is not stored by this class except through the token binding lifecycle.

## Dependencies and Integration Points

This class sits at the Hadoop/S3 boundary. It depends on Hadoop `FileSystem`, `Path`, `FileStatus`, `FSDataInputStream`, `FSDataOutputStream`, `BulkDelete`, `MultipartUploader`, audit/span APIs, IO statistics, retry annotations, security UGI/tokens, and common filesystem capability constants. It depends on AWS SDK v2 S3 models and clients for HEAD, LIST, PUT, COPY, DELETE, multipart, transfer manager, access point ARN, and bucket metadata operations.

Within S3A it integrates with `S3AStore`, `S3AStoreBuilder`, `S3AInputPolicy`, `S3AInputStream`/object stream factories, `S3ABlockOutputStream`, `S3ADataBlocks`, `RequestFactoryImpl`, `S3AUtils`, `S3xLoginHelper`, `ChangeTracker`, `ChangeDetectionPolicy`, `MagicCommitIntegration`, commit protocols, directory-marker tooling, multipart utilities, header processing, client factory abstractions, signer management, and CSE-specific filesystem operation implementations.

## Risks and Edge Cases

S3 renames and recursive deletes are not atomic and may leave partial results if copy/delete/list phases fail. Status and directory semantics depend on HEAD/LIST permissions and on marker/prefix interpretation; missing list permission can look different from missing object permission. Directory markers and parent-marker recreation can interact with concurrent writers and magic commit paths. Performance create flags skip safety probes and can trade correctness checks for fewer S3 calls. Conditional create requires the FS option to be enabled and can fail fast when unsupported.

Initialization has many partially constructed services, so cleanup ordering is critical. Access point ARNs alter bucket identity, endpoint, region, and list-version support. CSE changes available operations, active block count, object size interpretation, and multipart uploader support. S3 Express declares inconsistent directory listing capability. Bulk delete has page-size and partial-failure handling; `MultiObjectDeleteException` updates rejected-file metrics but callers still need to handle incomplete deletion. `getS3AInternals().getBucketLocation()` appears recursively routed in the no-argument implementation, so tests around that path should guard against accidental recursion. `setInputPolicy` is retained as a deprecated no-op, so callers expecting runtime filesystem-wide policy changes will not get them.

## Test Signals

High-value tests include initialization with normal bucket, access point ARN, required access point missing, delegation token enabled/disabled, CSE variants, FIPS/region/endpoint settings, list V1/V2 selection, S3 Express flagging, and bucket probe modes. Filesystem behavior tests should cover open with supplied status and without HEAD-skipping, open-file read policies, create overwrite/no-overwrite/performance/conditional-create modes, root create rejection, directory conflict detection, magic commit paths, append unsupported, rename file/directory/error cases, delete missing/nonrecursive/recursive cases, parent marker recreation, mkdirs on existing files and magic paths, status probes for file/directory/root/empty directory, and listing fallbacks.

Integration tests should assert AWS operation counters and IO statistics for PUT, multipart upload, copy, list, delete, and read/open. Failure tests should cover 404/403 bucket/object handling, multi-delete partial failures, request retry translation, change-detected copy failures, cleanup after initialization failure, close idempotence, delegation token issuance, `hasPathCapability` for CSE and conditional-create permutations, and xattr/checksum behavior under enabled and disabled configuration.
