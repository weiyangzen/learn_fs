<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/yarn/ITestS3AMiniYarnCluster.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/yarn/ITestS3AMiniYarnCluster.java


## Purpose
End-to-end integration test running Hadoop WordCount on a MiniYARNCluster with S3A input/output and staging committer.


## Important APIs, Types, and Functions
ITestS3AMiniYarnCluster overrides createConfiguration(), setup(), teardown(), testWithMiniCluster(), getResultAsMap(), writeStringToFile(), and readStringFromFile().


## Control Flow
Configuration selects the S3A staging committer and disables unique filenames. setup requires multipart uploads, creates input dirs, sets working directory, and starts a one-node MiniYARNCluster. The test writes input text, configures WordCount job, waits for completion, validates non-empty _SUCCESS committer metadata, loads SuccessData, reads reducer output, and checks word counts.


## State and Persistence Behavior
Persistent state is S3 input/output/working directories and committer _SUCCESS/part files. Runtime state includes MiniYARNCluster lifecycle and job credentials/configuration.


## Dependencies and Integration Points
Depends on MiniYARNCluster, MapReduce Job APIs, WordCount example classes, S3A staging committer, SuccessData, FileContext, and S3A filesystem reads/writes.


## Risks and Test Signals
Risks are high runtime/environment sensitivity, multipart availability, and committer configuration drift. Signals validate S3A usability from YARN containers and committer output correctness.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/yarn/ITestS3AMiniYarnCluster.java -->
