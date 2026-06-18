<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/error.go -->
# sources/cloud-native/moby/daemon/command/error.go

## Purpose
Defines a simple command error type carrying a textual status and integer status code.

## Important APIs, Types, And Functions
`StatusError` has `Status` and `StatusCode` fields and implements `error` through `Error`.

## Control Flow
`Error` formats both fields as `Status: <status>, Code: <code>`.

## State And Persistence Behavior
No mutable state or persistence. Values are immutable unless callers modify the struct.

## Dependencies And Integration Points
Uses only `fmt`. Intended for command execution paths that need to return an exit/status detail through the error channel.

## Risks And Test Signals
No direct tests in this subset. The main risk is callers needing structured access but receiving only a formatted string unless they type-assert `StatusError`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/error.go -->
