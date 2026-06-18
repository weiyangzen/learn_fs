<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestMarkerToolRootOperations.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestMarkerToolRootOperations.java


## Purpose
Sequential root-filesystem tests for auditing and cleaning directory markers at bucket root.


## Important APIs, Types, and Functions
ITestMarkerToolRootOperations overrides setup() and defines ordered tests test_100_audit_root_noauth() and test_200_clean_root().


## Control Flow
setup skips unless root tests are enabled and stores the qualified root path. Tests run MarkerTool audit and clean with verbose output and write scan output to temporary files for logging.


## State and Persistence Behavior
Persistent state can include root-level marker cleanup across the whole test bucket, so the class is root-test tagged and ordered. rootPath is per-test state.


## Dependencies and Integration Points
Depends on AbstractMarkerToolTest, maybeSkipRootTests(), RootFilesystemTest, MethodOrderer, and MarkerTool CLI constants.


## Risks and Test Signals
High blast radius because it scans/cleans root. Signals are mostly smoke/integration checks for root path handling rather than exact marker counts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestMarkerToolRootOperations.java -->
