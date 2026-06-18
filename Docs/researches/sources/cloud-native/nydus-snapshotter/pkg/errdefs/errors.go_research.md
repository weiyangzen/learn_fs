# Research: sources/cloud-native/nydus-snapshotter/pkg/errdefs/errors.go

This file centralizes project-level error sentinels and classifiers. It aliases containerd's `ErrAlreadyExists` and `ErrNotFound`, defines local sentinels for invalid argument, unavailable, not implemented, and device busy, then exposes helpers such as `IsAlreadyExists`, `IsNotFound`, `IsConnectionClosed`, and `IsErofsMounted`.

Integration points are broad: daemon creation checks `ErrAlreadyExists`, client socket failures wrap `ErrNotFound`, filesystem and manager cleanup check EROFS busy via `IsErofsMounted`, and metrics tooling returns `ErrInvalidArgument` for invalid CPU samples. The file depends on `github.com/pkg/errors` for compatibility with wrapped errors, standard `errors` for syscall matching, `net.OpError`, and `syscall.EBUSY`.

State and persistence are absent; this is a semantic layer over error values. Risks include `IsConnectionClosed` comparing an inner error string exactly to `"use of closed network connection"`, local sentinel values not matching containerd `errdefs` classifiers, and comments for `ErrDeviceBusy` copied from not-implemented text. There are no direct tests in this subset, so behavior is only indirectly validated by callers.
