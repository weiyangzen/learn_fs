<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/readers.go -->
# sources/cloud-native/moby/pkg/ioutils/readers.go

Purpose: reader wrappers for close callbacks and context-cancelable reads. Important APIs are `NewReadCloserWrapper`, `NewCancelReadCloser`, `cancelReadCloser.Read`, `Close`, and `subsequentCloseWarn`. Control flow wraps an `io.Reader` with a closer protected by atomic close detection, pipes reads from an input reader into an `io.Pipe` in a goroutine, closes with context cancellation errors, and logs warning stacks on repeated closes. State includes atomic closed flags, context cancellation, and pipe endpoints. Dependencies include context, IO pipes, atomics, containerd logging, and debug stacks. Risks include goroutine lifetime, close races, warning noise on intentional repeated closes, and cancellation semantics. Tests cover close callback once and cancelable read behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/readers.go -->
