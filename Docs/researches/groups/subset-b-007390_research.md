# subset-b-007390 research

This grouped report covers Hadoop `org.apache.hadoop.fs.contract` abstract contract tests and the `AbstractFSContract` base contract. Each section preserves the source path in its document title and is wrapped for deterministic split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractConcatTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractConcatTest.java

Purpose: `AbstractContractConcatTest` validates the Hadoop `FileSystem.concat(Path target, Path[] sources)` contract for filesystems that declare `SUPPORTS_CONCAT`. It is an abstract JUnit 5 test class extending `AbstractFSContractTestBase`, intended to be subclassed by concrete filesystem contract suites.

Important APIs and types: the class uses `Path`, `FileSystem.concat`, `CommonPathCapabilities.FS_CONCAT`, `ContractTestUtils.createFile`, `touch`, `dataset`, `assertFileHasLength`, `validateFileContent`, `readDataset`, and `LambdaTestUtils.intercept`. The test state is four paths prepared in `setup()`: `testPath`, `srcFile`, `zeroByteFile`, and `target`.

Control flow: `setup()` calls `super.setup()`, skips if concat is unsupported, builds a test directory, writes `srcFile` with `TEST_FILE_LEN` bytes, and creates an empty source. The tests then exercise invalid empty-source concat, missing target concat, valid file-on-file concat, self-concat rejection, and path-capability declaration. The valid concat case creates a target with the same dataset, concatenates `srcFile`, expects doubled length, and validates byte ordering as target block followed by source block.

State and persistence behavior: concat mutates the target file and should consume or move source data according to filesystem implementation semantics, but the test only asserts final target contents and length. It relies on the contract test base for test path isolation and cleanup.

Dependencies and integration points: this file integrates optional contract flags (`SUPPORTS_CONCAT`) with runtime capability probing (`FS_CONCAT`). It depends on relaxed exception handling in `AbstractFSContractTestBase.handleExpectedException()` so stores can normalize acceptable error behavior.

Risks: the test only validates one non-empty source and one zero-byte source in error cases; it does not assert whether source paths remain after concat. Filesystems with eventual consistency may need stronger post-concat stabilization in subclasses.

Test signals: pass means concat rejects empty source arrays, missing targets, and self-concat, preserves byte order for a simple append-style concat, and truthfully advertises `fs.concat` path capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractConcatTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractContentSummaryTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractContentSummaryTest.java

Purpose: `AbstractContractContentSummaryTest` checks `FileSystem.getContentSummary(Path)` behavior for a nested directory tree and for missing paths.

Important APIs and types: it uses `ContentSummary`, `FileSystem`, `Path`, AssertJ assertions, `ContractTestUtils.touch`, and `LambdaTestUtils.intercept`. It extends `AbstractFSContractTestBase` for filesystem selection and path construction.

Control flow: `testGetContentSummary()` creates `parent`, a nested `a/b/c` path, and a touched file below that nested path. It calls `fs.getContentSummary(parent)` and expects four directories and one file. `testGetContentSummaryIncorrectPath()` creates only `parent`, then requests a summary of missing `parent/a` and expects `FileNotFoundException`.

State and persistence behavior: the test builds a small persisted namespace under the contract test path. It verifies that summary traversal counts all directories under the queried parent, including the parent itself and nested descendants, while reporting exactly one file.

Dependencies and integration points: it depends on `mkdirs()` and `touch()` semantics being functional. It does not feature-gate content summaries, so concrete contract suites including this test are expected to provide an implementation of `getContentSummary`.

Risks: the nested file path is constructed through string concatenation (`path(nested + "file.txt")`), which depends on `Path.toString()` formatting and may produce a file name appended to the nested path string without an explicit separator. The expected directory count is tightly coupled to Hadoop `ContentSummary` semantics, including the queried directory.

Test signals: pass indicates content summary correctly recurses into nested directories, counts files and directories, and rejects nonexistent paths with `FileNotFoundException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractContentSummaryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractCopyFromLocalTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractCopyFromLocalTest.java

Purpose: `AbstractContractCopyFromLocalTest` validates `FileSystem.copyFromLocalFile()` behavior for local files and directories copied into the contract filesystem. It covers overwrite, delete-source, directory recursion, destination interpretation, and error handling.

Important APIs and types: the test uses local `java.io.File`, `java.nio.file.Files`, Apache Commons `FileUtils` and `IOUtils`, Hadoop `Path`, `FileSystem`, `FileStatus`, `PathExistsException`, and `FileAlreadyExistsException`. Helper methods include `copyFromLocal(File, overwrite, delSrc)`, `fileToPath()`, temp file and directory builders, and `assertFileTextEquals()`.

Control flow: each test creates temporary local sources, invokes a `copyFromLocalFile` overload, then validates remote existence and contents. File cases cover empty files, non-empty files, no-overwrite failure, overwrite success, missing source failure, and `delSrc=true`. Directory cases cover copying a file into an existing directory, copying to a nonexistent destination, copying non-empty and empty directories, directory overwrite options, delete-source for directories, nested directory trees, and failure when copying a directory onto an existing file.

State and persistence behavior: local temp files are cleaned in `teardown()` when tracked by the `file` field, while several directory tests create additional temp directories managed by the OS temp area. Remote filesystem state is written under paths derived from local file or directory names and validated through contract-base assertions.

Dependencies and integration points: it integrates local filesystem URIs (`new Path(file.toURI())`) with the target filesystem. It depends on `copyFromLocalFile` preserving file bytes, recursively copying directory trees, honoring overwrite and delete-source flags, and mapping a source directory relative to its local parent for expected destination paths.

Risks: temp directory cleanup is incomplete for every local helper-created directory, so repeated local test execution may leave OS temp artifacts. Destination expectations are path-name based and may differ for filesystems that normalize local names or reject certain URI forms. Directory overwrite behavior can vary across implementations, with `PathExistsException` and `FileAlreadyExistsException` used as expected signals.

Test signals: pass indicates reliable local-to-remote copy semantics for files, directories, trees, overwrite policy, deletion of local sources when requested, missing-source rejection, and file/directory collision handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractCopyFromLocalTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractCreateTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractCreateTest.java

Purpose: `AbstractContractCreateTest` is the main file-creation contract suite. It checks basic create, overwrite rules, directory collisions, visibility timing, block size reporting, automatic parent creation, parent-file rejection, and stream sync semantics.

Important APIs and types: it uses `FileSystem`, `Path`, `FSDataOutputStream`, `FSDataInputStream`, `FileStatus`, `FileAlreadyExistsException`, `ParentNotDirectoryException`, `StreamCapabilities`, and `TestAbortedException`. Key helpers are `writeDataset`, `writeTextFile`, `touch`, `getFileStatusEventually`, `assertCapabilities`, `validateSyncableSemantics()`, `expectCreateUnderFileFails()`, and `expectMkdirsUnderFileFails()`.

Control flow: paired helper methods run most create tests against both classic create and builder-based create paths by passing `useBuilder`. The suite writes datasets, verifies contents, attempts forbidden overwrites, checks directory preservation, waits for eventual file status, validates block sizes, creates parent trees, and probes parent-file errors. `testSyncable()` reads contract flags for `SUPPORTS_HFLUSH`, `SUPPORTS_HSYNC`, and `METADATA_UPDATED_ON_HSYNC`, then verifies stream capability declarations and actual hflush/hsync behavior.

State and persistence behavior: tests create real files and directories under method-specific contract paths. Visibility tests explicitly account for object store and delayed-visibility filesystems through `IS_BLOBSTORE` and `CREATE_VISIBILITY_DELAYED`. Sync tests write bytes before close, optionally open a separate reader during the write, and inspect metadata length when declared supported.

Dependencies and integration points: the file is tightly coupled to `ContractOptions` feature flags and `ContractTestUtils` dataset helpers. It integrates with stream capability APIs and IO statistics logging for output streams. The builder path exercises Hadoop's newer create-file builder indirectly through test utilities.

Risks: relaxed exception handling allows some implementations to pass with generic `IOException`, so precise exception conformance is not always enforced. Visibility and sync behavior are difficult for object stores and append-only backends; incorrect contract flag values can turn real bugs into skips or failures. `testOverwriteNonEmptyDirectory` contains explicit accommodation for filesystems that implement file/directory overlays.

Test signals: pass indicates create and overwrite semantics are coherent, parent directories are populated, creating under files is rejected unless explicitly supported, block sizes are plausible, visibility timing matches declared behavior, and syncable stream capabilities align with actual hflush/hsync effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractCreateTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractDeleteTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractDeleteTest.java

Purpose: `AbstractContractDeleteTest` validates delete semantics for files, empty directories, non-empty directories, deep paths, and nonexistent paths.

Important APIs and types: it uses Hadoop `Path`, `FileSystem.delete(Path, boolean)`, `ContractTestUtils.writeTextFile`, and assertion helpers from `AbstractFSContractTestBase` such as `assertDeleted`, `assertPathDoesNotExist`, `assertPathExists`, and `assertIsDirectory`.

Control flow: tests first construct filesystem state, then call delete with recursive or non-recursive flags. Empty directories must delete with either flag. Missing paths must return false for both recursive and non-recursive delete after `rejectRootOperation()` validates the path is not root. Non-empty directory non-recursive delete is expected to raise `IOException`; recursive delete must remove the directory and child. Deep-directory deletion removes the requested subtree while preserving its parent. File deletion removes a single file.

State and persistence behavior: all filesystem mutations are under contract-generated paths. The tests persist small text files to make directories non-empty and then verify post-delete namespace shape.

Dependencies and integration points: root operation rejection is delegated to `ContractTestUtils.rejectRootOperation()` to guard against accidental destructive tests. Expected exception processing is delegated to `handleExpectedException()`.

Risks: the tests require missing delete to return false rather than throw, which is Hadoop contract behavior but may need adapter logic for foreign stores. Non-recursive deletion of non-empty directories accepts only `IOException`, so implementations returning false may fail even if they preserve data.

Test signals: pass indicates delete returns correct booleans for nonexistent paths, enforces recursive requirements for non-empty directories, removes files and target subtrees, and does not delete ancestors unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractDeleteTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractEtagTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractEtagTest.java

Purpose: `AbstractContractEtagTest` validates etag exposure and consistency for filesystems that support etags through path capabilities.

Important APIs and types: it uses `EtagSource`, `FileStatus`, `LocatedFileStatus`, `FileSystem`, `Path`, `CommonPathCapabilities.ETAGS_AVAILABLE`, `ETAGS_PRESERVED_IN_RENAME`, AssertJ assertions, and AssertJ assumptions. The internal `etagFromStatus(FileStatus)` helper requires status objects to implement `EtagSource` and return a non-blank etag.

Control flow: `testEtagConsistencyAcrossListAndHead()` asserts `ETAGS_AVAILABLE`, touches a file, obtains the etag from `getFileStatus`, then lists the path and compares the listed status etag. `testEtagsOfDifferentDataDifferent()` writes one byte sequence, captures its etag, overwrites with same-length different data, and requires the etag to change. `testEtagConsistencyAcrossRename()` runs only when `ETAGS_PRESERVED_IN_RENAME` is true and checks rename does not change etag. `testLocatedStatusAlsoHasEtag()` verifies `listLocatedStatus()` and `listFiles()` return `LocatedFileStatus` entries with etags matching `getFileStatus`.

State and persistence behavior: tests create and overwrite short files and rename one file. Etag is treated as persistent object identity or content-version metadata depending on the capability under test.

Dependencies and integration points: the test integrates Hadoop path-capability probing, object metadata in `FileStatus`, and list APIs used by query planners. It depends on `ContractTestUtils.createFile` and `touch`.

Risks: etag semantics vary across filesystems. The same-length overwrite test prevents trivial length/path-only etags but may fail on stores with weak or delayed metadata refresh. Rename preservation is opt-in, so false capability declarations are the main risk.

Test signals: pass indicates etags are non-empty, exposed consistently across head/list/listFiles/listLocatedStatus, change when content changes, and are preserved across rename only when the filesystem declares that behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractEtagTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractGetEnclosingRoot.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractGetEnclosingRoot.java

Purpose: `AbstractContractGetEnclosingRoot` validates `FileSystem.getEnclosingRoot(Path)` for ordinary paths, existing paths, missing paths, and wrapped filesystem access under another user context.

Important APIs and types: it uses `FileSystem`, `Path`, `UserGroupInformation`, `PrivilegedExceptionAction`, JUnit assertions, and SLF4J logging. It extends `AbstractFSContractTestBase`.

Control flow: `testEnclosingRootEquivalence()` compares results for `/foo/bar`, `/`, `methodPath()`, and repeated `getEnclosingRoot()` calls, expecting all to resolve to `/`. `testEnclosingRootPathExists()` creates a method path and still expects root. `testEnclosingRootPathDNE()` checks missing absolute and method paths. `testEnclosingRootWrapped()` checks direct access and access from `UserGroupInformation.doAs()` using a freshly obtained test filesystem.

State and persistence behavior: only one test creates a directory. The API is expected to be metadata-derived or path-derived and should not require target path existence.

Dependencies and integration points: this test integrates filesystem root resolution with Hadoop security wrappers. It specifically checks that a wrapped filesystem obtained inside a remote-user `doAs` block returns the same root path as the original filesystem.

Risks: the class assumes a single root at `/`. Filesystems with mount-table semantics, viewfs-style nested roots, or bucket-root distinctions may need subclasses or contract settings not represented here. The logger is declared but not used.

Test signals: pass indicates `getEnclosingRoot()` is idempotent, existence-independent, stable across paths under the same root, and preserved when filesystem access occurs through UGI wrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractGetEnclosingRoot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractGetFileStatusTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractGetFileStatusTest.java

Purpose: `AbstractContractGetFileStatusTest` is the central listing/status contract suite. It validates `getFileStatus`, `listStatus`, `listStatusIterator`, `listLocatedStatus`, `listFiles`, filtering, iterator behavior, and metadata consistency.

Important APIs and types: it uses `FileStatus`, `LocatedFileStatus`, `RemoteIterator`, `FilterFileSystem`, `PathFilter`, `TreeScanResults`, and many `ContractTestUtils` helpers. Constants define a small generated tree: depth 2, width 3, four files per directory, 512 byte files.

Control flow: `setup()` skips if `SUPPORTS_GETFILESTATUS` is absent. Basic tests cover missing status, root status, empty directory listings, and missing path errors for every listing API. `testComplexDirActions()` creates a test tree once, then checks non-recursive `listStatus`, `listStatusIterator`, `listLocatedStatus`, non-recursive `listFiles`, and recursive `listFiles`. It compares listings with generated tree data and tree walks. Iterator tests consume iterators both with ordinary `hasNext()/next()` and through `next()` calls alone. File-as-input tests confirm listing a file returns a single file entry. Filtering tests validate `PathFilter` behavior on directories, files, and empty directories.

State and persistence behavior: helper methods delete and recreate the contract test root, generate random subfolder names for empty directory tests, and create a deterministic nested tree for complex listings. No durable state beyond test artifacts is intended.

Dependencies and integration points: the file depends heavily on `ContractTestUtils.TreeScanResults` for comparing file and directory sets. `ExtendedFilterFS` exposes protected `listLocatedStatus(Path, PathFilter)` so the filter path is tested through the standard `FilterFileSystem` layer.

Risks: object stores with eventual listing consistency may fail unless their contract layer stabilizes results. Iterator implementations that require `hasNext()` before `next()` are explicitly caught. Owner comparisons in `verifyFileStats()` may expose inconsistent listing metadata even when paths and lengths are correct.

Test signals: pass indicates status calls throw expected missing-path exceptions, root is a directory, listing APIs agree on directory and file contents, iterator contracts are robust, recursive file listing matches tree walk, filters are honored, and located statuses match direct file statuses for core fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractGetFileStatusTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractLeaseRecoveryTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractLeaseRecoveryTest.java

Purpose: `AbstractContractLeaseRecoveryTest` validates the `LeaseRecoverable` interface and `LEASE_RECOVERABLE` path capability.

Important APIs and types: it uses `FileSystem`, `Path`, `LeaseRecoverable`, `CommonPathCapabilities.LEASE_RECOVERABLE`, AssertJ assertions, `ContractTestUtils.touch`, and `LambdaTestUtils.intercept`.

Control flow: `testLeaseRecovery()` touches a file, verifies the filesystem both advertises `LEASE_RECOVERABLE` for the path and implements `LeaseRecoverable`, then calls `recoverLease(path)` and `isFileClosed(path)`, expecting both to return true for a closed file. `testLeaseRecoveryFileNotExist()` uses a missing relative path and expects `FileNotFoundException` with "File does not exist" from both methods. `testLeaseRecoveryFileOnDirectory()` uses the parent directory of a method path and expects `FileNotFoundException` with "Path is not a file".

State and persistence behavior: one test creates an empty file. The tests do not leave open leases; they verify behavior against already-closed files, missing paths, and directories.

Dependencies and integration points: it bridges path capabilities and Java interface availability; an implementation must not merely declare the capability but also implement `LeaseRecoverable`.

Risks: expected exception messages are asserted, which can make compatible implementations fail on wording differences. The missing path is `new Path("notExist")`, not built through `path()`, so qualification is filesystem-dependent.

Test signals: pass indicates lease recovery can be invoked safely on closed files, reports closed status, rejects missing files and directories as files, and keeps path capability declarations consistent with implemented interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractLeaseRecoveryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractMkdirTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractMkdirTest.java

Purpose: `AbstractContractMkdirTest` validates `FileSystem.mkdirs()` and directory creation semantics.

Important APIs and types: it uses `FileSystem`, `Path`, `FileAlreadyExistsException`, `ParentNotDirectoryException`, `ContractTestUtils.assertMkdirs`, `createFile`, `dataset`, and base assertions. The public constant `MKDIRS_NOT_FAILED_OVER_FILE` is used in failure messages.

Control flow: simple tests create and delete directories recursively and non-recursively. Negative tests create a file at the target or as a parent, call `mkdirs()`, and expect `FileAlreadyExistsException`, `ParentNotDirectoryException`, or a relaxed `IOException`; they then verify the original file content survived. Slash handling tests create paths with and without trailing slashes, qualified and unqualified, including multiple trailing slashes. Ancestor tests verify `mkdirs()` populates all nonexistent ancestors and does not remove existing parent directories during repeated nested calls. The final test confirms `mkdirs()` is idempotent on an existing directory.

State and persistence behavior: tests create directories and small files under contract paths and verify directory hierarchy preservation after creation calls. File-content validation ensures failed `mkdirs()` does not corrupt existing file data.

Dependencies and integration points: behavior is checked through direct `FileSystem.mkdirs()` and through `ContractTestUtils.assertMkdirs()`. The tests depend on `Path` normalization for trailing slash handling.

Risks: filesystems with object-store marker behavior may simulate directories lazily, so ancestor existence and listing semantics must be coherent. Some implementations may return false rather than throw on file collisions, which this contract treats as failure.

Test signals: pass indicates directory creation is idempotent, creates all ancestors, handles trailing slashes, rejects file collisions without corruption, and preserves parent directories across nested `mkdirs()` operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractMkdirTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractMultipartUploaderTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractMultipartUploaderTest.java

Purpose: `AbstractContractMultipartUploaderTest` validates Hadoop `MultipartUploader` implementations: starting uploads, putting parts, completing, aborting, concurrent upload policy, invalid handles, and path capabilities.

Important APIs and types: it uses `MultipartUploader`, `UploadHandle`, `PartHandle`, `PathHandle`, `BBUploadHandle`, `FileSystem.createMultipartUploader()`, `CommonPathCapabilities.FS_MULTIPART_UPLOADER`, `CompletableFuture`, MD5 `MessageDigest`, `DurationInfo`, and `FutureIO.awaitFuture`. Subclasses must implement `partSizeInBytes()`, `finalizeConsumesUploadIdImmediately()`, and `supportsConcurrentUploadsToSamePath()`, and may override payload count or consistency delay.

Control flow: `setup()` assumes multipart upload capability and creates two uploader instances. `teardown()` aborts any active upload, aborts all uploads under the test path, logs statistics, closes uploaders, and delegates to the base teardown. Helpers generate deterministic payloads from part numbers, upload parts with alternating uploaders, complete with random or specified uploaders, validate file length and MD5 digest, and abort uploads. Tests cover single-part upload, multipart upload, empty parts and empty blocks, reverse-order and non-contiguous part maps, abort behavior, abort-all-under-path, invalid empty handles, complete with no parts, invalid upload IDs, directory collision at completion, concurrent uploads to the same path, and capability declaration.

State and persistence behavior: uploads create pending remote state before completion. `activeUpload` and `activeUploadPath` are tracked so teardown can abort leftovers. Completed uploads are validated through file status length and full-file digest. Concurrent upload tests may wait for eventual consistency before validating the second completed upload.

Dependencies and integration points: this file integrates async uploader APIs with the synchronous test suite through `awaitFuture`. It relies on `ContractTestUtils.verifyPathExists`, base path assertions, Apache Commons digest/IO helpers, and per-filesystem subclass policy hooks.

Risks: random uploader selection can expose cross-uploader bugs but can also make intermittent failures harder to reproduce. MD5 validation reads whole uploaded files into memory, acceptable for contract-sized payloads but not scalable. The contract allows different finalization models, so subclass hook accuracy is critical. Eventual consistency delays must be tuned by concrete filesystem tests.

Test signals: pass indicates multipart upload supports deterministic assembly by part number, cross-uploader completion where expected, empty data handling, robust abort and invalid-handle rejection, no file creation after abort, directory collision failure, declared concurrency behavior, and `FS_MULTIPART_UPLOADER` path capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractMultipartUploaderTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractOpenTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractOpenTest.java

Purpose: `AbstractContractOpenTest` validates classic `FileSystem.open()` and async builder-based `openFile()` semantics, plus input stream argument validation and EOF behavior.

Important APIs and types: it uses `FSDataInputStream`, `FutureDataInputStreamBuilder`, `CompletableFuture`, `FileStatus`, `FileSystem`, `Path`, `Options.OpenFileOptions`, `FutureIO.awaitFuture`, and `LambdaTestUtils.interceptFuture`. It sets `io.file.buffer.size` to 4096 in `createConfiguration()`.

Control flow: classic tests open zero-byte files, reject opening directories, ensure two streams over the same file have independent positions, and verify sequential single-byte reads. Builder tests validate unknown `must()` options fail at build, missing file failures surface through futures, `exceptionally()` chains behave as expected, `awaitFuture()` unwraps IOExceptions, and callback chains can read full files. More builder tests pass file status, bogus status paths, null status plus length/read-policy options, floating-point length options, and unknown optional values. Input stream tests assert null buffers, negative offsets, negative lengths, too-long reads, zero-length reads, consistent EOF, and equivalence of single-byte and multi-byte reads.

State and persistence behavior: tests create small deterministic files and directories under contract paths. `instream` is closed in `teardown()` to prevent leaked streams after failure.

Dependencies and integration points: the file integrates Hadoop functional future helpers, open-file option parsing, FileStatus hints, stream read utilities, and base contract cleanup. `areZeroByteFilesEncrypted()` is a protected hook for encrypted filesystems.

Risks: some exceptions are intentionally broad to accommodate legacy stream behavior. Future timing is important: some tests require missing-file errors to occur after `build()`, not during option setup. Implementations must ignore bogus status path values and use the path passed to `openFile()`.

Test signals: pass indicates open rejects directories, reads files consistently, supports independent streams, implements async open-file contracts and option validation, unwraps future failures properly, and honors Java input stream boundary checks and EOF conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractOpenTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractPathHandleTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractPathHandleTest.java

Purpose: `AbstractContractPathHandleTest` validates `PathHandle` creation and open semantics across different `HandleOpt` policies for content changes and path/location changes.

Important APIs and types: it uses `PathHandle`, `RawPathHandle`, `HandleOpt`, `InvalidPathHandleException`, `FileStatus`, `FSDataInputStream`, `CompletableFuture`, `FileSystem.getPathHandle()`, `FileSystem.open(PathHandle)`, and `FileSystem.openFile(PathHandle)`. It is parameterized over `exact`, `content`, `path`, and `reference` options, each with serialized and non-serialized handle use.

Control flow: `params()` creates the option matrix. `initAbstractContractPathHandleTest()` stores options and serialization mode. `testIdent()` gets a handle for an unchanged file and reads original bytes. `testChanged()` appends data after the original status and expects open to either allow changed content or throw `InvalidPathHandleException` according to `HandleOpt.Data`. `testMoved()` renames after status capture and checks `HandleOpt.Location`. `testChangedAndMoved()` combines rename and append. Additional tests open handles through `openFile().build().thenApply(readStream)`, delete the target before async open and accept `FileNotFoundException` or `InvalidPathHandleException`, and verify successful lazy open for existing handles.

State and persistence behavior: each test creates a method-named file with deterministic bytes. Some tests append, rename, or delete the target after acquiring status or handle, then validate whether the handle remains valid. Serialization is simulated by converting handle bytes into `RawPathHandle`.

Dependencies and integration points: the file uses contract flags `SUPPORTS_FILE_REFERENCE` and `SUPPORTS_CONTENT_CHECK` as skip gates. It relies on append and rename utilities and on the target filesystem implementing handle option semantics precisely.

Risks: a one-second sleep works around second-precision timestamps in raw local filesystems, but timing-based content checks remain sensitive. Support for content and reference validation is optional, so coverage depends on concrete contract settings.

Test signals: pass indicates path handles can reopen stable files, serialized handles round-trip, content and location change policies are enforced, async open by handle behaves like path open, and deleted targets fail lazily with a recognized exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractPathHandleTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractRenameTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractRenameTest.java

Purpose: `AbstractContractRenameTest` validates file and directory rename semantics, including missing sources, destination collisions, directory moves, parent creation policy, and attempts to rename under a file.

Important APIs and types: it uses `FileSystem`, `Path`, `FileAlreadyExistsException`, `FileNotFoundException`, `ContractOptions` flags, and `ContractTestUtils` helpers such as `rename`, `writeDataset`, `writeTextFile`, `verifyFileContents`, `rm`, and `dataset`.

Control flow: positive tests rename a file in the same directory, rename an empty directory, rename a directory into an existing directory, and move nested directory/file ancestor trees. Missing-source behavior is controlled by `RENAME_RETURNS_FALSE_IF_SOURCE_MISSING`. File-over-file behavior is controlled by `RENAME_OVERWRITES_DEST` and `RENAME_RETURNS_FALSE_IF_DEST_EXISTS`, which are asserted mutually exclusive. Rename into nonexistent directory follows `RENAME_CREATES_DEST_DIRS`. Rename of non-empty source into existing destination accepts either POSIX replacement (`RENAME_REMOVE_DEST_IF_EMPTY_DIR`) or CLI-style nesting. Negative tests attempt to rename into a direct child or descendant of a path that is actually a file.

State and persistence behavior: tests write deterministic source and destination data and validate final byte content to distinguish overwrite from rejection. Directory tests verify both source removal and destination ancestor creation.

Dependencies and integration points: the suite relies heavily on contract flags to encode acceptable semantic variation across HDFS, local, object store, and CLI-like stores. It also depends on listing diagnostics from `generateAndLogErrorListing()` on unexpected outcomes.

Risks: rename behavior is one of the most variable filesystem surfaces; incorrect contract flag values can either fail valid stores or hide nonconformance. Some tests do not explicitly assert the boolean result of raw `fs.rename()` calls in ancestor cases.

Test signals: pass indicates rename preserves data, handles destination conflicts as declared, moves directories and nested ancestors correctly, rejects paths under files, removes sources, and does not silently create wrong destinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractRenameTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractRootDirectoryTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractRootDirectoryTest.java

Purpose: `AbstractContractRootDirectoryTest` exercises dangerous operations against `/`, gated by `TEST_ROOT_TESTS_ENABLED`, and is annotated `@RootFilesystemTest` to signal that it should only be used on transient filesystems.

Important APIs and types: it uses `FileSystem`, `Path`, `FileStatus`, `LocatedFileStatus`, `RemoteIterator`, AssertJ, `LambdaTestUtils.eventually`, and root-focused `ContractTestUtils` helpers such as `deleteChildren`, `listChildren`, `treeWalk`, `dumpStats`, and `assertDeleted`.

Control flow: `setup()` skips unless root tests are enabled. Tests create `/testmkdirdepth1`, attempt recursive and non-recursive deletion of an empty root, attempt non-recursive deletion of a non-empty root, attempt recursive deletion of a root containing a file, reject creating a file over root, list an emptied root, compare simple root listings across `listStatus`, `listLocatedStatus`, `listFiles`, and `listStatusIterator`, and compare recursive root `listFiles` with a tree walk.

State and persistence behavior: this class deliberately mutates root-level namespace state. Non-recursive empty-root cleanup uses retry logic to remove children and tolerate object-store listing lag before deleting root. Tests always assert root remains a directory and clean up created files in `finally` where applicable.

Dependencies and integration points: root behavior depends on filesystem-specific policy; some stores may allow recursive root delete to remove children while others preserve them. The class integrates with test tags to separate high-risk root tests from ordinary contract tests.

Risks: data-loss risk is explicit; this class must never run against a valuable filesystem. Object stores can expose stale children after deletion, hence `OBJECTSTORE_RETRY_TIMEOUT`. Root listing comparisons may be expensive or unstable on large shared roots.

Test signals: pass indicates root remains a directory after delete/create attempts, non-recursive deletion protects non-empty root, root listing APIs are mutually consistent, recursive file listings match tree walk, and root-level cleanup behaves according to contract expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractRootDirectoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSafeModeTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSafeModeTest.java

Purpose: `AbstractContractSafeModeTest` validates the `SafeMode` interface on filesystems that include safe mode controls.

Important APIs and types: it uses `FileSystem`, `SafeMode`, `SafeModeAction`, and AssertJ. The private helper `verifyAndGetSafeModeInstance(FileSystem)` asserts the filesystem implements `SafeMode` and casts it.

Control flow: `testSafeMode()` obtains the test filesystem, verifies interface support, then calls `setSafeMode(GET)`, `ENTER`, `GET`, `LEAVE`, and `FORCE_EXIT`. It expects initial `GET` false, `ENTER` true, subsequent `GET` true, `LEAVE` false, and `FORCE_EXIT` false.

State and persistence behavior: the test mutates filesystem safe mode state and must return it to off through `LEAVE` and `FORCE_EXIT`. It does not create files or directories.

Dependencies and integration points: it checks interface implementation rather than path capability or contract feature flags. Concrete tests should include it only for filesystems where safe mode is supported and safe to toggle in tests.

Risks: there is no `try/finally` around safe mode transitions, so an assertion failure after `ENTER` could leave safe mode enabled until teardown or external cleanup. The assertion description uses `SafeMode.class.getClass()` in the message, which prints `Class` rather than the interface class, but does not affect behavior.

Test signals: pass indicates the filesystem implements `SafeMode` and its state transitions return the expected boolean state for get, enter, leave, and force-exit actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSafeModeTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSeekTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSeekTest.java

Purpose: `AbstractContractSeekTest` validates seeking, positioned reads, readFully semantics, EOF behavior, and closed-stream behavior for filesystems declaring `SUPPORTS_SEEK`.

Important APIs and types: it uses `FSDataInputStream`, `FileSystem`, `Path`, `EOFException`, `Configuration`, `CommonConfigurationKeysPublic.IO_FILE_BUFFER_SIZE_KEY`, `ContractOptions`, and `ContractTestUtils.verifyRead`. Test files include a deterministic `smallSeekFile` and a zero-byte file.

Control flow: `setup()` gates on seek support, creates the deterministic data file and zero-byte file, and configures a 4096 byte IO buffer. Tests cover zero-byte reads, block reads, operations after close, negative seek, ordinary seeks, reading past EOF, seeking past EOF then recovery, large-file seeks beyond buffer boundaries, positioned reads that must not change stream position, randomized seek/read sequences, readFully on zero-byte and small files, invalid offsets and lengths, reads past EOF, null buffers, and reading exactly at EOF.

State and persistence behavior: tests create deterministic files whose byte value equals offset modulo the dataset range, enabling direct validation after seek. `instream` is closed in teardown.

Dependencies and integration points: `assumeSupportsPositionedReadable()` uses `SUPPORTS_POSITIONED_READABLE`, defaulting true when seek is supported. Contract flags also control seek-on-closed, available-on-closed, and seek-past-EOF behavior. Random seek count is controlled by `TEST_RANDOM_SEEK_COUNT`.

Risks: `testRandomSeeks()` uses an unseeded `Random`, so reproducing failures requires the logged last ten seek/read pairs rather than a seed. Relaxed exception handling accepts several exception classes for invalid positioned reads because implementations differ. Closed-stream capabilities are explicitly variable.

Test signals: pass indicates seek positions are accurate, data read after seeks is correct, positioned reads preserve current position, EOF and invalid-argument behavior is coherent, streams recover after past-EOF seeks where allowed, and random seek/read sequences do not expose buffering bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSeekTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSetTimesTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSetTimesTest.java

Purpose: `AbstractContractSetTimesTest` validates `FileSystem.setTimes(Path, mtime, atime)` behavior for missing files when the filesystem declares `SUPPORTS_SETTIMES`.

Important APIs and types: it uses `Path`, `FileNotFoundException`, JUnit, SLF4J, and the base contract methods `skipIfUnsupported()` and `handleExpectedException()`.

Control flow: `setup()` calls the base setup, skips unsupported filesystems, and initializes `testPath` and `target`. `testSetTimesNonexistentFile()` calls `setTimes()` on the missing target with current time for both modification and access time. Reaching normal completion fails the test; `FileNotFoundException` is expected.

State and persistence behavior: no file is created. The test verifies that `setTimes()` does not create missing paths as a side effect.

Dependencies and integration points: this is a focused feature-gated contract test. It depends on concrete filesystems setting `SUPPORTS_SETTIMES` only when the API is implemented.

Risks: the class only tests the negative missing-file case, not successful timestamp updates on files or directories. The logger and `testPath` field are not substantively used beyond path construction.

Test signals: pass indicates `setTimes()` on a nonexistent file fails with `FileNotFoundException` and does not silently create or ignore missing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSetTimesTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractStreamIOStatisticsTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractStreamIOStatisticsTest.java

Purpose: `AbstractContractStreamIOStatisticsTest` validates `IOStatistics` support on filesystem input and output streams, especially byte counters for reads and writes.

Important APIs and types: it uses `IOStatistics`, `IOStatisticsSnapshot`, `IOStatisticsSource`, `FSDataInputStream`, `FSDataOutputStream`, `STREAM_READ_BYTES`, `STREAM_WRITE_BYTES`, and assertion helpers from `IOStatisticAssertions`. Hooks include `streamWritesInBlocks()`, `readBufferSize()`, `outputStreamStatisticKeys()`, and `inputStreamStatisticKeys()`.

Control flow: `teardown()` aggregates filesystem-level statistics into a static snapshot when the filesystem implements `IOStatisticsSource`; `@AfterAll` logs aggregate stats if non-empty. Output tests verify required statistic keys, single-byte write counters before write, after write, and after close, and byte-array write counters including stringified stats. Input tests verify required keys and read byte counters across single-byte reads, buffer reads, `readFully`, positioned reads, seeks, lazy-seek reads, and EOF-adjacent reads for unbuffered streams.

State and persistence behavior: each test creates and deletes method-path files. Stream statistics must remain queryable after stream close. The static snapshot persists across test methods for final aggregate logging only.

Dependencies and integration points: the file integrates stream statistics extraction, logging support, and concrete stream buffering policy via overridable hooks. It assumes streams expose at least read/write byte counters.

Risks: buffered input streams count bytes at buffer granularity, so `readBufferSize()` must be correctly overridden by concrete tests or expected counters will be wrong. For block-writing streams, in-progress write counters may stay zero until close, controlled by `streamWritesInBlocks()`.

Test signals: pass indicates stream statistics expose required keys, counters start at zero, byte counters advance according to explicit or buffered IO policy, counters remain available after close, seeks do not count as reads, and filesystem aggregate statistics can be harvested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractStreamIOStatisticsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractUnbufferTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractUnbufferTest.java

Purpose: `AbstractContractUnbufferTest` validates `FSDataInputStream.unbuffer()` behavior for filesystems declaring `SUPPORTS_UNBUFFER`.

Important APIs and types: it uses `FSDataInputStream`, `Path`, AssertJ, `ContractTestUtils.createFile`, `dataset`, and `readNBytes`. The class is annotated `@FlakyTest("buffer underflow")`, acknowledging that some valid `InputStream.read(byte[])` implementations may return fewer bytes than requested.

Control flow: `setup()` creates a deterministic file and byte array after skipping unsupported filesystems. Tests call `unbuffer()` after full reads, before reads, on empty files, after stream close, repeatedly, and between multiple partial reads. The private `unbuffer()` helper captures `getPos()`, calls `stream.unbuffer()`, and asserts the position is unchanged. Content validation reads expected byte ranges and compares against the original dataset.

State and persistence behavior: the main file and an empty file are created under contract paths. The stream's logical position is the critical mutable state; unbuffering must release internal buffers without changing position or corrupting later reads.

Dependencies and integration points: this file exercises the `CanUnbuffer` behavior exposed through `FSDataInputStream`. It depends on accurate `getPos()` and deterministic file content from `ContractTestUtils`.

Risks: tests assume `readNBytes()` can retrieve the exact requested length in one validation step; the class-level flaky annotation documents risk from short reads. Calling unbuffer on a closed stream is expected not to fail, which may be stricter than some implementations.

Test signals: pass indicates unbuffer can be called before reads, after reads, on empty or closed streams, and multiple times without changing position or breaking subsequent reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractUnbufferTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractVectoredReadTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractVectoredReadTest.java

Purpose: `AbstractContractVectoredReadTest` validates `FSDataInputStream.readVectored()` for both heap and direct buffers, including range validation, EOF behavior, buffer release semantics, interoperation with normal reads, and async result handling.

Important APIs and types: it uses `FileRange`, `FSDataInputStream`, `ByteBuffer`, `ElasticByteBufferPool`, `WeakReferencedElasticByteBufferPool`, `TrackingByteBufferPool`, `CompletableFuture`, `CountDownLatch`, and `HadoopExecutors`. It is parameterized by buffer type through `@ParameterizedClass` and `params()`. It uses open-file options `FS_OPTION_OPENFILE_LENGTH` and vector read policy.

Control flow: `setup()` writes a 128 KiB vector file. `openVectorFile()` opens it through `openFile()` with vector read policy. Tests read multiple ranges, whole files, disjoint and mergeable ranges, overlapping and same ranges according to `VECTOR_IO_OVERLAPPING_RANGES`, null range inputs, random non-overlapping ranges, consecutive ranges, empty range lists, EOF ranges with early or late failure according to `VECTOR_IO_EARLY_EOF_CHECK`, invalid negative length or offset, null release callbacks, normal read before/after vectored read, multiple vectored reads, and end-to-end async processing in a separate thread pool. `testBufferSlicing()` verifies whether returned buffers are from the pool or sliced according to `VECTOREDIO_BUFFERS_SLICED`.

State and persistence behavior: the dataset is static and deterministic. Buffer pool state is released in teardown, and many tests explicitly return buffers after validation. `bufferReleases` tracks release callback calls but is not asserted because implementations vary on failure cleanup.

Dependencies and integration points: this test suite integrates vectored IO, `openFile()` policy hints, stream capabilities, buffer pool ownership, async future completion, and contract flags controlling overlap and EOF timing.

Risks: asynchronous tests depend on timeout constants and correct executor shutdown. Buffer ownership is subtle when implementations slice larger buffers. Not all implementations release buffers on failure, so leak detection is intentionally limited.

Test signals: pass indicates vectored read returns exact requested bytes for many range layouts, rejects invalid input, reports EOF at the declared time, coexists with normal reads, completes futures reliably, handles direct and heap buffers, and accurately advertises sliced-buffer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractVectoredReadTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractFSContract.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractFSContract.java

Purpose: `AbstractFSContract` is the abstract configuration and capability model behind Hadoop filesystem contract tests. Concrete contract classes subclass it to provide the filesystem under test, scheme, and root test path.

Important APIs and types: it extends `Configured` and uses `Configuration`, `FileSystem`, `Path`, `URI`, `URL`, `ContractOptions`, and SLF4J. Abstract methods are `getTestFileSystem()`, `getScheme()`, and `getTestPath()`. Public helpers include `init()`, `teardown()`, `getFileSystem(URI)`, `isEnabled()`, `setEnabled()`, `isSupported()`, `getLimit()`, `getOption()`, and `getConfKey()`.

Control flow: the constructor stores the configuration and tries to load `ContractOptions.CONTRACT_OPTIONS_RESOURCE` through `maybeAddConfResource()`, logging whether it was found. `init()` and `teardown()` are no-ops for subclasses to override. `addConfResource()` asserts a named resource exists, while `maybeAddConfResource()` probes the classloader and adds the resource to the configuration if present. `getFileSystem(URI)` delegates to the standard `FileSystem.get(uri, conf)` factory. Feature and limit lookups build keys by appending a feature string to `ContractOptions.FS_CONTRACT_KEY`. `toURI()` constructs a URI from the contract scheme and path.

State and persistence behavior: persistent state is limited to the inherited `Configuration` and the mutable boolean `enabled`. Configuration resources and options determine which contract tests run and how they interpret filesystem-specific behavior.

Dependencies and integration points: every abstract contract test uses this class indirectly through `AbstractFSContractTestBase` to decide feature support, limits, test root, and filesystem instance. It is the bridge between concrete filesystems and generic contract tests.

Risks: `enabled` is a simple mutable flag without synchronization, which is fine for ordinary JUnit lifecycle but not a concurrent control plane. `toURI()` uses `new URI(getScheme(), path, null)`, so unusual schemes or path formats may need subclass care. A comment contains a typo ("norrmal") but no behavior issue.

Test signals: this is infrastructure, not a test. Correct behavior is evidenced by concrete contract suites being able to load optional resources, query feature flags and limits, construct test paths, and obtain configured filesystem instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractFSContract.java -->
