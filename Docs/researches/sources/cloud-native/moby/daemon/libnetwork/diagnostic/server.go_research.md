<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/diagnostic/server.go -->
# sources/cloud-native/moby/daemon/libnetwork/diagnostic/server.go

## Purpose
Provides an opt-in HTTP diagnostic server for libnetwork and networkdb commands.

## Important APIs, Types, And Functions
`Server` holds enable state, `http.Server`, mux, port, and dynamic handler map. `New` registers `/`, `/help`, and `/ready`. `Handle` and `HandleFunc` support handler replacement without re-registering mux patterns. `Enable`, `Shutdown`, `Enabled`, `ParseHTTPFormOptions`, and `HTTPReply` manage lifecycle and response formatting.

## Control Flow
`Enable` records the port, avoids double-start, creates an HTTP server with the diagnostic server as handler, and starts `ListenAndServe` in a goroutine. Registered mux wrappers lock and fetch the current handler. Default handlers parse form options, audit-log the command, and return plain text or JSON responses.

## State And Persistence
State is in-memory. No diagnostic data is persisted; handlers may expose state from other components.

## Dependencies And Integration Points
Used by libnetwork controller diagnostics and `networkdb-test`. Integrates with Go `net/http`, containerd logging, and diagnostic result types.

## Risks And Edge Cases
The server has no authentication and should remain bound to safe addresses; controller uses localhost while test server can listen broadly. Re-enabling on a new port while already enabled does not reconfigure. Read header timeout is intentionally long.

## Test Signals
Signals include `/ready` returning `OK`, `/help` listing handlers, JSON/plain formatting, handler replacement, enable/disable lifecycle, and audit logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/diagnostic/server.go -->
