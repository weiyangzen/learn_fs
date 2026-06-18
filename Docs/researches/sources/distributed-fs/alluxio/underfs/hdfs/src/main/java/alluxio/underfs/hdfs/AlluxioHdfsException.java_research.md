## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/AlluxioHdfsException.java

### Purpose
`AlluxioHdfsException` maps HDFS and WebHDFS exceptions to Alluxio runtime exceptions with gRPC statuses, error types, and retryability.

### Important APIs, Types, And Functions
`fromUfsException(Exception)` is the main conversion entry. `convertException` unwraps Jersey `ParamException`, `ContainerException`, Hadoop `RemoteException`, and some `SecurityException` causes. `toCause` handles nested causes, including the HDFS invalid-token/standby exception case.

### Control Flow
The converter normalizes wrapper exceptions first, then maps security, authorization, not found, unsupported operation, invalid argument, IO, and unknown categories to corresponding statuses. General `IOException` maps to `ABORTED`, external, retryable.

### State, Persistence, And Dependencies
No state is retained. It depends on Alluxio runtime exception types, gRPC `Status`, Hadoop IPC/security exceptions, and Jersey exceptions.

### Integration Points
`HdfsPositionedUnderFileInputStream` wraps read failures with `AlluxioHdfsException.from(e)`, surfacing lower-level HDFS errors through Alluxio's runtime-exception model.

### Risks
Most HDFS errors are marked non-retryable except generic IO, which may be too broad or too narrow depending on the original remote exception. Message extraction can assume nested causes exist for parameter errors.

### Test Signals
No direct test exists in this subset. Useful tests would cover each mapped exception category, RemoteException unwrapping, StandbyException nested in InvalidToken, and null/empty messages.
