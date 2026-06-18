# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/datatransfer.cc

Purpose: implements utility functions for DataTransfer SASL/encryption handshake messages.

Important APIs and functions: `DataTransferSaslStreamUtil::ConvertToStatus` and `PrepareInitialHandshake`.

Control flow: `ConvertToStatus` maps `DataTransferEncryptorMessageProto` statuses to libhdfspp `Status`: unknown key becomes `InvalidEncryptionKeyException`, generic error becomes `Status::Error`, and success copies payload. `PrepareInitialHandshake` initializes a success status with empty payload.

State and persistence: stateless helper functions only.

Dependencies and integration: depends on `datatransfer.h`, `hdfspp/status.h`, and generated DataTransfer protobufs. Used by `DataTransferSaslStream` template code in `datatransfer_impl.h`.

Risks and test signals: tests should verify all DataTransfer encryptor status mappings and payload clearing/copying. Unknown future status values currently fall through as success, which is a compatibility risk.
