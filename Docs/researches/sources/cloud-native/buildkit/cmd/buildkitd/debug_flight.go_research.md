# Research: sources/cloud-native/buildkit/cmd/buildkitd/debug_flight.go

Purpose: adds HTTP endpoints for Go execution flight recorder traces under the daemon debug server.

Important APIs and flow: `flightRecorder` wraps an `x/exp/trace.FlightRecorder` with a mutex. `StartTrace`, `StopTrace`, `SetTracePeriod`, and `Trace` validate current recorder state, parse period values, set response headers, and write trace data. `setupDebugFlight` registers POST start/stop/set-period routes and a GET trace download route.

State and dependencies: state is the in-memory flight recorder and its enabled/period settings. It depends on `net/http`, mutex locking, duration parsing, and `golang.org/x/exp/trace`.

Risks and test signals: mutex serialization prevents concurrent recorder mutation, but trace downloads can expose detailed runtime behavior. Errors are returned as HTTP status codes. There are no direct tests in this subset.
