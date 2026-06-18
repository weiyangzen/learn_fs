<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/shim/io_unix.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/shim/io_unix.go

## Purpose
Provides Unix FIFO plumbing for direct shim exec attachment.

## Important APIs, Types, And Functions
Defines `bufPool` and `prepareStdio`.

## Control Flow
For stdin/stdout/stderr FIFO paths, opens FIFOs, starts goroutines to copy between process stdio and FIFO handles, and returns a WaitGroup for attached mode.

## State And Persistence
Opens existing FIFO paths and transfers bytes; does not create persistent files itself.

## Dependencies And Integration Points
Uses `cio.OpenFifos`, os stdio, pooled buffers, sync.WaitGroup, and Unix build tag.

## Risks And Test Signals
Incorrect FIFO paths can block/open-fail; goroutine copy errors are not propagated beyond attach wait behavior. Exercised indirectly by `ctr shim exec --attach`. Source size reviewed: 93 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/shim/io_unix.go -->
