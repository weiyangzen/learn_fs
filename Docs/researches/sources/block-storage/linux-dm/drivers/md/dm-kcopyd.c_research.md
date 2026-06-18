# File Research: sources/block-storage/linux-dm/drivers/md/dm-kcopyd.c

## Purpose
Implements DM kcopyd, an asynchronous block copy/zero service used by DM targets to copy one source region to one or more destination regions, split large jobs, throttle copy I/O, and report completion through callbacks.

## Main Interfaces
- Global setup: `dm_kcopyd_init()`, `dm_kcopyd_exit()`.
- Client lifecycle: `dm_kcopyd_client_create()`, `dm_kcopyd_client_destroy()`, `dm_kcopyd_client_flush()`.
- Work submission: `dm_kcopyd_copy()`, `dm_kcopyd_zero()`.
- Callback-only helpers: `dm_kcopyd_prepare_callback()`, `dm_kcopyd_do_callback()`.

## Control Flow
A client owns reserved pages, a `dm_io_client`, a job mempool, a workqueue, and four job lists. `dm_kcopyd_copy()` allocates one master job plus split-job storage, configures source/destinations, decides whether sequential writes are required for host-managed zoned destinations, and dispatches either one job or multiple sub-jobs.

Copy jobs first acquire pages, then issue a read from the source, then write the pages to all destinations. Zero jobs use `WRITE_ZEROES` when all destinations support it, otherwise write from a reusable zero page list. Completion moves jobs through callback/complete queues so final callbacks run from kcopyd’s workqueue context.

## State And Synchronization
`struct dm_kcopyd_client` contains page accounting, a job spinlock, callback/complete/io/pages lists, throttle pointer, workqueue, destroy waitqueue, and active-job counter. Split jobs share a master job mutex, progress counter, write offset, and aggregate error state. Throttle accounting is protected by a global spinlock.

## Integration Points
Uses `dm_io()` for block I/O, DM module parameters for sub-job sizing, block zoned-device model checks, block write-zeroes support checks, mempools for no-I/O allocation safety, and workqueues for serialized callback execution.

## Notable Behaviors
- Default sub-job size is 512 KiB, capped at 1024 KiB by module parameter handling.
- Large jobs are split into `SPLIT_COUNT` concurrent sub-jobs.
- Host-managed zoned destinations force sequential writes and disable ignore-error behavior.
- Throttling tracks approximate busy versus total periods and sleeps in 100 ms increments, bounded by `MAX_SLEEPS`.
- Client destruction waits for all submitted jobs before freeing resources.

## Risks And Review Focus
- Split-job lifetime depends on the mempool object containing the master plus sub-job array.
- Sequential write ordering relies on `write_offset` and `pop_io_job()` choosing only the next eligible write.
- Ignored errors and normal errors take different completion paths; callers must understand read versus per-destination write error reporting.
- Throttle accounting is global-lock based and approximate, so changes can affect copy-rate behavior across clients.
