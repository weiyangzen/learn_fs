# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolSignature.java

## Purpose
`ProtocolSignature` serializes a protocol version and method fingerprint list. It underpins Hadoop RPC compatibility checks and method-support queries.

## Important APIs, Types, and Functions
It implements `Writable`, registers a factory, stores `version` and nullable `methods`, and provides `getFingerprint(Method)`, `getFingerprint(Method[])`, `getProtocolSignature(...)`, and `resetCache`. A null methods array means client and server protocol methods match.

## Control Flow
Fingerprints hash method name, return type, and parameter type names. Method arrays are converted to fingerprints, sorted, and hashed for order-independent comparison. Static cache maps protocol names to signatures/fingerprints and is synchronized.

## State and Persistence Behavior
Writable read/write serializes version plus optional method hashes. Static cache stores reflected signatures in memory only.

## Dependencies and Integration Points
It is used by `VersionedProtocol`, `ProtocolProxy`, `RpcClientUtil`, and `ProtocolMetaInfoServerSideTranslatorPB`. `TestRPCCompatibility` exercises fingerprint and cache behavior.

## Risks and Test Signals
Risks include hash collisions, cache key ignoring version differences for same protocol name, and `Arrays.sort` mutating input arrays. Tests should verify order independence, method overload distinctions, cache reset, and version mismatch behavior.
