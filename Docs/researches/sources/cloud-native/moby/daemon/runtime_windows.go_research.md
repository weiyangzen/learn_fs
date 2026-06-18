# sources/cloud-native/moby/daemon/runtime_windows.go

## Purpose
Provides Windows stubs for the runtime configuration API used by shared daemon code.

## Important APIs, Types, And Functions
Defines empty `runtimes` type with `Get`, plus `initRuntimesDir` and `setupRuntimes`. `Get` returns "not implemented"; setup functions return nil/empty values.

## Control Flow
No runtime resolution is implemented on Windows in this file. Calls either no-op during setup or return an error for `Get`.

## State And Persistence
No runtime script directory or runtime state is created by these stubs.

## Dependencies And Integration Points
Compiles against daemon config on Windows and satisfies references from shared reload/start code.

## Risks And Edge Cases
Any shared code that unexpectedly calls `runtimes.Get` on Windows receives a generic not-implemented error. Windows runtime selection is handled elsewhere.

## Test Signals
No file-local tests. Windows build/test jobs provide compile coverage.
