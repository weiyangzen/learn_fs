# sources/cloud-native/containerd/internal/cri/io/container_io.go

## Purpose

This file owns long-lived container stdio plumbing. It adapts containerd `cio.IO` to either filesystem FIFOs or reconnectable streaming endpoints, fans container stdout/stderr to multiple attach/log consumers, and manages cancellation/wait/close behavior for container IO.

## Important APIs, Types, and Functions

`ContainerIO` stores the container ID, `cio.FIFOSet`, opened `stdioStream`, stdout/stderr `WriterGroup`s, and a `wgCloser`. `ContainerIOOpts` configures construction through `WithFIFOs`, `WithNewFIFOs`, and `WithStreams`. `NewContainerIO` validates FIFOs/streams and opens actual stdio endpoints. `Config` returns the `cio.Config`. `Pipe` starts background copying from container output into writer groups. `Attach` wires a client’s stdin/stdout/stderr to the existing streams. `AddOutput` registers named output writers and returns displaced writers. `Cancel`, `Wait`, and `Close` delegate to the closer and FIFO set.

## Control Flow

Construction applies all options, requires a non-nil FIFO set, then calls `newStdioStream`. `Pipe` starts one goroutine for stdout and, when non-TTY, one for stderr; each drains into the writer group, closes its reader/group, and marks the shared waitgroup done. `Attach` generates per-attach keys, optionally copies client stdin into container stdin, registers output writers with close informers, waits for output close or context cancellation, removes writer-group entries on cancellation, and ensures the wrapped stdin reader is closed.

## State and Persistence Behavior

Runtime state is in open FIFOs/streams, writer-group membership, goroutines, and waitgroups. FIFO paths live below the volatile container root when `WithNewFIFOs` is used. Streaming mode encodes stable stream IDs derived from container ID and stream name so shim streams can reconnect after containerd restarts.

## Dependencies and Integration Points

It depends on the CRI `io` helpers, `pkg/cio`, `pkg/ioutil.WriterGroup`, containerd logging, and `util.GenerateID`. The CRI server attaches user streams through `ContainerIO.Attach`; container creation stores the `ContainerIO` in the container store.

## Risks and Edge Cases

TTY mode intentionally suppresses stderr. Incorrect writer-group removal can leak attach writers or block copies. `StdinOnce` behavior differs for TTY and non-TTY to match kubectl/docker expectations. Output goroutines must be closed on create failure and container teardown, otherwise FIFO reads or stream connections can leak.

## Test Signals

Tests should cover FIFO and stream construction, TTY versus non-TTY stderr behavior, attach cancellation cleanup, `StdinOnce` close behavior, multiple concurrent `AddOutput` consumers, and `Wait` returning after output goroutines drain.
