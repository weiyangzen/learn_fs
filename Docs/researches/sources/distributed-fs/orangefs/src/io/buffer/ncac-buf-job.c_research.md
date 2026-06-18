# sources/distributed-fs/orangefs/src/io/buffer/ncac-buf-job.c

## Purpose
Contains intended workers for NCAC operations where the caller supplies a user buffer and data is copied between cache extents and that buffer.

## Important APIs, Types, And Functions
Exports `NCAC_do_a_bufread_job` and `NCAC_do_a_bufwrite_job`.

## Control Flow
The meaningful read/write copy implementations are inside `#if 0`, so both functions currently return `0` without setting request status or copying data. Disabled code shows intended behavior: process one or multiple file regions, count ready cache buffers, transition to partial/complete, copy data to/from `usrbuf`, and call `NCAC_extent_done_access`.

## State And Persistence
With current compiled code, no state is changed. Intended state would involve `NCAC_req_t` buffer arrays, extent reference counts, and request status transitions.

## Dependencies And Integration Points
Included in `module.mk.in` and dispatched from `NCAC_do_a_job` for `NCAC_BUF_READ` and `NCAC_BUF_WRITE`. Depends on internal NCAC types and state helpers.

## Risks And Test Signals
The primary risk is that public `cache_read_post`/`cache_write_post` classify requests with non-NULL `desc->buffer` as buffered jobs, but these jobs are effectively stubs. Tests should explicitly cover supplied-buffer reads/writes and assert either implemented completion or a deliberate unsupported error; current behavior may leave requests submitted without progress.
