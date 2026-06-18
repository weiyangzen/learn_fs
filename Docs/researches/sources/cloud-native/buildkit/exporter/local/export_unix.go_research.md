# sources/cloud-native/buildkit/exporter/local/export_unix.go

Purpose: provides the non-Windows implementation of local exporter filesystem walking.

Important API: `fsWalk(ctx, fs, s, walkFn)` is the platform abstraction used by `export.go` while checking duplicate paths before transfer.

Control flow: the Unix build simply delegates to `fsutil.FS.Walk` with the given context, start path, and callback. It has no special privilege elevation, filtering, or retry behavior.

State and persistence: no state is stored; it is a thin call-through over the output `fsutil.FS`.

Dependencies and integration: selected by `//go:build !windows`; shares the same package and signature as the Windows implementation so `export.go` can remain platform-neutral.

Risks and test signals: risk is limited to whatever the underlying filesystem walk returns. Platform-specific coverage is normally via exporter integration tests on Unix runners.
