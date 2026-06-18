# sources/cloud-native/containers-storage/pkg/reexec/reexec_test.go

Purpose: tests reexec registration, child dispatch, context cancellation, and self-path resolution.

Important APIs, types, and functions: init-time registrations for `reexec` and `sleep`, `TestRegister`, `TestCommand`, `TestCommandContext`, and `TestNaiveSelf`.

Control flow: init registers child functions and calls `Init`. Tests assert duplicate registration panics, run a child that panics and expect exit status 2, run a sleeping child with deadline cancellation and check stdout, and run `naiveSelf` through a subprocess plus `LookPath` resolution.

State and persistence: mutates global reexec registry and `os.Args[0]` in the naive-self test. No persistence.

Dependencies and integration points: depends on `bytes`, `context`, `fmt`, `os`, `os/exec`, `testing`, `time`, and `testify`. It validates command files for the current platform.

Risks and edge cases: init-time `Init` changes package-global state for all tests. The deadline test depends on scheduler/process timing but uses a generous 5-second deadline.

Test signals: confirms registration uniqueness, argv-based dispatch, context-driven process termination, stdout propagation before cancellation, and executable path resolution.
