# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsWithAuthorityLocalFs.java

Purpose: concrete `ViewFsBaseTest` subclass that uses an authority-bearing URI, `viewfs://mycluster/`, for `FileContext` tests. It validates authority-selected mount table behavior for `ViewFs`.

Important APIs and types: `ViewFsBaseTest`, `FileContext.getFileContext(URI, conf)`, `FsConstants.VIEWFS_SCHEME`, `MOUNT_TABLE_NAME`, and `Path.makeQualified`.

Control flow: setup assigns local `fcTarget`, invokes base setup to populate a config whose default mount table name is `mycluster`, builds `schemeWithAuthority`, and replaces `fcView` with a context opened on that URI. `testBasicPaths` asserts default filesystem URI, working directory, home directory, and qualification all include the authority.

State and persistence: inherits base test local filesystem setup and cleanup. No extra persistent state beyond the viewfs context.

Dependencies and integration: tests `FileContext`/`AbstractFileSystem` authority routing rather than `FileSystem` routing.

Risks and test signals: wrong authority handling may pass authorityless tests but fail here through URI mismatch, missing mount table entries, or incorrect working/home directory qualification.
