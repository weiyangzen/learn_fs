# sources/cloud-native/moby/daemon/internal/stdcopymux/writer.go

## Purpose
Implements Docker's stdout/stderr multiplexing writer format for daemon stream output. `NewStdWriter` wraps a shared `io.Writer` and prefixes every payload with the 8-byte stdcopy header so the receiver can demultiplex frames by stream type.

## Important APIs, Types, And Functions
`stdWriter` embeds `io.Writer` and stores a stream prefix byte derived from `stdcopy.StdType`. `Write` validates the wrapped writer, builds the header with stream id at byte 0 and payload size at bytes 4-7 in big-endian order, appends the payload, and writes a single framed buffer. `bufPool` reuses `bytes.Buffer` instances to reduce allocations.

## Control Flow
Each write is transformed into `header + payload`, sent once to the underlying writer, then translated back to the number of payload bytes by subtracting the header length. Negative adjusted counts are clamped to zero. A nil payload is a no-op.

## State And Persistence
There is no persistent state beyond the pooled temporary buffers. Correctness assumes stdout, stderr, and system-error wrappers share the same underlying writer so frame order is preserved by the caller.

## Dependencies And Integration Points
Integrates with `api/pkg/stdcopy` framing constants and consumers such as attach/log streaming. The wire format is compatibility-sensitive.

## Risks And Test Signals
Partial writes can report adjusted payload counts that do not distinguish header-only progress from payload progress. Concurrent calls rely on the underlying writer's safety; this wrapper adds no locking. No tests are listed in this subset for this package, so coverage is indirect through stdcopy and attach behavior.
