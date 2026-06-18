<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/select/ITestSelectUnsupported.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/select/ITestSelectUnsupported.java


## Purpose
Integration test proving removed S3 Select functionality is consistently reported unsupported.


## Important APIs, Types, and Functions
ITestSelectUnsupported defines STATEMENT and tests openFile .must/.opt behavior, path capability absence, and S3GuardTool select command failure.


## Control Flow
The .must(SELECT_SQL) path must raise UnsupportedOperationException with SELECT_UNSUPPORTED; .opt(SELECT_SQL) is ignored after touching a file. hasPathCapability must return false, and the CLI path is invoked with system exits disabled to inspect exit code.


## State and Persistence Behavior
Persistent state is a touched methodPath object for the optional-open test. CLI state is limited to ExitUtil system-exit interception.


## Dependencies and Integration Points
Depends on AbstractS3ATestBase, SelectConstants, ContractTestUtils.touch, S3GuardTool.main(), ExitUtil, and launcher exit codes.


## Risks and Test Signals
Risks are accidental re-advertisement of removed capability or inconsistent optional/must semantics. Signals cover API-level, capability-level, and command-line behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/select/ITestSelectUnsupported.java -->
