# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-session.c

## Purpose
Implements the public UDS session lifecycle and request admission layer. A session owns at most one open index, tracks state flags, drains in-flight requests for suspend/close/save, queues callbacks, and converts internal UDS status codes to errno values for callers.

## Important APIs, Types, And Functions
Public functions are `uds_create_index_session()`, `uds_destroy_index_session()`, `uds_open_index()`, `uds_close_index()`, `uds_suspend_index_session()`, `uds_resume_index_session()`, `uds_flush_index_session()`, `uds_get_index_session_stats()`, `uds_launch_request()`, and `uds_wait_cond()`. Internal state flags include loading, loaded, disabled, suspended, waiting, closing, and destroying. `index_load_context` coordinates pausable rebuilds with statuses `INDEX_OPENING`, `INDEX_READY`, `INDEX_SUSPENDING`, `INDEX_SUSPENDED`, and `INDEX_FREEING`.

## Control Flow
Opening validates parameters, marks the session loading, copies parameters, creates a configuration, and calls `uds_make_index()`. Requests validate callback and request type, reset internal request fields, acquire a request reference only if the session is exactly loaded, and enqueue into the index. Index completion enters `enter_callback_stage()`, which disables the session on any request error, then sends the request to the callback queue. Callback processing updates stats, converts status, invokes the client callback, and releases the request reference.

Suspend waits for competing state changes, either pauses a rebuild through `load_context` or drains active requests and optionally saves the index, then marks the session suspended. Resume can replace the block device and resume paused replay. Close and destroy drain requests, save/free the index when appropriate, and finish queues.

## State And Persistence
Session state is protected by `request_mutex`; `request_count` tracks asynchronous requests and state transitions waiting for callbacks. Statistics are updated with `READ_ONCE`/`WRITE_ONCE` style counters. Persistence occurs indirectly through `uds_save_index()` during suspend, close, or destroy unless the index is already suspended.

## Dependencies And Integration Points
Integrates with `index.c` through `uds_make_index()`, `uds_save_index()`, `uds_free_index()`, `uds_enqueue_request()`, and `uds_wait_for_idle_index()`. It depends on request queues for callback serialization, configuration creation, logging, allocation, and kernel wait queues.

## Risks
Any request error permanently disables the open index until close, so errors from lower layers have broad operational impact. State flag combinations are subtle during loading plus suspended rebuild; missed broadcasts can hang suspend/resume/destroy. `get_index_session()` increments `request_count` before state validation and must release it on every rejection path. `uds_wait_cond()` uses `TASK_IDLE`, so all callers must hold the paired mutex and recheck conditions.

## Test Signals
Tests should cover request validation, callback completion, disable-on-error, suspend with and without save, suspend/resume during rebuild, storage replacement on resume, close while busy, destroy during suspended load, stats aggregation, and rejection of launches while suspended/loading/disabled/no-index.
