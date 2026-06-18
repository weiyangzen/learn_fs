# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/web/resources/TestWebHdfsCreatePermissions.java

## Purpose
`TestWebHdfsCreatePermissions` verifies that WebHDFS create and mkdir operations apply the same default and explicit permissions expected from normal HDFS creation paths.

## Important APIs, Types, and Functions
The test uses `WebHdfsTestUtil.createConf`, `MiniDFSCluster.getHttpUri`, raw `HttpURLConnection`, `NamenodeProtocols.getFileInfo`, and `FsPermission`. The shared helper `testPermissions` constructs a `/webhdfs/v1` URL with `user.name`, operation, and optional `permission` parameter, sends a PUT, then reads the resulting permission through the NameNode RPC server.

## Control Flow
Each test starts a cluster, invokes `testPermissions`, and the helper shuts the cluster down in its finally block. The cases are MKDIRS with no permission expecting `rwxr-xr-x`, MKDIRS with `permission=777`, CREATE with no permission expecting `rw-r--r--`, and CREATE with `permission=666`.

## State and Persistence Behavior
State is the live HDFS namespace permission bits after WebHDFS requests. There is no restart or persistence validation.

## Dependencies and Integration Points
This file integrates the WebHDFS HTTP layer, query parameter parsing, NameNode create/mkdir implementation, and RPC metadata reads.

## Risks and Edge Cases
Risks include WebHDFS ignoring explicit permission parameters, applying directory defaults to files or vice versa, or returning HTTP success while creating metadata with wrong permission bits. A structural risk is that `testPermissions` shuts down the cluster even though `tearDown` also does, which is tolerated by the null check but unusual.

## Test Signals
Signals are HTTP status codes `200 OK` or `201 Created` and exact symbolic permission strings read back from the NameNode.
