<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/VersionedProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/VersionedProtocol.java

## Purpose
`VersionedProtocol` is the legacy/common base interface for Hadoop RPC protocols that support version and method-signature negotiation.

## Important APIs, Types, And Functions
- `getProtocolVersion(String protocol, long clientVersion)` returns the server version for a protocol.
- `getProtocolSignature(String protocol, long clientVersion, int clientMethodsHash)` returns a `ProtocolSignature` including version and supported method data.
- Implementing protocol interfaces are expected to expose a static `versionID`.

## Control Flow
Implementations answer client negotiation requests before normal RPC calls. The default behavior is often delegated to `ProtocolSignature.getProtocolSignature(...)`.

## State And Persistence
The interface defines no state. Implementations may compute signatures from class metadata.

## Dependencies And Integration Points
Integrated with Hadoop RPC protocol negotiation, `RPC.getProtocolVersion`, `ProtocolSignature`, and client-side compatibility checks.

## Risks And Edge Cases
Incorrect versions or method hashes can break rolling upgrades and client/server compatibility. Removing legacy support can affect downstream Hadoop ecosystem projects.

## Test Signals
Protocol compatibility tests should verify version mismatch handling, method support lookup, and rolling-upgrade compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/VersionedProtocol.java -->
