# sources/control-plane/csi-lib-utils/standardflags/automaxprocs.go

## Purpose

This file adds a shared `-automaxprocs` flag for CSI sidecars and drivers. When enabled, it uses Uber's `automaxprocs` library to set `GOMAXPROCS` according to Linux container CPU quota.

## Important APIs and Flow

`AddAutomaxprocs` registers `flag.BoolFunc("automaxprocs", ...)` with `handleAutomaxprocs`. It also wraps an optional logging function into a `maxprocs.Logger`-compatible printf. `EnableAutomaxprocs` is a programmatic equivalent of setting the flag true and avoids re-enabling if already active. `automaxprocsIsEnabled` checks whether an undo function is stored. `handleAutomaxprocs` treats an empty string as enabled, parses explicit booleans, calls `maxprocs.Set` with optional logger when true, and calls the undo function and clears state when false.

## State, Dependencies, and Integration

Package-level globals hold `logFunc` and `undoAutomaxprocs`. Dependencies are Go `flag`, `fmt`, `strconv`, and `go.uber.org/automaxprocs/maxprocs`. Integration is through process-global command-line flags and runtime `GOMAXPROCS`.

## Risks and Test Signals

This is process-global state, so repeated tests or libraries registering flags must guard against duplicate registration. `EnableAutomaxprocs` calls `flag.Set`, so `AddAutomaxprocs` must have been called first. Tests cover true/false/empty/invalid values and enable/disable state transitions.
