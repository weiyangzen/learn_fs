# sources/cloud-native/buildkit/exporter/local/export_windows.go

Purpose: provides the Windows implementation of local exporter filesystem walking.

Important API: `fsWalk(ctx, fs, s, walkFn)` matches the Unix signature but wraps the walk in `winio.RunWithPrivilege(winio.SeBackupPrivilege, ...)`.

Control flow: caller-supplied filesystem walking is executed while holding backup privilege so Windows rootfs or metadata files that require elevated read semantics can be traversed.

State and persistence: no persistent state; privilege scope is bounded to the callback executed by `go-winio`.

Dependencies and integration: used only on Windows through build tags. It integrates with the same duplicate-path validation path in `local/export.go`.

Risks and test signals: failures depend on process privilege availability and special Windows files. The in-code reference to issue 4994 explains the special-file motivation. Windows exporter and tar tests are the main regression signal.
