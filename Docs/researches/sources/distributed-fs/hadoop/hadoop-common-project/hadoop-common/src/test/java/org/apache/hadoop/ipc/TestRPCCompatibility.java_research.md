# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRPCCompatibility.java

Purpose: tests method-signature fingerprint compatibility used by versioned RPC protocol negotiation.

Important APIs/types/functions: `VersionedProtocol`, `ProtocolInfo`, `ProtocolSignature`, `TestProtocol0/1/2/3/4`, `TestImpl0/1/2`, `RPC.setProtocolEngine()`, and `ProtobufRpcEngine2`.

Control flow: setup resets `ProtocolSignature` cache and binds all local protocols to protobuf engine 2. The active test reflects methods from protocol interfaces and checks fingerprints differ when method name, return type, parameter type, or parameter count differs, match across declaring classes for identical signatures, and produce order-independent aggregate fingerprints.

State and persistence behavior: static config/server/address fields are present but this file's active coverage is reflection/cache state only. Teardown stops any proxy/server if future tests add them. No durable state.

Dependencies and integration points: method fingerprinting is part of Hadoop RPC compatibility negotiation; protocol annotations allow newer interfaces to share protocol names with older ones.

Risks and test signals: focused signal for accidental fingerprint algorithm changes. It does not perform full client/server compatibility calls in its current form, but protects the core hash behavior those calls rely on.
