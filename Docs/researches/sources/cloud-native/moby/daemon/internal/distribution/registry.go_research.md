# sources/cloud-native/moby/daemon/internal/distribution/registry.go

## Purpose
Creates authenticated Docker distribution repository clients and defines supported media/config types.

## APIs, Control Flow, and Integration
Package vars list acceptable media-type prefixes, default image config types, plugin config types, and `mediaTypeClasses`. `newRepository` constructs an HTTP transport with proxy/TLS/timeouts, adds Docker headers and OpenTelemetry wrapping, pings `/v2/`, builds token/basic or pass-through bearer auth, creates the distribution repository with path-only remote name, and wraps setup failures in `fallbackError` with transport status. `passThruTokenHandler` injects `Authorization: Bearer`.

## State, Dependencies, and Risks
State is network transport/auth configuration. Risks include relying on ping challenge flow, token scopes matching requested actions, fallback classification on ping errors, and media-type allowlists needing updates for new artifact classes. Tests cover pass-through token host scoping.
