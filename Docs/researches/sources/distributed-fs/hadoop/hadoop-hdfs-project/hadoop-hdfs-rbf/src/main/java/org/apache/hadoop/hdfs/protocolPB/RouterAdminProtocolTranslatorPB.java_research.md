# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterAdminProtocolTranslatorPB.java

## Purpose
Client-side translator for Router admin RPCs. It exposes native manager interfaces while forwarding calls through a `RouterAdminProtocolPB` protobuf proxy.

## Important APIs, Types, and Functions
The class implements `ProtocolMetaInterface`, `MountTableManager`, `RouterStateManager`, `NameserviceManager`, `RouterGenericManager`, `Closeable`, and `ProtocolTranslator`. `close()` stops the RPC proxy, `getUnderlyingProxyObject()` exposes it, and `isMethodSupported()` delegates to `RpcClientUtil`. Admin methods convert PBImpl request objects to protos, invoke the proxy, and wrap response protos in PBImpl response objects.

## Control Flow
Mount-table and nameservice methods expect incoming native requests to be PBImpls, cast them, extract `getProto()`, and call `rpcProxy`. Safe-mode and disabled-nameservice list calls build empty request protos directly. `refreshSuperUserGroupsConfiguration()` builds an empty proto, calls the proxy, then unwraps a boolean status from `RefreshSuperUserGroupsConfigurationResponsePBImpl`. `ServiceException` is converted to `IOException` using `getRemoteException(e).getMessage()`.

## State and Persistence Behavior
The translator holds only the `rpcProxy`; all durable state changes occur remotely in the Router admin server/state store. `close()` is important lifecycle behavior because it releases the Hadoop RPC proxy.

## Dependencies, Risks, and Test Signals
The class depends on generated federation protobuf messages, PBImpl store protocol classes, Hadoop IPC `RPC`, `RpcClientUtil`, `ProtocolTranslator`, and `ShadedProtobufHelper.getRemoteException`. It assumes callers pass PBImpl request objects; alternate implementations of native request interfaces will fail with `ClassCastException`. Tests should assert close/proxy behavior, method-support probing, correct proto forwarding, safe-mode empty-request behavior, refresh status unwrapping, and useful IOException conversion.
