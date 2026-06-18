<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/read_retry.c -->
# sources/distributed-fs/ceph-client/fs/netfs/read_retry.c

## Purpose
Retries failed or short read subrequests, especially converting failed cache reads into server downloads and renegotiating request sizes when a filesystem provides `prepare_read()` or `retry_request()`.

## Important APIs, Types, And Functions
Defines `netfs_retry_reads()` and `netfs_unlock_abandoned_read_pages()`. Internal functions are `netfs_reissue_read()` and `netfs_retry_read_subrequests()`.

## Control Flow
`netfs_retry_reads()` sets `RETRYING`, waits for all in-progress subrequests in stream 0 to quiesce, clears `RETRYING`, and rebuilds retryable subrequests. Simple mode resubmits each `NEED_RETRY` subrequest in place. Renegotiation mode decants contiguous retry spans, resets iterators, converts source to `NETFS_DOWNLOAD_FROM_SERVER`, calls `prepare_read()`, truncates iterators to negotiated lengths/segment limits, reissues, discards superfluous subrequests, or allocates extra subrequests when the retried span splits smaller than before. Abandon paths mark remaining retry/failed subrequests failed with `-ENOMEM`.

## State And Persistence
Mutates subrequest `source`, `start`, `len`, `transferred`, `retry_count`, flags, iterators, and stream `sreq_max_len/sreq_max_segs`. It does not persist data but determines whether final read data comes from cache or server.

## Dependencies And Integration Points
Called by `read_collect.c` when the front subrequest requests retry. Uses netfs ops `retry_request()`, `prepare_read()`, `issue_read()`, iterator limiting, and request waitqueues.

## Risks
Retry reconstruction can corrupt coverage if boundaries, donations, transferred offsets, or iterator counts are mishandled. Allocating extra subrequests can fail after partial rebuild. Cache failure fallback must avoid retry loops with no progress.

## Test Signals
Cache read failure fallback to download, partial read with progress, retry needing smaller `rsize`, boundary-preserving split, extra-subrequest allocation failure, and abandoned page unlock after unrecoverable failure.
