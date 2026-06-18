# sources/distributed-fs/orangefs/src/io/buffer/ncac-interface.c

## Purpose
Provides the public NCAC cache request API used by higher layers to post read/write/sync operations, poll request progress, and mark completed buffer communication.

## Important APIs, Types, And Functions
Exports `cache_read_post`, `cache_write_post`, `cache_sync_post`, `cache_req_test`, `cache_req_testsome`, and `cache_req_done`.

## Control Flow
Read/write post functions build an internal request, prepare and submit it, store the internal id/optype/status into the public request handle, and return buffer arrays in `cache_reply_t` when partial or buffer-complete progress is available. `cache_req_test` calls `NCAC_check_request`, updates public status, exposes buffers for partial/buffer-complete state, and sets a completion flag for buffer-complete or complete. `cache_req_done` calls `NCAC_done_request` and marks the public handle complete. Sync and testsome print "not implemented yet" and return zero.

## State And Persistence
State lives in NCAC internal request objects and public handles. `user_ptr` parameters are currently unused. Replies reference internal request arrays, so the caller must finish communication before `cache_req_done` recycles the request.

## Dependencies And Integration Points
Depends on `ncac-interface.h` for public structures and `internal.h` for request engine calls. Higher network or server I/O code should interact through these functions instead of direct internal structures.

## Risks And Test Signals
Risks include sync/testsome stubs, no descriptor validation, supplied-buffer paths dispatching to stubbed workers, reply pointers becoming invalid after done, and mismatch between comments and actual status names. Tests should cover post/test/done for cache-buffer reads, missing free requests, supplied-buffer reads/writes, polling before/after Trove completion, and unsupported sync/testsome behavior.
