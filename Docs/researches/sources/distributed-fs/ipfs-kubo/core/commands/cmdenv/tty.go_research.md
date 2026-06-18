<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/tty.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/tty.go

## Purpose

Wraps terminal detection for standard and MSYS/Cygwin-style terminals.

## Important APIs, Types, and Functions

`IsTerminal(f *os.File) bool` checks both `isatty.IsTerminal` and `isatty.IsCygwinTerminal` for the file descriptor.

## Control Flow

The function extracts `f.Fd()` and returns true if either terminal detector recognizes it.

## State and Persistence Behavior

Read-only process/file-descriptor inspection.

## Dependencies and Integration Points

Depends on `github.com/mattn/go-isatty` and is used by `ShouldShowProgress`.

## Risks and Edge Cases

Callers must pass a non-nil file. Terminal detection can differ under containers, pipes, Windows compatibility layers, and test runners.

## Test Signals

Indirectly exercised by `progress_test.go`; no dedicated tests for Cygwin/MSYS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/tty.go -->
