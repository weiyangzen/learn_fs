# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/TestUdpServer.java

## Purpose
`TestUdpServer` is a manual UDP portmap request harness. It sends raw ONCRPC UDP packets to local rpcbind/portmap for NFS and mount service discovery. It is not a JUnit test.

## Important APIs, Types, And Functions
`createPortmapXDRheader` writes RPC call headers. `testGetportMount`, `testGetport`, and `testDump` build portmap GETPORT/DUMP requests. `Runtest1` and `Runtest2` are `SubjectInheritingThread` wrappers.

## Control Flow
`main` starts `Runtest1`, which sends a MOUNT GETPORT request to `localhost:SUN_RPCBIND`. `testRequest` opens a `DatagramSocket`, sends the bytes, waits for one response, and closes the socket.

## State And Persistence
There is no durable state. The only runtime state is the UDP socket and request/response byte arrays.

## Dependencies And Integration Points
It depends on a local rpcbind service and Hadoop ONCRPC XDR/RpcCall classes. It is adjacent to NFS gateway registration behavior rather than HDFS data paths.

## Risks
It exits the JVM on IO or host errors, has no assertions, ignores the `request2` argument, and contains likely copy/paste errors where headers are written to `xdr_out` instead of `request2`. It is unsuitable for automated CI as written.

## Test Signals
Manual success is receipt of a UDP response. Automated regression coverage would need assertions over decoded portmap responses and cleanup/timeouts.
