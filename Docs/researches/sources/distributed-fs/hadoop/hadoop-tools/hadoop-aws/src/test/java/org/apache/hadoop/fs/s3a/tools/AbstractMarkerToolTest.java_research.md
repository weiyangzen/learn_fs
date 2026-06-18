<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/AbstractMarkerToolTest.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/AbstractMarkerToolTest.java


## Purpose
Base class for S3A directory-marker CLI/tool tests with shared configuration, execution, output-reading, and assertion helpers.


## Important APIs, Types, and Functions
AbstractMarkerToolTest overrides createConfiguration() and teardown(), and defines tempAuditFile(), expectMarkersInOutput(), readOutput(), markerTool() overloads, run(), uncachedFSConfig(), runToFailure(), toPath(), and m().


## Control Flow
Configuration disables create-performance flags, authoritative path overrides, bucket probes, and FS caching for tool invocations. Helpers run S3Guard/MarkerTool commands, assert exit codes, read audit output files, and delete test dirs before superclass teardown to avoid audit failures from intentional markers.


## State and Persistence Behavior
State is inherited filesystem/test-directory state plus temporary audit files. Tool execution may create/delete S3 directory markers under test paths.


## Dependencies and Integration Points
Depends on AbstractS3ATestBase, S3GuardToolTestHelper, MarkerTool.ScanArgsBuilder/ScanResult, S3A constants, FileSystem, and AssertJ.


## Risks and Test Signals
Risks include teardown order and caching hiding config changes. Signals centralize marker count and exit-code checks used by concrete marker-tool tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/AbstractMarkerToolTest.java -->
