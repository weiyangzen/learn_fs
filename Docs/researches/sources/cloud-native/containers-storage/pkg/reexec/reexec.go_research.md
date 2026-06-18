# sources/cloud-native/containers-storage/pkg/reexec/reexec.go

Purpose: provides registration and dispatch for reexecuting the current binary into named subroutines.

Important APIs, types, and functions: `Register`, `Init`, `panicIfNotInitialized`, `naiveSelf`, and globals `registeredInitializers` and `initWasCalled`.

Control flow: packages register initializers by name. `Init` marks initialization called, checks whether `os.Args[0]` matches a registered name, runs the initializer if found, and returns true to tell main to exit. `panicIfNotInitialized` enforces that command constructors are only used after `Init`. `naiveSelf` resolves `os.Args[0]` through `LookPath` or absolute path conversion.

State and persistence: global in-memory registry and initialization flag. No persistence.

Dependencies and integration points: depends on `fmt`, `os`, `os/exec`, and `filepath`. Used by lockfile tests and any code needing subprocess execution of internal functions.

Risks and edge cases: duplicate registration panics. Matching on `os.Args[0]` means command constructors must set `cmd.Args` exactly to registered names. Registry is not concurrency-protected.

Test signals: `reexec_test.go` covers duplicate registration, child command dispatch, context cancellation, and `naiveSelf` resolution.
