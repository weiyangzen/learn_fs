# File Research: sources/block-storage/kvdo/vdo/index-session.c

Session-level API mediator for opening, closing, suspending, resuming, destroying, and issuing asynchronous requests against a UDS index.

Key responsibilities:
- Manages session state flags: loading, loaded, disabled, suspended, waiting, closing, destroying.
- Tracks in-flight asynchronous requests with `request_count` and drains them for suspend/close/destroy/flush.
- Creates the callback request queue and forwards completed index requests to user callbacks.
- Validates request types and callbacks in `uds_start_chunk_operation()`, resets internal request fields, obtains a session reference, and enqueues requests to the index.
- Converts internal UDS statuses to system errors at callback/API boundaries.
- Updates per-session statistics for posts, updates, deletes, queries, locations, and request totals.
- Opens indexes with `uds_open_index()`, including parameter name ownership and create/load/no-rebuild modes.
- Suspends and resumes sessions, including special coordination with an in-progress rebuild through `index_load_context`.
- Saves/free indexes on close and destroy.
- Returns parameter copies and statistics snapshots.

Important behavior:
- Any successful async request increments `request_count`; callback completion releases it.
- Any request callback status other than `UDS_SUCCESS` marks the session disabled. A disabled index rejects later requests until close/reopen.
- Suspend blocks new requests by setting `IS_FLAG_WAITING`, drains or saves depending on the `save` parameter, and then marks the session suspended.
- If suspend races with rebuild, it changes load context to `INDEX_SUSPENDING` and waits for rebuild code to publish `INDEX_SUSPENDED` or `INDEX_READY`.
- Resume can replace backing storage if a new name is supplied, then wakes a suspended rebuild by returning load context to `INDEX_OPENING`.
- Destroy handles the special case of a suspended load by setting `INDEX_FREEING` and waiting until loading exits.

Dependencies:
- Depends on `index.c` APIs, request queues, configuration building, logging, memory allocation, mutexes/condition variables, and time utilities.

Notable risks:
- `get_index_session()` increments `request_count` before checking state, then must release on non-loaded states; this is correct but fragile.
- Statistics use `READ_ONCE`/`WRITE_ONCE` increments rather than atomics; they are intended as approximate thread-safe counters.
- `uds_resume_index_session()` returns raw `result` on some no-work paths instead of always mapping through `uds_map_to_system_error()`.
- A single internal request error disables the whole session, which is conservative but broad.
