# sources/distributed-fs/ceph-client/io_uring/timeout.h

Purpose: defines timeout async data and declares timeout operation/cancellation helpers.

Important APIs/types/functions: `struct io_timeout_data` stores request pointer, hrtimer, target time, hrtimer mode, and flags. Prototypes expose timeout flush, cancel, kill, linked queue/disarm, prep, issue, remove prep, and remove issue.

Control flow: none in the header.

State and persistence: defines per-timeout hrtimer state used while requests are pending.

Dependencies/integration: consumed by linked request completion, cancellation, ring teardown, and opcode dispatch.

Risks/test signals: correct declaration is crucial for timer lifetime and cancellation. Timeout unit/integration tests and lockdep runs cover it.
