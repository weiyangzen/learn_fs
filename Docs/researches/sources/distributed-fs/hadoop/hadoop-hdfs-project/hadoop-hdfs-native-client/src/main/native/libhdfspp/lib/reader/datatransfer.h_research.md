# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/datatransfer.h

Purpose: declares DataTransfer protocol constants and a SASL-wrapping DataNode stream template.

Important APIs and types: constants `kDataTransferVersion` and `kDataTransferSasl`, enum `Operation` with write/read block opcodes, and template `DataTransferSaslStream<Stream>` implementing `DataNodeConnection`.

Control flow: the wrapper forwards async reads/writes to the underlying stream, exposes `Handshake`, stubs `Connect` with a TODO, and declares `Cancel`. Implementation details are included from `datatransfer_impl.h`.

State and persistence: stores shared wrapped stream and `DigestMD5Authenticator`. No disk persistence.

Dependencies and integration: depends on data-transfer protobufs, SASL authenticator, async stream, and `DataNodeConnection`. It is intended to secure DataNode data-transfer streams.

Risks and test signals: `Connect` is currently a no-op TODO and `Cancel` is implemented as empty in the template impl, so secured DataTransfer integration is incomplete. Tests should distinguish direct stream forwarding from actual SASL handshake coverage.
