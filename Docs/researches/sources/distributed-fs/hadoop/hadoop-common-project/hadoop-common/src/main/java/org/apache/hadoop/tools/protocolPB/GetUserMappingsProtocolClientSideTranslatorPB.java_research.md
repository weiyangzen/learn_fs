# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/protocolPB/GetUserMappingsProtocolClientSideTranslatorPB.java

Purpose: this client-side translator adapts the protobuf RPC blocking interface to the classic `GetUserMappingsProtocol` Java interface.

Important APIs and types: it implements `ProtocolMetaInterface`, `GetUserMappingsProtocol`, and `Closeable`. It stores a `GetUserMappingsProtocolPB` proxy, uses a null `RpcController`, implements `getGroupsForUser`, `isMethodSupported`, and `close`.

Control flow: `getGroupsForUser` builds `GetGroupsForUserRequestProto` with the user, invokes `rpcProxy.getGroupsForUser` through `ShadedProtobufHelper.ipc` to convert service exceptions, then converts the response group list to a `String[]`. `close` stops the RPC proxy.

State and persistence behavior: persistent state is only the RPC proxy reference. No data is cached.

Dependencies and integration points: integrates Hadoop RPC, protobuf-generated request/response classes, `RpcClientUtil`, protocol version lookup, and `GetUserMappingsProtocolPB`.

Risks: a null controller is intentional but assumes server-side code ignores it. Array sizing uses `resp.getGroupsCount()`, preserving list size. Callers must close the translator or proxy resources remain open.

Test signals: cover request user propagation, group order preservation, service exception conversion to IOException, `RPC.stopProxy` on close, and `isMethodSupported` using the PB protocol/version.
