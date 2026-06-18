# sources/cloud-native/moby/daemon/internal/builder-next/executor_others.go

## Purpose
Provides the non-Linux, non-Windows executor fallback under `//go:build !linux && !windows`.

## APIs, Control Flow, and Integration
`newExecutor(executorOpts)` returns a `stubExecutor`, no proxy provider, and no error. This lets the package compile on unsupported OS targets while avoiding real process execution support. It satisfies the same signature as Linux and Windows executor constructors.

## State, Dependencies, and Risks
There is no persisted state. Dependencies are only BuildKit `executor` and `network` interfaces. Runtime risk is that builds requiring execution will fail later through stub behavior; this file is primarily a compile-time portability shim. Test coverage is indirect by build tags and package compilation on non-Linux/non-Windows platforms.
