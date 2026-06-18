# sources/cloud-native/moby/daemon/internal/stream/attach.go

## Purpose
Connects client attach streams to a container stream `Config`, including stdin forwarding, stdout/stderr forwarding, close propagation, detach-key handling for TTY input, and cancellation cleanup.

## Important APIs, Types, And Functions
`AttachConfig` carries requested stream flags, container-side pipes, client-side streams, TTY/detach settings, and stdin close policy. `Config.AttachStreams` populates container pipes according to requested streams. `Config.CopyStreams` starts an `errgroup` of copy goroutines and returns a single error channel. `copyEscapable` wraps TTY input with `term.NewEscapeProxy` and uses the default ctrl-p ctrl-q detach sequence when no keys are supplied.

## Control Flow
For stdin, a goroutine copies client input into `CStdin`; when it exits it either closes container stdin for non-TTY `CloseStdin`, or closes output pipes to unblock readers. Separate goroutines copy `CStdout` and `CStderr` to the client and close client stdin plus their pipe when done. A supervisor goroutine races group completion against context cancellation; on cancel it closes all container pipes and client stdin so blocked `io.Copy` calls can unwind.

## State And Persistence
State is transient stream lifecycle state. The function mutates and closes caller-provided pipe handles but persists no daemon metadata.

## Dependencies And Integration Points
Uses `pools.Copy`, containerd logging, `pkg/errors`, `errgroup`, and `moby/term`. It is called by daemon attach/exec APIs after `AttachStreams` wires stream `Config` broadcasters.

## Risks And Test Signals
The main risk is goroutine leaks from blocked reads when containers exit without I/O. `io.ErrClosedPipe` is normalized to success. `attach_test.go` exercises no-I/O combinations and expects cancellation to return `context.Canceled` within 10 seconds.
