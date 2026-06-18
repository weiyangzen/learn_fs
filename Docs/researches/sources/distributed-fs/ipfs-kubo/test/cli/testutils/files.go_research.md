# sources/distributed-fs/ipfs-kubo/test/cli/testutils/files.go

Purpose: file-related test helpers for opening fixtures and walking up directories to find a named file.

Important APIs: `MustOpen(name string) *os.File` opens a file or panics with `log.Panicf`. `FindUp(name, dir string) string` scans `dir`, then each parent, returning the first matching path or an empty string at filesystem root.

Control flow: `FindUp` repeatedly calls `os.ReadDir`, compares entry names, advances with `filepath.Dir`, and stops when the parent equals the current directory. ReadDir errors panic.

State and persistence: no persistent state, but `MustOpen` returns an open file descriptor that callers must close if needed.

Dependencies and integration points: supports tests that need fixture discovery independent of current working directory. It uses standard `os`, `filepath`, and `log`.

Risks and test signals: panic-based failure is appropriate for test helpers but can make error recovery impossible. `FindUp` matches only basename equality and does not skip permission-denied directories; such errors panic.
