# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AContractGetFileStatusV1List.java

Purpose: Runs the standard contract get-file-status suite against S3A while forcing the legacy List Objects V1 API. It ensures status resolution still works with older listing semantics and small paging.

Important APIs/types/functions: extends `AbstractContractGetFileStatusTest`, creates `S3AContract`, sets `Constants.LIST_VERSION` to `1`, and sets `Constants.MAX_PAGING_KEYS` to `2`. It uses `disableFilesystemCaching()`, `skipIfNotEnabled(KEY_LIST_V1_ENABLED)`, and `skipIfS3ExpressBucket()`.

Control flow: the inherited contract tests create files/directories and call `getFileStatus`; this class only specializes configuration and logs filesystem details during teardown.

State and persistence: test data is inherited from the contract suite and written to the live S3A test path. Filesystem caching is disabled to keep the configured V1 client isolated.

Dependencies and integration points: Hadoop contract tests, S3A contract binding, List Objects V1 compatibility, paging code, and S3 Express skip logic.

Risks: V1 listing can be unsupported or undesirable on newer stores; small page size raises iterator/pagination sensitivity; inherited tests can mask S3-specific assumptions unless configuration is isolated.

Test signals: proves `getFileStatus` contract behavior when the backing list API is V1 and listings span multiple pages.
