# Research: sources/cloud-native/buildkit/errdefs/internal_linux.go

Purpose: provides Linux syscall errno classification for internal/system errors.

Important API: `syscallErrors` returns a map marking `EIO`, `EFAULT`, `ENOTRECOVERABLE`, and `EHWPOISON` as internal non-resource-exhaustion, while `ENOMEM` and `ENOSPC` are internal resource-exhaustion.

State and dependencies: no persistence or runtime state. Depends on `golang.org/x/sys/unix` errno constants and syscall types.

Risks and test signals: the map defines which low-level failures are treated as infrastructure/system problems. Over-classification can hide user errors; under-classification can reduce diagnostic quality. No direct tests are listed.
