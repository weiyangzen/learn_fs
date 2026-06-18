# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/UnknownCryptoProtocolVersionException.java

Purpose: `UnknownCryptoProtocolVersionException` is a checked HDFS client exception for unsupported crypto protocol versions found during encryption metadata processing or negotiation.

Important APIs/types/functions: the sole constructor `UnknownCryptoProtocolVersionException(String unknown)` builds the message `"Unknown CryptoProtocolVersion: " + unknown`.

Control flow: no internal control flow exists. The class serves as a typed signal for callers that a crypto protocol version is unrecognized.

State and persistence behavior: state is limited to the inherited exception message. There is no persistence or cleanup.

Dependencies and integration points: depends on `java.io.IOException` and is expected to be thrown by HDFS crypto code that parses file encryption information or data-transfer encryption protocol fields.

Risks: because it represents compatibility failure, tests should validate that newer/unknown protocol values fail clearly and do not silently downgrade crypto behavior. Diagnostic content should remain safe if the unknown string originates from serialized metadata.
