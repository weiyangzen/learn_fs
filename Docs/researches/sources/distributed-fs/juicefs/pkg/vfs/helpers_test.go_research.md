# sources/distributed-fs/juicefs/pkg/vfs/helpers_test.go

Purpose: unit-tests VFS helper formatting.

Important APIs and types: `smodeCase`, global `cases`, `TestSmode`, `TestEntryString`, and `TestError`.

Control flow and state: `TestSmode` checks directory, regular, symlink, and socket modes with special bits. `TestEntryString` verifies nil entries, entries without attrs, and file entries with mode/nlink/uid/gid/timestamps/length. `TestError` checks errno formatting for success and `EACCES`.

Persistence and integration: no storage or metadata service is required beyond constructing a `meta.Attr`.

Risks and test signals: these tests are high-signal for diagnostic output compatibility. They do not test `NewLogContext.Duration` timing behavior.
