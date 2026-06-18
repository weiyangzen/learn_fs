# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ProtoUtil.java

## Purpose
`ProtoUtil` contains protobuf and Hadoop RPC wire helpers: protobuf varint decoding, IPC connection context construction, UGI reconstruction, RPC kind conversion, and RPC request header construction.

## Important APIs, Types, And Functions
Important APIs are `readRawVarint32`, `makeIpcConnectionContext`, `getUgi`, `convert(RPC.RpcKind)`, `convert(RpcKindProto)`, and `makeRpcRequestHeader`. The request header path integrates trace, caller context, authorization header, and optional alignment context state.

## Control Flow
`readRawVarint32` manually decodes up to five significant bytes and discards up to five upper bytes before declaring a malformed varint. Connection-context construction conditionally sends user fields based on auth method: Kerberos sends effective user, token sends none, simple sends effective and optional real user. Header construction sets core RPC fields, then conditionally attaches tracing, caller context, authorization bytes, and alignment state.

## State And Persistence
The class is stateless. It reads thread-local/current context from tracing, caller context, authorization context, and alignment context, then serializes it into protobuf messages.

## Dependencies And Integration Points
It depends on Hadoop IPC protobuf classes, `RPC`, `UserGroupInformation`, SASL auth methods, tracing, authorization context, and third-party protobuf `ByteString`.

## Risks
Wire compatibility is critical. Returning null for unknown enum conversions can defer failures. Auth-method-specific UGI elision must remain aligned with server-side authentication assumptions. Context propagation can leak caller or authorization metadata if set incorrectly.

## Test Signals
Tests should cover malformed varints, auth-method matrix for context fields, proxy-user reconstruction, enum round trips, trace/caller/authorization propagation, and alignment-context mutation of request headers.
