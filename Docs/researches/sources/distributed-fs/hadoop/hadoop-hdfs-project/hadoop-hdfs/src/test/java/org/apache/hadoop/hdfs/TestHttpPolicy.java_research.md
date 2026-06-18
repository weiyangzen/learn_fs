# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHttpPolicy.java

## Purpose
Verifies invalid HDFS HTTP policy configuration is rejected with `HadoopIllegalArgumentException`.

## APIs and Control Flow
`testInvalidPolicyValue` creates a `Configuration`, sets `DFS_HTTP_POLICY_KEY` to `"invalid"`, and asserts `DFSUtil.getHttpPolicy(conf)` throws `HadoopIllegalArgumentException`.

## State, Dependencies, Integration
The only state is configuration key/value data. Dependencies are `Configuration`, `DFSConfigKeys`, `DFSUtil`, and JUnit `assertThrows`. It integrates config parsing with validation of the HTTP/HTTPS policy enum contract.

## Risks and Test Signals
The signal is direct exception type matching. Risk is narrow coverage: it does not check accepted values or exception messages, only the invalid-value failure path.
