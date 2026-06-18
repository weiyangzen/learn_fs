# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/S3AContract.java

Purpose: Hadoop filesystem contract binding for S3A tests.

Important APIs/types/functions: extends `AbstractBondedFSContract`. Constant `CONTRACT_XML` points to `contract/s3a.xml`. Constructors optionally add that resource after forcing S3A static initialization. `getScheme()` returns `s3a`; `getTestPath()` wraps the superclass path with `S3ATestUtils.createTestPath()`.

Control flow: construction calls `S3AFileSystem.initializeClass()` to load deprecated keys, then optionally adds contract XML. Test path generation is delegated to base contract and S3A test utility.

State and persistence: holds inherited contract configuration; no external persistence.

Dependencies and integration: central integration point between Hadoop contract-test framework and S3A configuration/test-path utilities.

Risks: adding `contract/s3a.xml` can reload configuration and interfere with tests that deliberately remove bucket overrides; the boolean constructor exists for those cases.

Test signals: not a test itself, but every S3A contract test depends on it.
