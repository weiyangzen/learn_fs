# sources/distributed-fs/ceph-client/io_uring/poll.h

Purpose: defines shared poll data structures and exported poll helper APIs for explicit poll requests and async retry.

Important APIs/types/functions: `IO_POLL_ALLOC_CACHE_MAX` sizes cached async poll objects. `IO_APOLL_OK`, `IO_APOLL_ABORTED`, and `IO_APOLL_READY` describe async-poll arm results. `struct io_poll` stores file, waitqueue head, event mask, retry budget, and wait entry. `struct async_poll` adds optional double poll. `io_poll_multishot_retry()` bumps `poll_refs` for owned multishot retries. Prototypes expose add/remove, cancel, arm, remove-all, and task-work execution.

Control flow: inline control is limited to `io_poll_multishot_retry()`, which assumes the caller owns the poll request and increments `req->poll_refs` so task-work will loop.

State and persistence: state is transient request waitqueue state and retry counters; no persistent storage.

Dependencies/integration: includes `io_uring_types.h` and is consumed by read/write, uring_cmd, task-work, cancel, and opcode dispatch paths.

Risks/test signals: callers must obey ownership assumptions for `io_poll_multishot_retry()` or corrupt poll reference accounting. Build coverage plus multishot read/command tests exercise this header contract.
