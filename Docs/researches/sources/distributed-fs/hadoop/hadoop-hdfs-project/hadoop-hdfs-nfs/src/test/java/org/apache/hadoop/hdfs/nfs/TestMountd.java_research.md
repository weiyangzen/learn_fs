# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/TestMountd.java

## Purpose
`TestMountd` is a JUnit test for NFS gateway startup and portmap UDP timeout propagation to both mountd and nfsd RPC programs.

## Important APIs, Types, And Functions
The single test `testStart` uses `MiniDFSCluster`, `NfsConfiguration`, `Nfs3`, `RpcProgramMountd`, `RpcProgramNfs3`, and a NULL XDR call.

## Control Flow
The test starts a one-node MiniDFSCluster, sets mountd and NFS ports to 0 for parallel-safe ephemeral binding, sets the portmap timeout config, starts `Nfs3`, invokes mountd `nullOp` and nfsd `nullProcedure`, and asserts each RPC program sees the configured timeout.

## State And Persistence
It creates temporary MiniDFSCluster state and starts local NFS services on ephemeral ports. No durable repository state is written.

## Dependencies And Integration Points
It integrates the HDFS test cluster, NFS service startup, mount daemon, NFS daemon, and ONCRPC XDR handling.

## Risks
The test does not use `finally` around cluster shutdown, so failures before the explicit shutdown can leak test resources. It verifies startup/config plumbing, not actual mount or NFS data operations.

## Test Signals
Passing indicates NFS and mount daemons can start against MiniDFSCluster and share the UDP portmap timeout configuration.
