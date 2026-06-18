# sources/cloud-native/moby/integration/internal/container/exec.go

Purpose: shared helper for synchronous `docker exec` operations in integration tests.

Important APIs and types: `ExecResult`, `Stdout`, `Stderr`, `Combined`, `AssertSuccess`, `Exec`, and `ExecT`.

Control flow: `Exec` creates an exec instance with stdout/stderr attached and stdin closed, applies optional create-option mutators, attaches to the exec, uses `demultiplexStreams` from `container.go` to read output, then inspects the exec to return exit code and buffers. `ExecT` wraps `Exec` and fails the test on error.

State and persistence: creates transient exec instances inside existing containers and captures their output in memory. It reads daemon exec inspect state for exit code.

Dependencies and integration: depends on Moby exec API, the package stream demultiplexer, contexts, and testing interfaces.

Risks: if the context expires while output is still being copied, `Exec` returns an error and may not inspect exit code. Callers needing partial output on timeout do not get a result.

Test signals: helper-only file; many tests rely on it to validate cgroup files, mounts, and runtime state inside containers.
