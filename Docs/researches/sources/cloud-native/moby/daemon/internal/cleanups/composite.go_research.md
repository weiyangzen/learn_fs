# sources/cloud-native/moby/daemon/internal/cleanups/composite.go

## Purpose
Implements a simple LIFO cleanup stack with aggregate error reporting.

## APIs, Control Flow, and Integration
`Composite.Add` appends cleanup functions. `Call` executes all registered cleanups in reverse order via `call`, joins all returned errors using `multierror.Join`, and clears the stack. `Release` clears the stack but returns a function that can later execute the previously registered cleanups, also in reverse order.

## State, Dependencies, and Risks
State is an in-memory slice; there is no synchronization, so callers must not mutate from multiple goroutines. Cleanup functions are always called even after earlier errors. Risks include nil cleanup functions panicking and callers forgetting to invoke a released function. Tests confirm reverse order and nested/joined error preservation.
