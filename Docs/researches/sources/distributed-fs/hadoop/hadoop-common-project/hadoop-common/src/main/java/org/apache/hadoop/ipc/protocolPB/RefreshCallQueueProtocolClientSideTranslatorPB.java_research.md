<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/RefreshCallQueueProtocolClientSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/RefreshCallQueueProtocolClientSideTranslatorPB.java

## Purpose
Client-side adapter translating `RefreshCallQueueProtocol.refreshCallQueue()` to the shaded protobuf PB protocol.

## Important APIs, Types, And Functions
- Implements `ProtocolMetaInterface`, `RefreshCallQueueProtocol`, and `Closeable`.
- Uses singleton empty `RefreshCallQueueRequestProto`.
- `refreshCallQueue()` invokes the PB proxy through `ShadedProtobufHelper.ipc`.
- `isMethodSupported` delegates to `RpcClientUtil`; `close` stops the proxy.

## Control Flow
The no-argument Java call is converted into an empty protobuf request and sent to `rpcProxy.refreshCallQueue`. The response is ignored; exceptions are converted from `ServiceException` to `IOException`.

## State And Persistence
Holds only the PB proxy and a static immutable request. No local persistence.

## Dependencies And Integration Points
Used by admin clients that trigger live call-queue refresh on RPC servers. Integrates with Hadoop RPC proxy lifecycle and protocol metadata.

## Risks And Edge Cases
Stopping the proxy in `close()` affects shared proxy owners. Because the request is empty, all behavior depends on the server-side delegate and server authorization.

## Test Signals
Tests should verify a PB call is made, exceptions convert to IOExceptions, method support is queried with the correct protocol version, and proxy close stops the proxy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/protocolPB/RefreshCallQueueProtocolClientSideTranslatorPB.java -->
