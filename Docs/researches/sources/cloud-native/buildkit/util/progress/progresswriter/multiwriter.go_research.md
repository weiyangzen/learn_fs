<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/multiwriter.go -->
# sources/cloud-native/buildkit/util/progress/progresswriter/multiwriter.go

Purpose: multiplexes multiple prefixed progress streams into a single underlying `Writer`, allowing parallel sub-operations to report into one solve status channel.

Important APIs and types: `MultiWriter`, `NewMultiWriter`, `WithPrefix`, `prefixed`, and helper `addPrefix`.

Control flow: `NewMultiWriter` wraps an existing writer and starts a goroutine that waits until at least one prefixed stream is ready, then waits for all prefix goroutines before closing the underlying status channel. `WithPrefix` creates an input channel; a goroutine reads statuses, optionally rewrites vertex names with `addPrefix`, and forwards to the underlying writer status channel until input closes or the main writer completes.

State and persistence: in-memory only. `errgroup.Group`, `sync.Once`, and `ready` coordinate lifecycle. `MultiWriter.Status` intentionally returns nil; callers use per-prefix writers instead.

Dependencies and integration: uses BuildKit `client.SolveStatus`, `errgroup`, and the `Writer` interface from this package. Prefix formatting preserves existing bracketed names by inserting the prefix after the opening bracket.

Risks: underlying status channel closure waits for `ready`; if no prefixed writer is ever created, the closure goroutine blocks. Forwarding mutates vertex names in the received status object when `force` is true, which affects any other consumer of the same pointers.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/multiwriter.go -->
