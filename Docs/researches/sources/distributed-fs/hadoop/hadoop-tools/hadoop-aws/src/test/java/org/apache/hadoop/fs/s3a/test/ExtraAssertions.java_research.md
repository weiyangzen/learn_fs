<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/ExtraAssertions.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/ExtraAssertions.java


## Purpose
Private test assertion utility for file counts, text containment, nested causes, status codes, and Abortable results.


## Important APIs, Types, and Functions
ExtraAssertions contains assertFileCount(), assertTextContains(), failIf(), failUnless(), extractCause(), assertStatusCode(), assertCompleteAbort(), and assertNoopAbort().


## Control Flow
assertFileCount recursively lists files and fails with a joined listing on mismatch. Cause helpers unwrap and validate exception causes. Abort helpers assert whether AbortableResult represented a real cleanup or already-closed no-op.


## State and Persistence Behavior
No persistent state; only a static logger. Methods operate on supplied filesystems, paths, strings, exceptions, and abort results.


## Dependencies and Integration Points
Depends on S3AUtils.applyLocatedFiles, ContractTestUtils.fail, AssertJ, JUnit assertions, DurationInfo, AWSServiceIOException, and Abortable.


## Risks and Test Signals
Risks are test-only visibility: assertStatusCode is protected in a final utility, so it is not generally usable. Signals improve diagnostics for file-count and abort-cleanup tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/ExtraAssertions.java -->
