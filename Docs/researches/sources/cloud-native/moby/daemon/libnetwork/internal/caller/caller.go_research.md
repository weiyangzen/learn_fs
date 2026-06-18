# Research: sources/cloud-native/moby/daemon/libnetwork/internal/caller/caller.go

Purpose: provides a small helper for retrieving caller function names for diagnostics. Important APIs are internal `callerInfo` and exported `Name`.

Control flow: `callerInfo` calls `runtime.Caller`, obtains `runtime.FuncForPC`, splits the fully qualified function name on `.`, and returns the final segment, falling back to `unknown` if stack lookup fails. `Name(level)` offsets by two stack frames so `level == 0` returns the caller of `Name`, not `Name` itself.

State/dependencies: no persistent state. Dependencies are `runtime` and strings. Integration points are logging/tracing or error messages that want a lightweight function-name label without full file/line data. Risks include method names with dots or compiler-inserted wrappers producing unexpected suffixes, and stack depth changing if wrapper helpers are added. Tests cover direct and nested calls with level 0 and 1.
