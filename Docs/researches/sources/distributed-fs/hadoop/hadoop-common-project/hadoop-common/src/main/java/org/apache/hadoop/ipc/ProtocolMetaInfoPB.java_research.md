# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolMetaInfoPB.java

## Purpose
`ProtocolMetaInfoPB` is the protobuf RPC protocol used to ask a server which protocol versions and method signatures it supports.

## Important APIs, Types, and Functions
It extends `ProtocolInfoService.BlockingInterface` and is annotated with protocol name `org.apache.hadoop.ipc.ProtocolMetaInfoPB` and version `1`.

## Control Flow
`RPC.Server.initProtocolMetaInfo` registers this protocol on every RPC server through a `ProtocolMetaInfoServerSideTranslatorPB`. Clients use `RpcClientUtil` to reuse an existing connection and query method support.

## State and Persistence Behavior
The interface has no state. Responses are derived from the server's registered protocol map.

## Dependencies and Integration Points
It depends on generated `ProtocolInfoProtos` and integrates with `ProtobufRpcEngine2`.

## Risks and Test Signals
Risks are annotation drift and generated proto incompatibility. Tests should verify method support queries across multiple protocols and versions.
