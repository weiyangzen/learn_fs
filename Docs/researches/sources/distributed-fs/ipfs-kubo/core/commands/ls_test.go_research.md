# sources/distributed-fs/ipfs-kubo/core/commands/ls_test.go

## Purpose

`ls_test.go` validates the formatting helpers behind `ipfs ls --long`. It is focused on deterministic string rendering of file modes and modification times rather than full command execution.

## Important APIs, Types, and Functions

The file defines `TestFormatMode` and `TestFormatModTime`, using `testing` and `testify/assert`. The tests exercise unexported helpers `formatMode` and `formatModTime` from `ls.go`.

## Control Flow

`TestFormatMode` is table-driven and runs parent and child subtests in parallel. Cases cover regular files, directories, symlinks, named pipes, sockets, block and character devices, no/full permissions, setuid/setgid/sticky bits with and without execute bits, combined special bits, and directory sticky-bit output. Each case compares the exact 10-character Unix-style mode string. `TestFormatModTime` runs parallel subtests for zero time, old times, very old times, future times, and output length consistency. It uses fixed historical UTC values for stable year-format checks and relative `time.Now()` values only where the assertion is intentionally pattern/length based.

## State and Persistence Behavior

The tests do not mutate repository or filesystem state. They are pure formatting tests with wall-clock dependence in recent/future cases.

## Dependencies and Integration Points

These tests integrate directly with `ls.go` helpers and indirectly protect the `ipfs ls --long` text encoder. The dependency on `testify/assert` matches broader Kubo test style.

## Risks and Test Signals

The tests provide signal for file mode coverage, special-bit semantics, and the 12-character alignment contract for mtimes. Remaining gaps include full `tabularOutput` coverage, HTTP streaming output, sorting, escaped names, directory size placeholders, and deterministic tests around the six-month boundary. Because `formatModTime` uses `time.Now()`, boundary-sensitive tests should avoid exact expectations near the threshold.
