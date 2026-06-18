# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClosedFS.java

Purpose: validates operations against a closed S3A filesystem fail consistently and do not leak lifecycle threads.

Important APIs/types/functions: extends `AbstractS3ATestBase`; setup qualifies root and closes the FS immediately. Teardown is no-op because FS is already closed. Static `THREAD_SET` captures initial thread names and `@AfterAll` asserts final threads are a subset. Tests intercept `IOException` containing `E_FS_CLOSED` for status, listing, create, delete, and open operations; instrumentation test checks metric system absence and non-null IOStatistics.

Control flow: each test starts from a closed FS and invokes one operation expecting the closed-FS error.

State and persistence: closes the shared test FS; no S3 objects should be created after close.

Dependencies and integration: S3A closed-state checks, lifecycle thread utilities, instrumentation, and LambdaTestUtils.

Risks: thread subset assertion can be brittle when unrelated JVM threads appear. Teardown intentionally bypasses superclass cleanup.

Test signals: integration coverage for closed-filesystem guardrails and lifecycle cleanup.
