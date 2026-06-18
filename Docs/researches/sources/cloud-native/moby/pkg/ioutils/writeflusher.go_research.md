<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/writeflusher.go -->
# sources/cloud-native/moby/pkg/ioutils/writeflusher.go

Purpose: wraps a writer with flush tracking and close signaling. Important APIs are `WriteFlusher`, `Write`, `Flush`, `Flushed`, `Close`, and `NewWriteFlusher`. Control flow writes through to the underlying writer unless closed, calls an underlying `Flush` method when available or a no-op flusher otherwise, records that a flush happened, and protects state with a mutex/channel-like close guard. State includes flushed and closed flags. Dependencies are `io` and `sync`. Risks include writes after close, underlying flush errors not represented because `Flush` has no return, and concurrent write/close ordering. Test signal appears through consumers rather than a dedicated test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/writeflusher.go -->
