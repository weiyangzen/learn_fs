<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/LeaveSafeModeResponsePBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/LeaveSafeModeResponsePBImpl.java

## Purpose
Protobuf implementation of `LeaveSafeModeResponse`, returning whether a Router successfully transitioned out of safe mode.

## APIs, Types, and Functions
Implements `PBRecord` over `LeaveSafeModeResponseProto`. Public response API is `getStatus()` and `setStatus(boolean)`, mapped to the proto `status` field.

## Control Flow, State, and Persistence
The translator owns mutable builder/proto state. Server code sets `status`, the protobuf RPC layer serializes it, and clients read the same field. The response is transient RPC data and is not stored in the State Store.

## Dependencies and Integration
Produced by `RouterAdminServer.leaveSafeMode()` and consumed by `RouterAdmin.leaveSafeMode()` through `RouterStateManager`. It integrates with `RouterProtocol.proto` where `leaveSafeMode` returns `LeaveSafeModeResponseProto`.

## Risks and Test Signals
Default proto2 boolean value is false, so missing `status` is indistinguishable from failure. Relevant tests are Router admin safe-mode transition tests and PB translator round-trip coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/LeaveSafeModeResponsePBImpl.java -->
