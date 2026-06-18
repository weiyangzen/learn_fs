## sources/cloud-native/moby/daemon/logger/adapter_test.go

Purpose: Tests plugin logger adapter read/write behavior using a mock logging plugin.

Important fixtures and tests: `mockLoggingPlugin` uses an `io.Pipe`, protobuf delimited reader, log slice, condition variable, and optional error. `StartLogging` decodes entries into memory. `ReadLogs` re-encodes stored entries, optionally waits in follow mode, and closes on plugin error or non-follow exhaustion. `newMockPluginAdapter` builds a `pluginAdapterWithRead`. `TestAdapterReadLogs` logs two messages, reads them without follow, reads them with follow, logs a live third message, closes the logger, and checks watcher closure.

Control flow and state: The condition variable synchronizes producer/consumer tests. `waitLen` blocks until plugin ingestion sees expected messages. Test helper `testMessageEqual` compares line bytes, nanosecond timestamp, and source.

Dependencies and integration points: Exercises internal `logdriver` protobuf framing and the `Logger`/`LogReader` contract.

Risks covered: Validates follow mode, EOF closure, live append delivery, message timestamp preservation, and clean close propagation. Does not cover partial-log metadata or error paths from plugin `ReadLogs`/decode.
