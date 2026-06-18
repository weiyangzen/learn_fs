
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/backing_dev.h

## Purpose
Declares pcache backing-device request structures and APIs. It is the contract between cache request handling/writeback code and the lower block-device I/O layer implemented in `backing_dev.c`.

## Important APIs, Types, And Functions
`struct pcache_backing_dev_req` embeds a `bio`, request type, backing-device pointer, callback/private data, list node, result, and either upper-request clone metadata or kmem bvec metadata. `struct pcache_backing_dev` stores dm device, mempools, submit/complete queues, work items, inflight counters, waitqueue, and device size. `struct pcache_backing_dev_req_opts` describes request allocation/init options for upper-request or kmem I/O. APIs include `backing_dev_start()`, `backing_dev_stop()`, `backing_dev_req_submit()`, `backing_dev_req_end()`, allocation/init/create helpers, `backing_dev_flush()`, and module-level slab init/exit. `backing_dev_req_coalesced_max_len()` limits vmalloc/DAX-page coalescing to a single pgmap run.

## Control Flow
Callers allocate and initialize requests from options, submit directly or via queueing, and receive callback completion with an errno-style result. Shutdown uses inflight accounting exposed through `pcache_backing_dev`.

## State And Persistence
Defines runtime request and queue state only. No on-media metadata is represented.

## Dependencies And Integration Points
Includes device-mapper and pcache internal definitions. It integrates cache miss/read/writeback logic with block-device submission while hiding bio construction details.

## Risks
The embedded bio and union require callers to select the correct type and option fields. `backing_dev_req_coalesced_max_len()` is important for vmalloc mappings across device-private page maps; ignoring it could create invalid bios. Callback ownership of `priv_data` must be precise to avoid leaks or double puts.

## Test Signals
Compile all users of both request types, stress vmalloc coalescing boundaries, verify callback/private-data lifetime, and validate inflight accounting across allocation failures and completions.
