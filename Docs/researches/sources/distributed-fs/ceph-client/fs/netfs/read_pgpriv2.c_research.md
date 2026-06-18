<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/read_pgpriv2.c -->
# sources/distributed-fs/ceph-client/fs/netfs/read_pgpriv2.c

## Purpose
Implements deprecated `PG_private_2` based copy-to-cache after reads. When read data was fetched from the server and should be cached, this file builds a separate write request to copy read folios into the local cache and clears `PG_private_2` as cache writes complete.

## Important APIs, Types, And Functions
Defines `netfs_pgpriv2_copy_to_cache()`, `netfs_pgpriv2_end_copy_to_cache()`, and `netfs_pgpriv2_unlock_copied_folios()`. Internal helpers are `netfs_pgpriv2_copy_folio()` and `netfs_pgpriv2_begin_copy_to_cache()`.

## Control Flow
The first folio needing copy-to-cache creates a `NETFS_PGPRIV2_COPY_TO_CACHE` write request if cache resources are valid and cache stream 1 is available. Each folio is marked private_2, appended to the rolling buffer, split into cache write subrequests by `netfs_advance_write()`, and issued as needed. At end of the parent read, outstanding cache writes are issued, `ALL_QUEUED` is set, the collector is poked if empty, and the copy request ref is dropped. The write collector calls `netfs_pgpriv2_unlock_copied_folios()` to end private_2 on completed folios.

## State And Persistence
State includes `rreq->copy_to_cache`, `NETFS_RREQ_FOLIO_COPY_TO_CACHE`, copy request buffer/streams, folio private_2 marks, and cache write subrequests. Persistent effect is backend cache writes.

## Dependencies And Integration Points
Used only from read collection and write collection. Depends on FS-Cache resources, write issue functions, rolling buffer, folio private_2 APIs, and netfs write collector behavior.

## Risks
The file is marked deprecated. Risks include private_2 waits blocking reclaim/invalidation, copy request setup failure silently disabling cache copy, EOF races with changing i_size, and ensuring all marked folios are unmarked even on cache write failure.

## Test Signals
Read-through-cache miss followed by copy-to-cache, cache unavailable during copy setup, partial final folio near EOF, cache write failure, and invalidation/release waiting for private_2 clearance.
