# sources/cloud-native/moby/integration/plugin/logging/cmd/close_on_start/main.go

## Purpose
Minimal log driver plugin binary used to simulate a log plugin that closes the log FIFO immediately after `StartLogging`, approximating plugin crash or early close behavior.

## Important APIs, Types, And Functions
Defines `start{File string}` and `main`. `main` listens on Unix socket `/run/docker/plugins/plugin.sock`, registers `/LogDriver.StartLogging`, decodes JSON, opens the provided file read-only, closes it immediately, writes HTTP 200 and `{}`, then serves through `http.Server` with `ReadHeaderTimeout`.

## Control Flow
The process blocks in `server.Serve(l)`. Each StartLogging request opens then closes the log file before responding. Bad JSON returns 400; open failures return 500.

## State And Persistence Behavior
No persistent state. The only side effect is temporarily opening and closing the daemon-provided log file.

## Dependencies And Integration Points
Used by logging integration tests through plugin fixture creation. It implements only enough of the log driver API to test daemon behavior after log sink closure.

## Risks
The plugin intentionally omits other log driver endpoints. If daemon startup begins requiring capabilities or stop endpoints for this path, the fixture would need expansion.

## Test Signals
Signal is indirect through `TestContinueAfterPluginCrash`, which expects containers to continue producing stdout without daemon "broken pipe" log entries.
