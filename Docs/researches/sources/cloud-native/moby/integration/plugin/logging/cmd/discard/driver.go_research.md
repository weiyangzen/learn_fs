# sources/cloud-native/moby/integration/plugin/logging/cmd/discard/driver.go

## Purpose
Implements a discard log driver plugin fixture. It consumes log data and reports that plugin-side log reading is unsupported, allowing tests to verify Docker's log cache behavior.

## Important APIs, Types, And Functions
Defines request/response structs, `driver` with mutex-protected `logs map[string]io.Closer`, `handle`, and `respond`. Endpoints include `/LogDriver.StartLogging`, `/LogDriver.StopLogging`, and `/LogDriver.Capabilities`.

## Control Flow
`StartLogging` decodes a file path, opens it read-only, stores the closer under lock, starts `io.Copy(io.Discard, f)` in a goroutine, and responds with an error string if any. `StopLogging` closes the stored file. `Capabilities` returns `ReadLogs: false`.

## State And Persistence Behavior
Runtime state is the in-memory map of open log files. No persistent state is written. File descriptors remain open until stop or process exit.

## Dependencies And Integration Points
Used by the logging read tests as a plugin fixture behind `/run/docker/plugins/plugin.sock`. It exercises daemon behavior when plugin read capability is false.

## Risks
If `os.OpenFile` fails, the code still stores `f` only after the call; however it calls `respond(err, w)` without returning before later map assignment in the current control flow, which would risk storing nil if future changes moved code. The fixture is intentionally simple and not production-hardened.

## Test Signals
Indirect signals come from `ContainerLogs` behavior with log cache enabled/disabled when this plugin is selected.
