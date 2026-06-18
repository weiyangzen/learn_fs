<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestMarkerTool.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestMarkerTool.java


## Purpose
Integration tests for MarkerTool auditing, cleaning, limits, rename behavior, and directory-marker expectations.


## Important APIs, Types, and Functions
ITestMarkerTool defines marker CLI tests, assertMarkersDeleted(), nested CreatedPaths, createPaths(), and verifyRenamed(). It tracks expected file/marker counts as fields.


## Control Flow
Tests create a standard tree with base marker, empty dirs, non-empty dirs, and files; then run marker scans/CLI commands with limits, expected min/max, audit output files, clean/audit modes, and public many-object bucket scans. Rename test verifies markers are not copied to destination while files and directories remain visible.


## State and Persistence Behavior
Persistent state is S3 test trees and intentional directory markers. Temporary audit files capture scan output. Expected counts are instance fields populated during createPaths().


## Dependencies and Integration Points
Depends on AbstractMarkerToolTest, MarkerTool constants, S3GuardTool bucket-info command, PublicDatasetTestUtils, ContractTestUtils.touch, and S3A directory marker policy.


## Risks and Test Signals
Risks include directory-marker policy changes, root/base marker semantics, and public bucket availability. Signals validate CLI exit codes, audit output counts, marker purge behavior, and rename marker cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestMarkerTool.java -->
