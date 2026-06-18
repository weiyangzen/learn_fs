<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/queue/queue_test.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/queue/queue_test.go

Purpose: verifies per-ID serialization behavior for `Queue.Append`.

Important APIs and types: `TestSerialization` appends three callbacks with the same ID.

Control flow: the first callback sleeps to create overlap pressure, each callback checks and advances a shared integer, and the test sleeps long enough for expected completion.

State and persistence: in-memory shared integer and goroutines only.

Dependencies and integration: uses `gotest.tools/assert` and `time.Sleep`; it targets event ordering relied on by libcontainerd event delivery.

Risks: timing-based sleep makes the test less deterministic than using explicit synchronization. It does not test parallelism across different IDs or panic behavior.

Test signals: provides a basic regression signal that callbacks for the same container ID do not run concurrently or out of order.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/queue/queue_test.go -->
