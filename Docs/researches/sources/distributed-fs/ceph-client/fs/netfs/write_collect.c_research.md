<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/write_collect.c -->
# sources/distributed-fs/ceph-client/fs/netfs/write_collect.c

## Purpose
Collects write subrequest completions across server-upload and cache-write streams, unlocks completed folios, retries short writes, records mapping errors, invalidates cache on cache-write failure, and completes iocbs.

## Important APIs, Types, And Functions
Exports `netfs_write_subrequest_terminated()`. Defines `netfs_folio_written_back()`, `netfs_write_collection()`, `netfs_write_collection_worker()`, `netfs_collect_write_results()`, and `netfs_writeback_unlock_folios()`.

## Control Flow
The collector scans each active stream front-to-back, stopping at in-progress subrequests. It advances each stream's collected/transferred point, records permanent failure, flags short writes for retry, removes consumed subrequests, and computes request `collected_to` as the minimum collected point across active streams. For writeback-like origins, folios are completed only up to that common point. If retry is needed, `netfs_retry_writes()` quiesces and rebuilds streams. Final completion waits for `ALL_QUEUED` and empty active streams, sets transferred bytes, invalidates cache on cache-stream failure if the netfs provides `invalidate_cache()`, clears `IN_PROGRESS`, completes iocbs, and clears subrequests.

## State And Persistence
Updates folio private/group/writeback state, request `collected_to`, `cleaned_to`, `transferred`, stream failure/error/transferred state, mapping writeback error, request flags, and group release counts. Persistent server/cache writes were already issued by stream providers; this file decides completion semantics.

## Dependencies And Integration Points
Used by writeback, writethrough, single-object writeback, pgpriv2 copy-to-cache, and cache/backend write callbacks. Integrates with retry code, folio queues, mapping error state, iocb completion, and netfs group refs.

## Risks
The two-stream minimum-collection rule is subtle. Completing folios before both active streams cover them can lose dirty data or cache writes. Cache failure is tolerated differently from server failure, so disconnected-mode behavior depends on netfs `invalidate_cache()` and policy outside this file.

## Test Signals
Test server-only, cache-only, dual-stream writeback, cache-stream failure, server failure mapping error, partial write retry, writethrough iocb completion, group release, and pgpriv2 copy-to-cache folio unmarking.
