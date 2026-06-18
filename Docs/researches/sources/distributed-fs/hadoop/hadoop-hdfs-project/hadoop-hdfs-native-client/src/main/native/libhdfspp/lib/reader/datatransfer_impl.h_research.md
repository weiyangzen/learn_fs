# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/datatransfer_impl.h

Purpose: implements the template handshake pipeline for `DataTransferSaslStream`.

Important APIs and types: utility declarations for status conversion and initial handshake, nested continuations `Authenticator` and `ReadSaslMessage`, template method `Handshake`, and `Cancel`.

Control flow: `Handshake` writes the DataTransfer SASL magic number, sends an initial empty-success protobuf, reads the server SASL message, evaluates it with `DigestMD5Authenticator`, sends the response protobuf, and reads the final server message. The pipeline uses protobuf delimited-message continuations.

State and persistence: handshake state is temporary in a pipeline `State` struct containing request/response protobufs, payload strings, and stream. The stream and authenticator are object state from `datatransfer.h`.

Dependencies and integration: depends on continuation framework, ASIO write helpers, protobuf continuations, SASL authenticator, Boost ASIO, and generated DataTransfer protobufs.

Risks and test signals: encryption scheme handling is TODO, and `Authenticator::Run` always calls `next(Status::OK())` even if authentication failed, relying on message status rather than local status propagation. `Cancel` is empty. Tests should cover successful/failed challenge-response, malformed delimited protobufs, and handshake cancellation.
