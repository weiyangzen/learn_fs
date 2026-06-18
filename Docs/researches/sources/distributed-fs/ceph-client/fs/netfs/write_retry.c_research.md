<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/write_retry.c -->
# sources/distributed-fs/ceph-client/fs/netfs/write_retry.c

## Purpose
Retries short or retry-requested write subrequests in each active stream, with support for renegotiating write sizes and splitting/merging retry spans.

## Important APIs, Types, And Functions
Defines `netfs_retry_writes()` and internal `netfs_retry_write_stream()`.

## Control Flow
`netfs_retry_writes()` sets `RETRYING`, waits for all active streams to quiesce, clears the flag, leaves TODO hooks for encrypted RMW handling, then retries streams marked `need_retry`. For a stream without `prepare_write`, it resets iterators and resubmits `NEED_RETRY` subrequests. With preparation, it finds contiguous retry spans, resets the source iterator, renegotiates `sreq_max_len/sreq_max_segs`, reuses existing subrequests when possible, discards extras if fewer are needed, or allocates inserted subrequests when more splits are required.

## State And Persistence
Mutates stream `need_retry`, subrequest `start`, `len`, `transferred`, `retry_count`, `NEED_RETRY`, `MADE_PROGRESS`, `BOUNDARY`, and iterators. Persistent write effects are retried through stream `issue_write()`.

## Dependencies And Integration Points
Called by `write_collect.c`. Depends on `netfs_wait_for_in_progress_stream()`, `netfs_reissue_write()`, `netfs_limit_iter()`, stream `prepare_write()`, netfs `retry_request()`, and request `wsize`.

## Risks
Retry span reconstruction must preserve coverage and boundaries while accounting for already-transferred bytes. Allocation failure for inserted subrequests is not explicitly handled in this file. Encryption TODOs indicate future complexity where server changes may require read-modify-write and cache rewrite.

## Test Signals
Short write retries, renegotiated smaller write sizes, no-prepare resubmission, boundary preservation, stream failure skip, dual-stream retry, and stress tests with concurrent collector wakeups.
