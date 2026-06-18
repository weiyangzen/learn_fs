<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/queue_test.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/queue_test.go

Purpose: unit test for the internal FIFO queue.

Important APIs/types/functions: `TestQueuePutGet`.

Control flow: checks empty pop returns nil, pushes three values, and pops them in insertion order before returning nil again.

State and persistence: in-memory queue only.

Dependencies and integration points: depends on `testify/assert`; protects `NodeConns` queue ordering indirectly.

Risks: no concurrent access test and no test for nil values.

Test signals: basic FIFO behavior is covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/queue_test.go -->
