# sources/cloud-native/moby/daemon/logger/local/local_test.go

Purpose: tests local logger write/read behavior and benchmarks logging.

Important APIs/types/functions: `TestWriteLog`, `TestReadLog`, `BenchmarkLogWrite`, and helper `copyLogMessage`.

Control flow/state/persistence: tests create temporary local log files, write messages with timestamps, sources, attrs, and partial metadata, then read them back through the driver.

Dependencies/integration: validates `local.New`, `Log`, `ReadLogs`, protobuf marshaling, and `LogFile` persistence.

Risks: benchmark uses representative messages but does not replace correctness tests for rotation or corruption.

Test signals: strong round-trip signal for local protobuf records and metadata preservation.
