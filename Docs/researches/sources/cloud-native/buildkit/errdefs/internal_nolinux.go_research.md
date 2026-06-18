# Research: sources/cloud-native/buildkit/errdefs/internal_nolinux.go

Purpose: supplies the non-Linux implementation of syscall internal-error classification.

Important behavior: `syscallErrors` returns nil, so platform errno values are not automatically considered internal/resource-exhaustion on non-Linux builds.

State and dependencies: no state; imports only `syscall` for signature compatibility.

Risks and test signals: non-Linux platforms rely on explicit `Internal` wrapping instead of errno classification, which may produce different diagnostics from Linux. There are no direct tests in this subset.
