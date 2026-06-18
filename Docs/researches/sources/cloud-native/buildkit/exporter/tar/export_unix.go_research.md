# sources/cloud-native/buildkit/exporter/tar/export_unix.go

Purpose: provides the non-Windows tar writer implementation.

Important API: `writeTar(ctx, fs, w)` is the abstraction called by `tar/export.go`.

Control flow: directly delegates to `fsutil.WriteTar`, passing through the context, filesystem, and write closer.

State and persistence: no state beyond bytes written to the caller-provided stream.

Dependencies and integration: selected by `//go:build !windows` and shares a signature with the Windows privileged variant.

Risks and test signals: risks are limited to archive traversal/write failures from `fsutil.WriteTar`. Unix tar exporter integration is the primary signal.
