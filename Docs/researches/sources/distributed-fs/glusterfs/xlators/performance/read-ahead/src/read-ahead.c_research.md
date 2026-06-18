# sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead.c

## Purpose
Implements the `performance/read-ahead` xlator. It detects sequential read patterns, serves reads from a per-fd page cache, speculatively issues child `readv` operations, invalidates cached pages on file mutations, supports statedump, and exposes volume options for page sizing, page count, atime behavior, and pass-through.

## Important APIs, Types, And Functions
Public fops are `ra_open`, `ra_create`, `ra_readv`, `ra_writev`, `ra_flush`, `ra_fsync`, `ra_truncate`, `ra_ftruncate`, `ra_fstat`, `ra_discard`, and `ra_zerofill`. `ra_open_cbk()` and `ra_create_cbk()` allocate `ra_file_t` fd contexts, disabling caching for `O_DIRECT` and write-only opens. `dispatch_requests()` handles user read cache hits, misses, and waits. `read_ahead()` schedules speculative dirty page faults. `flush_region()` invalidates ready pages or marks pending pages stale/poisoned. Init/reconfigure/fini manage `ra_conf_t`, local frame pools, and options.

## Control Flow
Open/create attaches a read-ahead file context to the fd and links it into the translator config. `ra_readv()` bypasses disabled fds, compares the request offset against the expected sequential offset, resets prefetch depth on random reads, allocates `ra_local_t`, dispatches required pages, flushes old pages before the current offset, schedules future read-ahead pages, updates the next expected offset, and returns when all page waiters complete. Mutating fops walk all fds on the inode and invalidate cached pages before winding the child operation. `fstat` invalidates cached pages when `force-atime-update` is enabled.

## State And Persistence
`ra_conf_t` stores configured page size/count, atime behavior, the global list of open file contexts, and a config lock. Each `ra_file_t` tracks expected sequential offset, dynamic prefetch page count, cached pages, last stat buffer, fd pointer, disabled flag, and lock. State lives only in memory and is discarded on fd release or translator fini.

## Dependencies And Integration Points
Uses the Gluster xlator API, fd/inode contexts, frame-local memory pools, statedump hooks, child `readv`/mutation fops, iovec and iobref helpers, option parsing macros, and the page helpers in `page.c`. It integrates with other performance translators by respecting `pass-through` and by optionally forcing atime updates through a tiny child read.

## Risks
The implementation intentionally flushes broad ranges, often the whole cached fd, which is safe but can reduce benefit. Sequential-detection state is updated without a dedicated lock in `ra_readv`, so concurrent reads on the same fd can disrupt prefetch heuristics. `ra_create_cbk()` does not reduce page count to one for non-disabled created files while `ra_open_cbk()` does; that asymmetry may affect initial prefetch behavior. The atime workaround performs an extra child read that can interact poorly with other cache translators. Mutation invalidation must cover every fop that can change file data.

## Test Signals
Exercise sequential, random, and concurrent reads; O_DIRECT and write-only opens; writes/truncates/discard/zerofill racing with cached and in-flight pages; `force-atime-update`; option reconfigure for page size/count and pass-through; fd release/fini with cached pages; and statedump output. Performance signals should show fewer child reads for sequential reads and no stale data after mutations.
