# sources/distributed-fs/orangefs/src/io/buffer/internal.c

## Purpose
Implements NCAC internal request construction, buffer-range preparation, progress-list movement, request completion/recycling, inode lookup/allocation, and debug dump helpers.

## Important APIs, Types, And Functions
Public internal functions are `NCAC_rwreq_build`, `NCAC_rwjob_prepare`, `NCAC_do_jobs`, `NCAC_do_a_job`, `NCAC_check_request`, `NCAC_done_request`, `cache_dump_active_list`, and `cache_dump_inactive_list`. Private helpers include request-list lock wrappers, `get_internal_req_lock`, `NCAC_rwjob_prepare_single`, `NCAC_rwjob_prepare_list`, `get_inode`, and inode hash search.

## Control Flow
`NCAC_rwreq_build` draws a preallocated request from `NCAC_dev.free_req_list`, binds it to an inode keyed by `(coll_id, handle)`, classifies it as cached or buffered read/write, and copies vector offsets for multi-region requests. `NCAC_rwjob_prepare` computes extent-aligned communication buffer arrays, queues the request on `prepare_list`, and immediately advances that request via `NCAC_do_a_job`. Single-region and list-region preparation calculate file offsets, cache-buffer offsets, sizes, flags, and extent slots, sorting multi-region input by file position. `NCAC_do_a_job` dispatches by optype to job workers and moves requests from prepare to buffer-complete or complete lists. `NCAC_check_request` progresses unfinished requests on demand. `NCAC_done_request` handles post-communication cleanup and returns request objects to the free list.

## State And Persistence
State is global NCAC memory: preallocated request objects, prepare/buffer-complete/complete/free lists, inode collision chains, cached per-request buffer arrays, and inode page trees. No disk persistence exists. Requests may keep allocated buffer-info arrays across reuse to reduce allocations. Inodes are allocated lazily and never freed in this file.

## Dependencies And Integration Points
Depends on `internal.h`, `state.h`, `flags.h`, `aiovec.h`, `cache.h`, and `ncac-job.h`. It is called by `ncac-interface.c` and drives `ncac-job.c`/`ncac-buf-job.c` workers.

## Risks And Test Signals
Risks include `get_internal_req_lock` returning without unlocking when the free list is empty, pointer recovery through `list_entry(new->prev, ...)` after `list_del_init`, hardcoded debug `fprintf` output, possible zero-size last buffer when a request ends exactly on an extent boundary, request leaks on invalid done status, no inode-table lock, and limited implemented worker types. Tests should stress empty request pools, multi-region sorting and overlapping extents, request status transitions, completion recycling, and concurrent access to the same handle.
