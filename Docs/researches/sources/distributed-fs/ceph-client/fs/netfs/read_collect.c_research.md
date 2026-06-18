<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/read_collect.c -->
# sources/distributed-fs/ceph-client/fs/netfs/read_collect.c

## Purpose
Collects read subrequest completions, unlocks/marks folios, handles cache copy-to-cache decisions, detects short/error/retry conditions, finalizes direct/single reads, and exposes termination/progress callbacks for filesystem and cache IO providers.

## Important APIs, Types, And Functions
Exports `netfs_read_subreq_progress()` and `netfs_read_subreq_terminated()`. Defines `netfs_read_collection()`, `netfs_read_collection_worker()`, `netfs_cache_read_terminated()`, `netfs_collect_read_results()`, `netfs_read_unlock_folios()`, `netfs_rreq_assess_dio()`, and `netfs_rreq_assess_single()`.

## Control Flow
The collector walks the front of read stream 0. It advances `stream->collected_to` from completed subrequests, clears unread tails for EOF/clear-tail short reads, marks cache-copy folios, abandons failed ranges, and removes consumed subrequests. Pending front subrequests stall collection. Retry requests set `NEED_RETRY`, pause the issuer, and call `netfs_retry_reads()`. Completion requires `ALL_QUEUED` and an empty stream; then transferred count is set, DIO/single-read completion callbacks run, IO accounting is updated, `IN_PROGRESS` is cleared/woken, abandoned pages are unlocked, and deprecated pgpriv2 copy-to-cache is ended.

## State And Persistence
Updates request `collected_to`, `cleaned_to`, `transferred`, `error`, `abandon_to`, stream `transferred`, folio uptodate/private/dirty/locked state, subrequest flags, and request flags such as `PAUSE`, `FAILED`, `SHORT_TRANSFER`, and `FOLIO_COPY_TO_CACHE`.

## Dependencies And Integration Points
Consumes subrequests issued by buffered/direct/single read paths and cache reads. Integrates with retry code, pgpriv2 copy-to-cache, folio queues, task IO accounting, iocb completion, and netfs `done()` callbacks.

## Risks
Ordering around `IN_PROGRESS` and transferred counters is critical. Folio unlock decisions must match collected ranges or pages can remain locked or become uptodate with holes. Cache read errors must retry from server without reporting false user errors unless server download fails.

## Test Signals
Test cache hit, cache miss fallback, short reads with EOF, clear-tail, retry after partial progress, server failure, abandoned ranges, direct IO completion, single-object cache-dirty marking, and copy-to-cache folio tagging.
