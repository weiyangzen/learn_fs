# sources/cloud-native/moby/integration/session/session_test.go

## Purpose
Validates the daemon `/session` HTTP endpoint's h2c upgrade behavior and bad-upgrade error responses.

## Important APIs, Types, And Functions
- `TestSessionCreate` posts to `/session` with `X-Docker-Expose-Session-Uuid` and `Upgrade: h2c`, expecting `101 Switching Protocols`.
- `TestSessionCreateWithBadUpgrade` posts with no upgrade and with `Upgrade: foo`, expecting `400 Bad Request` with specific messages.
- Uses `internal/testutil/request` raw HTTP helpers.

## Control Flow
Both tests skip Windows, call `setupTest`, derive the daemon host, issue POST requests, close or read response bodies, and assert status codes/headers/body fragments.

## State And Persistence
No durable daemon state is intended. A successful session upgrade creates a transient upgraded connection identified by the header-provided UUID.

## Dependencies And Integration Points
Integrates direct HTTP request handling, API router upgrade validation, session manager, and h2c negotiation. It bypasses the high-level client to verify protocol-level details.

## Risks And Edge Cases
The successful upgrade body must be closed to avoid leaks. Tests are disabled on Windows with FIXME notes. Error assertions depend on response message text.

## Test Signals
Expected signals are `101` plus `Upgrade: h2c` for valid requests, and `400` bodies containing `no upgrade` or `not supported` for invalid upgrades.
