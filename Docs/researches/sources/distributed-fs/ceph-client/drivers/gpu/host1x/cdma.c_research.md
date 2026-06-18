<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/cdma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/cdma.c

## Purpose

`cdma.c` implements the generic command-DMA queue for each host1x channel. It owns the circular pushbuffer, synchronizes producer submissions with hardware consumption, tracks submitted jobs in `sync_queue`, unpins buffers after syncpoint completion, and coordinates timeout recovery.

## Important APIs, Types, And Functions

- Pushbuffer helpers allocate WC memory, optionally map it through the host IOMMU, initialize the hardware restart word, and manage `pos`/`fence` circular slots.
- `host1x_cdma_init()` / `host1x_cdma_deinit()` initialize locks, completions, workqueue state, queue heads, pushbuffer storage, and timeout resources.
- `host1x_cdma_begin()`, `host1x_cdma_push()`, `host1x_cdma_push_wide()`, and `host1x_cdma_end()` are the submission sequence used by `channel_hw.c`.
- `host1x_cdma_wait_locked()` and `host1x_cdma_wait_pushbuffer_space()` sleep on either pushbuffer space or an empty sync queue while preserving the CDMA mutex contract.
- `update_cdma_locked()` consumes completed jobs, unpins their buffers, pops pushbuffer slots, drops job references, and wakes waiters.
- `host1x_cdma_update_sync_queue()` is the timeout recovery path that resumes at the next job or CPU-increments/cancels the failed syncpoint depending on `job->syncpt_recovery`.

## Control Flow

Submission enters with `host1x_cdma_begin()`, which holds `cdma->lock`, rejects locked syncpoints, initializes timeout work if needed, starts CDMA hardware if idle, and records the first GET offset. Callers then emit two-word or four-word opcodes into the circular pushbuffer. Wide pushes avoid splitting a four-word opcode pair across the restart word by inserting a restart/pad slot if needed. `host1x_cdma_end()` flushes the hardware PUT pointer, stores `first_get` and `num_slots` in the job, appends the job to `sync_queue`, starts the timeout timer on idle-to-active transitions, and unlocks.

Completion is asynchronous. Fence callbacks, timeout paths, and explicit updates schedule `cdma_update_work`, which calls `update_cdma_locked()`. That function walks the queue from the head until the first unfinished, non-cancelled job, then starts a timeout for that pending head. Finished jobs are unpinned and released in order because pushbuffer slots are also retired in FIFO order.

## State And Persistence Behavior

Persistent per-channel state includes the WC pushbuffer mapping, DMA/IOVA addresses, circular cursor fields, `sync_queue`, timeout metadata, `running`/`torndown`, and the current wait event. Job references persist while queued. Hardware state persists through channel DMA registers programmed by `cdma_hw.c`. IOMMU mappings for pushbuffer memory persist for the CDMA lifetime; gather/reloc mappings persist only until job unpin.

## Dependencies And Integration Points

This file depends on host1x hardware ops from `dev.h`, job pin/unpin, syncpoint expiration, tracepoints, Linux completions/workqueues, DMA/IOMMU APIs, and the channel container. It is driven primarily by `channel_hw.c` submission and by fence interrupts from `intr.c`/`fence.c`.

## Risks And Edge Cases

The pushbuffer full/empty convention is inverted from the sync queue, so cursor regressions can deadlock submitters. Wide opcode padding is required for HW6+ gather and stream-ID programming. Timeout recovery mutates queued commands for cancellation and relies on memory barriers before resuming hardware. CPU syncpoint recovery must only be used for jobs marked safe. `host1x_cdma_deinit()` refuses to destroy a running CDMA, so release paths need to stop channels first.

## Test Signals

Good signals include repeated submit/complete under high queue depth, pushbuffer wraparound, wide gather at the tail boundary, IOMMU and non-IOMMU pushbuffer allocation, timeout with recovery and without recovery, locked syncpoint rejection, module remove after idle, and trace output when `trace_cmdbuf` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/cdma.c -->
