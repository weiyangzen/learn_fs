# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolInfo.java

## Purpose
`ProtocolInfo` is a runtime-retained annotation that overrides the default RPC protocol name and optionally declares a protocol version.

## Important APIs, Types, and Functions
`protocolName()` is required. `protocolVersion()` defaults to `-1`, which tells `RPC.getProtocolVersion` to fall back to the legacy `versionID` field.

## Control Flow
`RPC.getProtocolName` and `RPC.getProtocolVersion` inspect this annotation when registering protocols and constructing client request headers.

## State and Persistence Behavior
Annotation metadata is stored in class metadata at runtime. It persists nothing dynamically.

## Dependencies and Integration Points
It is used by protobuf protocol interfaces such as `ProtocolMetaInfoPB` and by server registration/version matching.

## Risks and Test Signals
Risks include mismatched annotation names between client/server translators and missing versions causing reflection failures. Compatibility tests should cover annotated and legacy `versionID` protocols.
