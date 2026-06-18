# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/TestOutOfOrderWrite.java

## Purpose
`TestOutOfOrderWrite` is a manual TCP client harness for sending NFS CREATE and out-of-order WRITE requests to a running NFS gateway. It is not a JUnit test.

## Important APIs, Types, And Functions
Helpers `create`, `write`, and `testRequest` build XDR/RPC requests. `WriteHandler` captures the file handle from the CREATE response. `WriteClient` customizes the Netty pipeline, and `main` sends writes for offsets 2000, 1000, and 0.

## Control Flow
`main` fills three data arrays, opens a TCP client to the configured NFS port, sends CREATE, waits until `WriteHandler` extracts the new handle, then sends three WRITE frames in reverse order using `Nfs3Utils.writeChannel`.

## State And Persistence
Runtime state is static handle/channel references and test byte arrays. If run against a live gateway, it creates a file named `out-of-order-write<timestamp>` and writes data through NFS.

## Dependencies And Integration Points
It depends on ONCRPC request framing, Netty, NFSv3 request/response types, and a separately running NFS server. It is intended to exercise `OpenFileCtx` out-of-order buffering.

## Risks
The write RPC header appears to use the CREATE procedure value when constructing WRITE requests, so the harness may not work as intended without inspection. It has no assertions, no automated cleanup, and can hang waiting for a handle.

## Test Signals
As a manual tool, useful signals are server logs and final HDFS file content. It should be converted to an automated integration test before being relied on for regression coverage.
