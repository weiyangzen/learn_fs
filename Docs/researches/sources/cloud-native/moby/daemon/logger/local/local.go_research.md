# sources/cloud-native/moby/daemon/logger/local/local.go

Purpose: local logging driver that persists compact protobuf log records to rotated files.

Important APIs/types/functions: `New`, `ValidateLogOpt`, `Log`, `marshal`, `messageToProto`, `protoToMessage`, `resetProto`, and driver constants/defaults. `driver` owns a `loggerutils.LogFile` and immutable extra attrs.

Control flow/state/persistence: `New` validates config, gathers attrs/tag, sorts attrs for deterministic protobuf output, and opens a `LogFile`. `Log` marshals a `logger.Message` into `[size][protobuf][size]`, writes via `LogFile`, and returns the message to the pool on success. `messageToProto` preserves partial metadata; `protoToMessage` reconstructs backend attrs and UTC timestamp.

Dependencies/integration: depends on generated `logdriver` protobuf, shared `loggerutils.LogFile`, `logger.Info`, and backend partial metadata.

Risks: persistent format compatibility is critical. Extra attrs are shared pointers and must remain immutable. Buffer pooling needs reset discipline to avoid data retention bugs.

Test signals: `local_test.go`, `read_test.go`, and loggerutils tests validate write/read, partial metadata, rotation, and tailing.
