# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcClientUtil.java

## Purpose
`RpcClientUtil` provides client-side helper logic for method-support discovery through the protocol metadata service and for concise RPC tracing names.

## Important APIs, Types, and Functions
`isMethodSupported` caches protocol signatures by server address, protocol, and rpc kind. `ProtoSigCacheKey` defines cache identity. `convertProtocolSignatureProtos` converts protobuf signature lists to `ProtocolSignature` maps. `methodToTraceString(Method)` builds `OuterClass#method` style names.

## Control Flow
On cache miss, `isMethodSupported` creates a minimal configuration, sets the metadata engine to `ProtobufRpcEngine2`, obtains a `ProtocolMetaInfoPB` proxy reusing the original connection id, fetches signatures, and caches them. It then finds the named client method and compares its fingerprint against the version map.

## State and Persistence Behavior
Static `signatureMap` caches signatures for process lifetime. No persistence is written.

## Dependencies and Integration Points
It depends on `RPC`, `ProtocolMetaInfoPB`, `ProtocolSignature`, protobuf metadata protos, `NetUtils`, and `ShadedProtobufHelper.ipc`. It is used by protocol translators and tracing in protobuf engines.

## Risks and Test Signals
Risks include stale cache after server restart/upgrade, assuming unique method names, cache key equality null assumptions, and security concerns from metadata proxy connection reuse. Tests should cover cache hit/miss, missing methods, multiple versions, and trace string formatting.
