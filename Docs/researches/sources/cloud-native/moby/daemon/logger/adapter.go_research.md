## sources/cloud-native/moby/daemon/logger/adapter.go

Purpose: Adapts external logging plugins to the daemon `Logger` and optional `LogReader` interfaces using the internal logdriver protobuf framing.

Important APIs and types: `pluginAdapter` stores plugin identity, FIFO path, capabilities, `Info`, mutex, encoder, stream, and reusable `logdriver.LogEntry` buffer. `Log` encodes `Message` fields and partial-log metadata into the shared buffer. `Close` calls plugin `StopLogging`, closes the FIFO stream, removes the FIFO path, and releases the plugin. `pluginAdapterWithRead.ReadLogs` reads plugin logs through `plugin.ReadLogs`, decodes entries, filters by `Since`/`Until`, and streams messages through a `LogWatcher`.

Control flow and state: `Log` serializes writes with a mutex and returns messages to the pool only on successful encode. Partial metadata is translated into protobuf metadata. `ReadLogs` runs in a goroutine, closes `watcher.Msg` on exit, stops on context cancellation, EOF, decode errors, until cutoff, or consumer-gone signal.

Dependencies and integration points: Uses internal `logdriver` encoder/decoder, plugin lifecycle APIs, `plugingetter.Release`, FIFO filesystem cleanup, and log watchers used by `docker logs`.

Risks: Shared buffer correctness depends on mutex discipline and reset after encode. If plugin `StopLogging` succeeds but stream close/remove fails, errors are logged but close continues. Read filtering is defensive but plugin-side filtering is still expected.

Test signals: `adapter_test.go` uses an in-memory mock plugin to verify log encode/decode, follow mode, live messages, closure, and message equality.
