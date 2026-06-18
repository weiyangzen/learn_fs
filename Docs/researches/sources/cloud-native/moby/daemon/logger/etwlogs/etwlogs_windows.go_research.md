## sources/cloud-native/moby/daemon/logger/etwlogs/etwlogs_windows.go

Purpose: Windows-only log driver that emits container logs as Event Tracing for Windows (ETW) provider events.

Important APIs and types: `etwLogs` stores container/image names and IDs. `New` registers the ETW provider and returns a logger. `Log` builds a formatted event string and calls `EventWriteString`. `Close` unregisters the provider. Helper functions include `createLogMessage`, `registerETWProvider`, `unregisterETWProvider`, `callEventRegister`, `callEventWriteString`, and `callEventUnregister`.

Control flow and state: Global `providerHandle`, `refCount`, and mutex manage provider lifetime across logger instances. Registration occurs only when refcount transitions from zero; unregister occurs when it drops to one and `EventUnregister` succeeds. `Log` rejects calls if the provider handle is invalid, returns messages to the pool after formatting, and writes UTF-16 strings through Windows syscalls.

Dependencies and integration points: Uses `Advapi32.dll` lazy procs, `golang.org/x/sys/windows`, a fixed provider GUID, containerd logging, and the logger factory via separate registration file.

Risks: Refcount/provider global state is concurrency-sensitive. `unregisterETWProvider` does not report unregister failure. Event payload is a formatted string, so escaping/field boundaries depend on content. Windows syscall errors are surfaced as numeric return codes.

Test signals: No tests in this subset; behavior depends on Windows runtime APIs.
