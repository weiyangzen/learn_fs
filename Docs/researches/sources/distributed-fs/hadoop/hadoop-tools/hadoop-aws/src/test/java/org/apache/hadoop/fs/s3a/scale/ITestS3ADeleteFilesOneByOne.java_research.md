<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADeleteFilesOneByOne.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADeleteFilesOneByOne.java


## Purpose
Variant of the bulk rename/delete scale test that disables S3A multi-object delete.


## Important APIs, Types, and Functions
ITestS3ADeleteFilesOneByOne overrides createScaleConfiguration() and sets Constants.ENABLE_MULTI_DELETE to false after inheriting ITestS3ADeleteManyFiles configuration.


## Control Flow
Control flow is entirely inherited: create many files, rename a directory tree, audit destination/source, then delete recursively. This subclass forces deletion to proceed object-by-object rather than via multi-delete pages.


## State and Persistence Behavior
Persistent state is the same S3 test tree as the parent class, but delete behavior changes from batched DeleteObjects calls to individual object deletes.


## Dependencies and Integration Points
Depends on ITestS3ADeleteManyFiles, S3A Constants.ENABLE_MULTI_DELETE, and the parent’s S3ATestUtils setup.


## Risks and Test Signals
Useful for detecting regressions hidden by bulk delete. It is slower and more request-heavy than the parent, so timeout/cost sensitivity is higher.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADeleteFilesOneByOne.java -->
