# sources/cloud-native/buildkit/exporter/tar/export_windows.go

Purpose: provides the Windows tar writer implementation, allowing tar export of special Windows rootfs metadata files.

Important API: `writeTar(ctx, fs, w)` wraps `fsutil.WriteTar` in `winio.RunWithPrivileges`.

Control flow: enables `SeBackupPrivilege` for the duration of archive writing so privileged metadata files can be read.

State and persistence: no persistent state; privilege scope is bound to the callback.

Dependencies and integration: selected on Windows and used transparently by `tar/export.go`.

Risks and test signals: behavior depends on Windows privilege availability. Regressions surface in Windows tar exporter tests and builds involving Windows container layers.
