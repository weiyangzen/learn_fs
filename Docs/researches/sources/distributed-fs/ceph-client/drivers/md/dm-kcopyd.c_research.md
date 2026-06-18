# sources/distributed-fs/ceph-client/drivers/md/dm-kcopyd.c

### Purpose
`dm-kcopyd.c` provides the Device Mapper asynchronous copy/zero service used by targets that need to copy one block-device region to one or more destinations. It handles page buffering, job splitting, write ordering for zoned devices, throttling, and completion callbacks.

### Important APIs, Types, And Functions
Public APIs are `dm_kcopyd_init`, `dm_kcopyd_exit`, `dm_kcopyd_client_create`, `dm_kcopyd_client_destroy`, `dm_kcopyd_client_flush`, `dm_kcopyd_copy`, `dm_kcopyd_zero`, `dm_kcopyd_prepare_callback`, and `dm_kcopyd_do_callback`. `kcopyd_subjob_size_kb` is a module parameter bounded by `dm_get_kcopyd_subjob_size`.

Important structures are `struct dm_kcopyd_client`, which owns reserved pages, a `dm_io_client`, job mempool, workqueue, throttle, job count, waitqueue, and four job lists; and `struct kcopyd_job`, which stores source/destination regions, pages, operation, error state, callback, split-job progress, sequential write offset, and master-job linkage.

### Control Flow
Client creation initializes job lists, a job mempool sized for `MIN_JOBS`, a reclaim-safe per-CPU workqueue, reserved pages sized from the subjob limit, a dm-io client, and a destroy waitqueue. Copy submission allocates one master job plus `SPLIT_COUNT` subjobs from the slab mempool, records source/destinations and flags, auto-enables sequential writes for host-managed zoned destinations, disables ignore-error when sequential ordering is required, and either dispatches a single job or seeds split subjobs through `segment_complete`.

The worker `do_work` always processes completions first, then page allocation jobs, then I/O jobs. Page jobs allocate temporary pages or fall back to the reserved pool. I/O jobs call `dm_io` for reads or writes. `complete_io` converts read jobs into write jobs after successful reads, records read/write errors, and either continues or completes depending on `DM_KCOPYD_IGNORE_ERROR`. Split jobs use `segment_complete` to atomically claim the next source range and dispatch replacement subjobs until all work is complete. Zeroing calls `dm_kcopyd_copy` with no source and uses `REQ_OP_WRITE_ZEROES` when all destinations support it, otherwise writes from a shared zero page list.

### State And Persistence Behavior
There is no persistent state. Runtime state lives in each client: reserved/free pages, pending job lists, throttle accounting, outstanding job count, split progress, and callback queues. `dm_kcopyd_client_destroy` waits until `nr_jobs` reaches zero before asserting all job lists are empty and releasing resources.

### Dependencies And Integration Points
This file depends on `linux/dm-kcopyd.h`, `linux/dm-io.h`, block device zoned/write-zeroes helpers, mempools, workqueues, page allocation, mutexes, spinlocks, and Device Mapper core module-parameter helpers. It builds on `dm_io` for the actual block I/O and is typically consumed by higher-level DM targets such as mirrors, snapshots, or thin provisioning.

### Risks And Edge Cases
The most delicate behavior is split-job accounting: the master job is freed only after all subjobs finish, while callbacks are forced onto the kcopyd workqueue to avoid caller-visible completion concurrency. Reserved pages protect against deadlocks, but page pressure still stalls work by requeueing page jobs. Sequential write mode for zoned devices serializes writes through `write_offset`; ignoring errors is disabled because skipping a failed sequential write would corrupt ordering. Throttle accounting uses global spinlock-protected decaying jiffies counters and sleeps in bounded loops, so rate limiting is approximate.

### Test Signals
Tests should cover single and split copies, multi-destination writes, zeroing with and without hardware write-zeroes support, read and write error propagation, `DM_KCOPYD_IGNORE_ERROR`, zoned-device sequential write ordering, client destruction while work is outstanding, low-memory reserved-page fallback, throttled clients, prepared callbacks, and `dm_kcopyd_client_flush` draining work.
