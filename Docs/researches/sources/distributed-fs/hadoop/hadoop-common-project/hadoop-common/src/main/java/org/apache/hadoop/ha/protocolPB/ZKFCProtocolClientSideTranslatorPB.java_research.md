<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolClientSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolClientSideTranslatorPB.java

Purpose: client-side protobuf translator implementing the native `ZKFCProtocol` API over Hadoop protobuf RPC. It hides request construction and RPC proxy management from callers that need to command a ZooKeeper Failover Controller.

Important APIs, types, and functions: the constructor configures `ProtobufRpcEngine2` for `ZKFCProtocolPB` and obtains an RPC proxy with the current `UserGroupInformation`. `cedeActive(int)` builds `CedeActiveRequestProto`. `gracefulFailover()` sends the default failover request. `close()` stops the proxy, and `getUnderlyingProxyObject()` exposes it for protocol translator plumbing.

Control flow: native method calls build protobuf requests and invoke `rpcProxy` through `ShadedProtobufHelper.ipc`, which converts protobuf service failures into Hadoop `IOException` and `AccessControlException` style errors. There is no retry logic in this class; retry behavior is inherited from the RPC proxy setup.

State and persistence: state is limited to the RPC proxy and a null protobuf controller. It does not persist failover state; it sends commands to the remote ZKFC service.

Dependencies and integration points: depends on Hadoop `RPC`, `ProtobufRpcEngine2`, UGI, socket factory configuration, generated `ZKFCProtocolProtos`, and the public `ZKFCProtocol` interface.

Risks and test signals: lifecycle correctness depends on callers closing the translator. Tests should validate request fields, proxy stop on close, exception conversion, timeout/socket configuration, and compatibility with secure UGI contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/protocolPB/ZKFCProtocolClientSideTranslatorPB.java -->
