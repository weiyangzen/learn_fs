## sources/distributed-fs/ipfs-kubo/test/dependencies/go-sleep/go-sleep.go

Purpose: tiny portable sleep helper for shell tests, accepting Go duration strings instead of relying on platform-specific `sleep` subsecond syntax.

Important APIs and control flow: `main` requires exactly one argument, parses it with `time.ParseDuration`, sleeps for that duration, and exits. `usageError` prints accepted units and exits with `-1`. There is no persisted state.

Dependencies and integration points: uses only `fmt`, `os`, and `time`; sharness helpers call `go-sleep 100ms`, `200ms`, and similar values in polling loops.

Risks: invalid duration strings or wrong arity abort the helper and can cause retry loops to fail immediately. Exit code `-1` maps through the OS to a nonzero status, which is enough for shell tests but not semantically specific. Test signals are stable timing behavior across Linux, BSD, and macOS shells.
