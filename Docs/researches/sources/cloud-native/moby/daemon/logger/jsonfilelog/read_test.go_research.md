# sources/cloud-native/moby/daemon/logger/jsonfilelog/read_test.go

Purpose: tests json-file readback, tail, follow, and rotation interactions.

Important APIs/types/functions: benchmarks read logs; `TestEncodeDecode`, `TestReadLogs`, `TestTailLogsWithRotation`, and `TestFollowLogsWithRotation` exercise decoder and `LogFile` read behavior.

Control flow/state/persistence: tests write JSON log files, rotate them through logger operations, then consume `LogWatcher` messages under different configs.

Dependencies/integration: validates `JSONFileLogger.ReadLogs`, `decodeFunc`, and shared `loggerutils.LogFile`.

Risks: timing-sensitive follow tests must coordinate watcher consumption and rotation.

Test signals: strong signal for json-file read compatibility with current and rotated files.
