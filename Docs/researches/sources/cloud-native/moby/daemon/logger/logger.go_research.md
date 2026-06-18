# sources/cloud-native/moby/daemon/logger/logger.go

Purpose: core logging interfaces and shared message/watcher types.

Important APIs/types/functions: `Message`, `NewMessage`, `PutMessage`, `Logger`, `SizedLogger`, `ReadConfig`, `LogReader`, `LogWatcher`, `NewLogWatcher`, `ConsumerGone`, `WatchConsumerGone`, `Capability`, and `ErrReadLogsNotSupported`.

Control flow/state/persistence: `Message` values are pooled and reset before reuse; logger implementations take ownership only on successful `Log`. `LogWatcher` has buffered message channel, single-error channel, and idempotent consumer-gone channel to unblock readers.

Dependencies/integration: subtypes `backend.LogMessage`; consumed by every driver, log copier, API readers, plugin adapter, and tests.

Risks: ownership contract is subtle: drivers must call `PutMessage` only after successful logging. Consumers must call `ConsumerGone` to release follow goroutines. `LogWatcher.Err` buffer is only one.

Test signals: `logger_test.go`, `loggertest.Reader`, and all driver tests exercise these contracts.
