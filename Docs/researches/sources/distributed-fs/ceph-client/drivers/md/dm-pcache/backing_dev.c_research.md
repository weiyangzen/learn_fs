
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/backing_dev.c

## Purpose
Implements asynchronous I/O submission and completion handling for pcache's backing block device. It creates cloned requests from upper bios or kmem-backed bios for cache writeback/read-miss operations, submits them to the lower device, and completes pcache request accounting.

## Important APIs, Types, And Functions
Global slab caches are `backing_req_cache` and `backing_bvec_cache`. `backing_dev_start()` initializes request/bvec mempools, submit/complete lists, work items, inflight counters, and backing device size. `backing_dev_stop()` waits for inflight requests and flushes work. `backing_dev_req_alloc()`, `backing_dev_req_init()`, and `backing_dev_req_create()` build either `BACKING_DEV_REQ_TYPE_REQ` cloned-bio requests or `BACKING_DEV_REQ_TYPE_KMEM` mapped-memory bios. `backing_dev_req_submit()` queues or directly submits bios. `backing_dev_bio_end()` records errno and queues completion. `backing_dev_req_end()` invokes callbacks, releases upper requests or bvecs, frees the request, and wakes shutdown waiters. `backing_dev_flush()` issues a lower flush.

## Control Flow
Requests are allocated from mempools and increment `inflight_reqs`. Non-direct submissions are added to `submit_list` and drained by `req_submit_fn()` on the pcache workqueue. Bio completion moves the request to `complete_list` and queues `req_complete_fn()`, which calls final callbacks and releases references. Type-specific initialization trims cloned upper bios or maps kernel memory/vmalloc/DAX-backed memory into bio vectors.

## State And Persistence
All state is runtime queueing and request accounting. There is no metadata persistence here. Data persistence is achieved through lower-device bios and explicit flushes invoked by higher layers.

## Dependencies And Integration Points
Depends on block bio APIs, dm device references initialized by `dm_pcache`, pcache request refcounting, mempools/slab caches, workqueues, vmalloc page translation, DAX/vmap range flushing, and cache/backing ownership macros.

## Risks
Mapped kmem/vmalloc ranges must be represented by valid pages and bio vector counts. Inflight accounting must balance on every allocation/free path or shutdown can hang. Direct submission bypasses the submit workqueue but still completes asynchronously. The use of `BUG_ON` in bio mapping and type dispatch turns unexpected inputs into kernel crashes. Request trimming requires sector-aligned offsets and lengths.

## Test Signals
Test req and kmem request types, inline and pooled bvec paths, vmalloc and direct-mapped memory, direct versus queued submit, completion callback errors, upper request refcount balancing, shutdown waiting with inflight I/O, lower flush, allocation failure paths, and sector alignment assertions.
