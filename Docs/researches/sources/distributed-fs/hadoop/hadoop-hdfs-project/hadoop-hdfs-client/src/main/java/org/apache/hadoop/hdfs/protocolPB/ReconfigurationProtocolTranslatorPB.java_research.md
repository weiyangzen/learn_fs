# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolTranslatorPB.java

## Purpose

`ReconfigurationProtocolTranslatorPB.java` adapts the Java `ReconfigurationProtocol` client interface to the protobuf `ReconfigurationProtocolPB` RPC service. It is the client-side wrapper used to start live reconfiguration, query status, and list mutable properties over Hadoop RPC.

## Important APIs, Types, and Functions

The class implements `ProtocolMetaInterface`, `ReconfigurationProtocol`, `ProtocolTranslator`, and `Closeable`. It exposes a public constructor that creates the PB proxy from address, ticket, configuration, and socket factory; static `createReconfigurationProtocolProxy`; `close`; `getUnderlyingProxyObject`; `startReconfiguration`; `getReconfigurationStatus`; `listReconfigurableProperties`; and `isMethodSupported`. It uses immutable empty request protos for all no-argument RPCs.

## Control Flow

Proxy creation installs `ProtobufRpcEngine2` for `ReconfigurationProtocolPB` and calls `RPC.getProxy` with protocol version and socket timeout. Each RPC method sends a prebuilt empty request through `ipc`: `startReconfiguration` ignores the empty response, `getReconfigurationStatus` converts the response through `ReconfigurationProtocolUtils`, and `listReconfigurableProperties` returns `response.getNameList()`. Method support probing delegates to `RpcClientUtil`.

## State and Persistence Behavior

The only instance state is the final RPC proxy. No reconfiguration state is stored locally; start/status results are remote service state. `close()` stops the proxy.

## Dependencies and Integration Points

Dependencies include Hadoop RPC (`RPC`, `RpcClientUtil`, `ProtobufRpcEngine2`), `UserGroupInformation`, `Configuration`, generated reconfiguration protos, `ReconfigurationTaskStatus`, and `ReconfigurationProtocolUtils`. It integrates HDFS clients/admin tools with NameNode/DataNode services implementing live reconfiguration.

## Risks and Edge Cases

Risks are mostly RPC compatibility: wrong protocol engine/version, missing method support on older servers, and response conversion drift. The static helper accepts a socket timeout but the public constructor passes `0`, so timeout behavior is inherited from Hadoop RPC defaults unless alternate construction is used.

## Test Signals

Tests should cover proxy creation against a mock or MiniDFS service, start/list/status RPC translation, method-support checks against servers with and without methods, exception translation through `ipc`, and close behavior.
