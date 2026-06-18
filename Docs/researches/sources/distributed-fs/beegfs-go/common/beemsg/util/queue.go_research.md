<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/queue.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/queue.go

Purpose: minimal thread-safe FIFO queue for arbitrary values.

Important APIs/types/functions: unexported `queue` with `tryGet` and `put`.

Control flow: `tryGet` locks, returns nil for empty, otherwise removes the first slice element. `put` locks and appends to the end.

State and persistence: in-memory slice protected by a mutex.

Dependencies and integration points: used by `NodeConns` to pool `net.Conn` values.

Risks: `nil` cannot be stored as a meaningful value because nil is also the empty sentinel. Popping from the front retains the underlying array until the queue is discarded, which can retain references under high churn.

Test signals: `queue_test.go` verifies FIFO order and empty behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/queue.go -->
