# sources/cloud-native/moby/integration/plugin/logging/cmd/dummy/main.go

## Purpose
No-op logging plugin fixture used when tests need a plugin process/socket that can be enabled but does not implement meaningful log driver behavior.

## Important APIs, Types, And Functions
`main` listens on `/run/docker/plugins/plugin.sock` and serves an empty HTTP mux with `ReadHeaderTimeout`.

## Control Flow
The process panics if the Unix socket cannot be opened; otherwise it serves indefinitely without registered handlers.

## State And Persistence Behavior
No internal or persistent state.

## Dependencies And Integration Points
Built by logging helper `ensurePlugin` and packaged by plugin fixture creation with logdriver capability metadata supplied outside the binary.

## Risks
Because it has no handlers, it only suits daemon paths that do not call log driver endpoints during the specific test phase. If daemon validation becomes stricter, tests may need a richer dummy.

## Test Signals
Indirectly used by `TestDaemonStartWithLogOpt`, which verifies daemon startup with the plugin configured as default log driver.
