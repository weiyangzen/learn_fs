# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolProxy.java

## Purpose
`ProtocolProxy` wraps a client proxy with optional server-method support discovery for versioned protocols.

## Important APIs, Types, and Functions
The constructor stores the protocol class, proxy, and `supportServerMethodCheck` flag. `getProxy` returns the underlying proxy. `isMethodSupported` lazily calls `fetchServerMethods`, compares protocol versions, and checks method fingerprints through `ProtocolSignature`.

## Control Flow
If server-method checking is disabled, every method is treated as supported. Otherwise the first support check reflects the client method, calls `VersionedProtocol.getProtocolSignature` through the proxy, detects version mismatch, caches server method hashes, and evaluates requested method hashes.

## State and Persistence Behavior
State is in-memory per proxy: fetched flag and optional hash set. No persistence is performed.

## Dependencies and Integration Points
It depends on `VersionedProtocol`, `RPC`, and `ProtocolSignature`. Protobuf engine proxies currently pass `false`, while legacy/versioned clients may use checks.

## Risks and Test Signals
Risks include method-name/parameter mismatch, stale cached signatures, and casts to `VersionedProtocol`. Compatibility tests should cover matching signatures, partial method sets, and version mismatch.
